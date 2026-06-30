"""Generate Module 5 — Multi-Agent Orchestration (stable core WorkflowBuilder)."""

from _nbbuild import code, md, write_notebook

PREAMBLE = """\
import sys, pathlib, warnings
sys.path.insert(0, str(pathlib.Path.cwd().parents[1]))
warnings.filterwarnings("ignore", category=DeprecationWarning)
from workshop_utils import get_chat_client
from agent_framework import Agent"""

cells = [
    md(
        """\
# M5 · Multi-Agent Orchestration

> **Goal:** coordinate **several** specialized agents — and learn when that beats
> one big agent.
>
> **You'll use:** the core `WorkflowBuilder` with **agents as nodes** (sequential
> and fan-out), plus low-level **executors + edges**.

---

One agent with twenty tools becomes confused and hard to debug. Splitting work
across **specialists** that each do one thing well is often clearer, cheaper, and
more reliable.

![Orchestration patterns](../../assets/orchestration-patterns.png)

| Pattern | Shape | Good for |
|:--|:--|:--|
| **Sequential** | A → B → C | pipelines, multi-stage processing |
| **Concurrent / fan-out** | A, B, C in parallel → merge | independent sub-tasks then aggregate |
| **Handoff** | control passes to a specialist | triage, escalation |
| **Group chat** | agents converse under a manager | debate, collaboration |
| **Magentic** | a manager plans & delegates dynamically | open-ended tasks |

In Agent Framework, **an agent is itself an executor** — so you compose agents
into a **typed workflow graph** with the same `WorkflowBuilder` you'd use for
plain functions. (Higher-level helpers like `SequentialBuilder` exist in the
separate `agent-framework-orchestrations` package; this workshop stays on the
**stable core** so everything installs cleanly.)"""
    ),
    md("## 1. Setup"),
    code(PREAMBLE),
    md(
        """\
## 2. Sequential: a writer → reviewer pipeline

Wire two agents into a chain: the **writer** drafts, then the **reviewer**
critiques. Each agent is a node; `add_edge(writer, reviewer)` connects them.
`output_from="all"` returns every node's contribution."""
    ),
    code(
        '''\
from agent_framework import WorkflowBuilder, AgentResponse
from typing import cast

client = get_chat_client()

writer = Agent(
    client=client,
    name="writer",
    instructions="You are a concise copywriter. Write a single punchy marketing sentence for the prompt.",
)
reviewer = Agent(
    client=client,
    name="reviewer",
    instructions="You are a thoughtful reviewer. Give brief, actionable feedback on the previous message.",
)

# An agent IS an executor, so it can be a node in the graph.
# `output_from="all"` is a WorkflowBuilder constructor argument; build() takes no args.
workflow = (
    WorkflowBuilder(start_executor=writer, output_from="all")  # collect output from every node
    .add_edge(writer, reviewer)
    .build()
)

events = await workflow.run("Write a tagline for a budget-friendly eBike.")
for output in cast(list[AgentResponse], events.get_outputs()):
    print(f"{'-'*60}\\n[{output.messages[0].author_name}]\\n{output.text}")
print("\\nFinal state:", events.get_final_state())'''
    ),
    md(
        """\
!!! note "The message flows along the edge"
    The writer's output becomes the reviewer's input automatically — that's what
    the edge means. No glue code; the graph moves data between agents."""
    ),
    md(
        """\
## 3. Fan-out: one prompt, several specialists

When sub-tasks are **independent**, connect the start node to several specialists.
Here a single idea is sent to three reviewers at once — an *optimist*, a *skeptic*,
and a *risk analyst* — and we collect all their takes."""
    ),
    code(
        '''\
intake = Agent(
    client=client,
    name="intake",
    instructions="Restate the user's idea in one neutral sentence so reviewers can react to it.",
)
optimist = Agent(client=client, name="optimist",
                 instructions="Give two upbeat PROS of the idea. Be brief.")
skeptic = Agent(client=client, name="skeptic",
                instructions="Give two honest CONS of the idea. Be brief.")
risk = Agent(client=client, name="risk_analyst",
             instructions="Name one key RISK to watch. One sentence.")

panel = (
    WorkflowBuilder(start_executor=intake, output_from="all")
    .add_edge(intake, optimist)
    .add_edge(intake, skeptic)
    .add_edge(intake, risk)
    .build()
)

events = await panel.run("Idea: a subscription service for refillable cleaning products.")
for output in cast(list[AgentResponse], events.get_outputs()):
    print(f"{'-'*60}\\n[{output.messages[0].author_name}]\\n{output.text}")'''
    ),
    md(
        """\
!!! tip "Fan-out → fan-in"
    To *merge* the specialists' outputs, add a final **aggregator** node that all
    three feed into (e.g. an `editor` agent that synthesizes a recommendation).
    That's the fan-out/fan-in shape — see upstream `03-workflows/parallelism/`."""
    ),
    md(
        """\
## 4. Low-level workflows: executors + edges

Agents-as-nodes are a convenience over Agent Framework's **typed workflow graph**.
When you need explicit, recoverable control flow, define your own **executors**
(nodes) and connect them with **edges**. This tiny graph has *no model calls* — it
just shows the mechanics: uppercase → reverse."""
    ),
    code(
        '''\
from agent_framework import Executor, WorkflowContext, executor, handler
from typing_extensions import Never

class UpperCase(Executor):
    def __init__(self, id: str):
        super().__init__(id=id)

    @handler
    async def to_upper(self, text: str, ctx: WorkflowContext[str]) -> None:
        await ctx.send_message(text.upper())          # forward to the next node

@executor(id="reverse")
async def reverse_text(text: str, ctx: WorkflowContext[Never, str]) -> None:
    await ctx.yield_output(text[::-1])                # terminal node yields output

upper = UpperCase(id="upper")
graph = WorkflowBuilder(start_executor=upper, output_from="all").add_edge(upper, reverse_text).build()

events = await graph.run("hello world")
print("output:", events.get_outputs())
print("state: ", events.get_final_state())'''
    ),
    md(
        """\
!!! tip "Why typed graphs matter"
    Edges are **type-checked**: a node emitting `str` only connects to a node
    accepting `str`. Add conditional edges, loops, fan-in, and **checkpointing**
    (pause/resume) and you get durable, debuggable orchestration — the foundation
    for human-in-the-loop and long-running workflows
    (`03-workflows/checkpoint/`, `human-in-the-loop/`)."""
    ),
    md(
        """\
## 5. Choosing a pattern

```
Fixed pipeline?                          → chain agents with add_edge (sequential)
Independent sub-tasks to merge?          → fan-out edges + an aggregator node
Route to the right specialist?           → Handoff (agent-framework-orchestrations)
Need agents to debate/collaborate?       → Group chat / Magentic (orchestrations)
Need explicit, recoverable control flow? → custom executors + edges
```

Start with the simplest shape that fits. The high-level `SequentialBuilder`,
`HandoffBuilder`, `GroupChatBuilder`, and `MagenticBuilder` (in
`agent-framework-orchestrations`) are worth exploring once you're comfortable."""
    ),
    md(
        """\
## 🧪 Your turn

1. Add an `editor` agent as a **fan-in** node: connect optimist, skeptic, and risk
   into it so it synthesizes one recommendation.
2. Turn the writer→reviewer pipeline into writer→reviewer→**writer** (a revision
   loop) and see the second draft.
3. Extend the low-level graph with a middle node that appends `"!!!"` between
   upper and reverse (see upstream `step1_executors_and_edges.py`).

---

✅ **You can coordinate many agents.** Now measure whether they're any good.
→ **[M6 · Evaluating & Optimizing](06-evaluation.ipynb)**"""
    ),
]

write_notebook("docs/modules/05-orchestration.ipynb", cells)
