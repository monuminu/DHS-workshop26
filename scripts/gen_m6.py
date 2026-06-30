"""Generate Module 6 — Evaluating & Optimizing."""

from _nbbuild import code, md, write_notebook

PREAMBLE = """\
import sys, pathlib
sys.path.insert(0, str(pathlib.Path.cwd().parents[1]))
from workshop_utils import get_chat_client
from agent_framework import Agent"""

cells = [
    md(
        """\
# M6 · Evaluating & Optimizing

> **Goal:** measure agent quality so you can improve it *on purpose* — not by vibes.
>
> **You'll use:** `evaluate_agent`, the `@evaluator` decorator, `LocalEvaluator`,
> and built-in checks like `keyword_check`.

---

A demo that works once isn't a product. To ship, you need a **repeatable
measurement** of quality that you can run on every change.

![Evaluation loop](../../assets/evaluation-loop.png)

The loop: **define checks → run them over a query set → inspect failures →
improve the agent → re-run.** Agent Framework gives you a lightweight harness for
exactly this — and the local checks below need **no extra API keys**."""
    ),
    md("## 1. Setup"),
    code(PREAMBLE),
    md(
        """\
## 2. Define checks

An **evaluator** is a function that inspects an agent's output and returns
pass/fail (or a score). Parameter names tell the framework what to pass in
(e.g. `response` = the agent's answer).

You can mix:

- **built-in** checks like `keyword_check("weather")` (answer must mention a word), and
- **custom** checks via the `@evaluator` decorator.

!!! tip "Make checks *instruction-sensitive*"
    A good check should be one the agent can only pass if it follows its
    instructions. `keyword_check("weather")` is weak here — the *question* already
    says "weather", so almost any answer repeats it. Below we also require a fixed
    **sign-off phrase** that only a well-instructed agent will produce. That's what
    lets section 4 actually *show* improvement."""
    ),
    code(
        '''\
from agent_framework import evaluator, keyword_check, LocalEvaluator

@evaluator
def is_helpful(response: str) -> bool:
    """Pass if the response is substantive and not a refusal."""
    refusals = ["i can't", "i'm not able", "i don't know"]
    return len(response) > 10 and not any(r in response.lower() for r in refusals)

# Combine built-in + custom checks into one local evaluator (no API key needed).
# The sign-off check is instruction-sensitive: only an agent told to add the
# phrase will pass it (see section 4).
local = LocalEvaluator(
    keyword_check("Stay weather-aware!"),   # must end with the mandated sign-off
    is_helpful,                             # our custom substance check
)
print("evaluator ready")'''
    ),
    md(
        """\
## 3. Run the evaluation

`evaluate_agent(...)` calls `agent.run()` for **each query**, then applies every
check to the output. You get a structured result you can print, inspect, or assert
on in CI."""
    ),
    code(
        '''\
agent = Agent(
    client=get_chat_client(),
    name="weather-assistant",
    instructions=(
        "You are a helpful weather assistant. Always mention the weather in your "
        "answer, and ALWAYS end your reply with the exact phrase: Stay weather-aware!"
    ),
)

from agent_framework import evaluate_agent

results = await evaluate_agent(
    agent=agent,
    queries=[
        "What's the weather like in Seattle?",
        "Will it rain in London tomorrow?",
        "What should I wear for 30°C weather?",
    ],
    evaluators=local,
)

for r in results:
    print(f"{r.provider}: {r.passed}/{r.total} passed")
    for item in r.items:
        print(f"  [{item.status}] Q: {item.input_text[:45]!r}")
        for score in item.scores:
            print(f"      {'PASS' if score.passed else 'FAIL'}  {score.name}")'''
    ),
    md(
        """\
!!! note "From scores to action"
    A failing check is a **lead**, not a verdict. If `keyword_check("Stay weather-aware!")`
    fails, maybe the instruction wasn't explicit enough — tighten it and re-run.
    That tighten-and-re-run cycle is the optimization loop."""
    ),
    md(
        """\
## 4. Close the loop: change the agent, re-measure

The point of a test is to **drive a change**. Below, a deliberately vague agent
fails more checks; then we improve its instructions and watch the score rise.
This is optimization you can *prove*, not guess."""
    ),
    code(
        '''\
vague = Agent(
    client=get_chat_client(),
    name="vague-assistant",
    instructions="Answer the question.",   # ← no mention of weather, terse
)

before = (await evaluate_agent(agent=vague, queries=[
    "What's the weather like in Seattle?",
    "Will it rain in London tomorrow?",
], evaluators=local))[0]
print(f"BEFORE (vague):   {before.passed}/{before.total} passed")

improved = Agent(
    client=get_chat_client(),
    name="improved-assistant",
    instructions=(
        "You are a weather assistant. Always explicitly mention the weather, be "
        "helpful and specific, and ALWAYS end your reply with the exact phrase: "
        "Stay weather-aware!"
    ),
)

after = (await evaluate_agent(agent=improved, queries=[
    "What's the weather like in Seattle?",
    "Will it rain in London tomorrow?",
], evaluators=local))[0]
print(f"AFTER (improved): {after.passed}/{after.total} passed")'''
    ),
    md(
        """\
## 5. Use it in CI

Call `results[0].raise_for_status()` to turn a failing eval into a non-zero exit
code — so a regression in agent quality **breaks the build**, just like a unit test:

```python
results = await evaluate_agent(agent=agent, queries=[...], evaluators=local)
results[0].raise_for_status()   # raises EvalNotPassedError if any check fails
```

Beyond local checks, Agent Framework integrates **model-graded** evaluators
(groundedness, relevance, coherence) for quality you can't capture with keywords —
see the upstream `02-agents/evaluation/` and `05-end-to-end/evaluation/` samples."""
    ),
    md(
        """\
## 🧪 Your turn

1. Add a custom `@evaluator` that checks the answer is **under N characters**
   (a brevity check) and add it to the `LocalEvaluator`.
2. Expand the query set to 6–8 prompts, including a couple designed to *trip up*
   the agent. Which checks catch them?
3. Re-run section 4 but improve the agent a *different* way (add a tool instead of
   editing instructions). Did the score move?

---

✅ **You can measure quality.** Now see inside the agent in production.
→ **[M7 · Operationalizing](07-operationalize.ipynb)**"""
    ),
]

write_notebook("docs/modules/06-evaluation.ipynb", cells)
