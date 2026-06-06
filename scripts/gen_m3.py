"""Generate Module 3 — Context Engineering."""

from _nbbuild import code, md, write_notebook

PREAMBLE = """\
import sys, pathlib
sys.path.insert(0, str(pathlib.Path.cwd().parents[1]))
from workshop_utils import get_chat_client
from agent_framework import Agent"""

cells = [
    md(
        """\
# M3 · Context Engineering

> **Goal:** control *what the model sees* on every turn — the single biggest lever
> on real-world agent quality.
>
> **You'll use:** sessions, a custom `ContextProvider` for memory, and the *idea*
> of compaction.

---

The model only ever sees what fits in its **context window**. **Context
engineering** is the discipline of deciding what goes in that window each turn:

| Lever | What it does |
|:--|:--|
| **Sessions** | Carry conversation history across turns |
| **Context providers** | Inject dynamic facts / instructions before each run |
| **Memory** | Persist what matters about the user or task |
| **Compaction** | Summarize or trim history so you never overflow the window |

![Context engineering](../../assets/context-engineering.png)"""
    ),
    md("## 1. Setup"),
    code(PREAMBLE),
    md(
        """\
## 2. The problem: stateless by default

Each `agent.run(...)` is independent. Without a session, the agent has **no idea**
what you said a moment ago. Watch it forget:"""
    ),
    code(
        '''\
forgetful = Agent(
    client=get_chat_client(),
    name="Forgetful",
    instructions="You are a friendly assistant. Keep answers brief.",
)

print(await forgetful.run("My name is Alice and I love hiking."))
print(await forgetful.run("What's my name and favourite hobby?"))  # ❌ it won't know'''
    ),
    md(
        """\
## 3. Sessions: carry history across turns

A **session** holds the running conversation. Pass the *same* session to each
`run()` and the agent remembers everything in it."""
    ),
    code(
        '''\
agent = Agent(
    client=get_chat_client(),
    name="ConversationAgent",
    instructions="You are a friendly assistant. Keep answers brief.",
)

session = agent.create_session()

print(await agent.run("My name is Alice and I love hiking.", session=session))
print(await agent.run("What's my name and favourite hobby?", session=session))  # ✅ remembers'''
    ),
    md(
        """\
!!! note "Session = short-term memory"
    The session is the conversation transcript. It's *short-term* memory: useful
    within a chat, but it grows with every turn and disappears when the session
    ends. For durable, *selective* memory we use a **context provider**."""
    ),
    md(
        """\
## 4. Memory with a `ContextProvider`

A `ContextProvider` plugs into the agent loop with two hooks:

- **`before_run`** — inject instructions/facts *into* the next model call.
- **`after_run`** — observe the exchange and *update* what you remember.

This provider extracts the user's name and re-injects it on every future turn —
durable, structured memory rather than relying on raw transcript."""
    ),
    code(
        '''\
from typing import Any
from agent_framework import AgentSession, ContextProvider, SessionContext

class UserMemoryProvider(ContextProvider):
    """Remembers the user's name in session state and personalizes replies."""

    DEFAULT_SOURCE_ID = "user_memory"

    def __init__(self):
        super().__init__(self.DEFAULT_SOURCE_ID)

    async def before_run(self, *, agent: Any, session: "AgentSession | None",
                         context: SessionContext, state: dict[str, Any]) -> None:
        name = state.get("user_name")
        if name:
            context.extend_instructions(self.source_id,
                f"The user's name is {name}. Always address them by name.")
        else:
            context.extend_instructions(self.source_id,
                "You don't know the user's name yet. Ask for it politely.")

    async def after_run(self, *, agent: Any, session: "AgentSession | None",
                        context: SessionContext, state: dict[str, Any]) -> None:
        for msg in context.input_messages:
            text = getattr(msg, "text", "") or ""
            if "my name is" in text.lower():
                state["user_name"] = text.lower().split("my name is")[-1].strip().split()[0].capitalize()

print("provider ready")'''
    ),
    code(
        '''\
mem_agent = Agent(
    client=get_chat_client(),
    name="MemoryAgent",
    instructions="You are a friendly assistant.",
    context_providers=[UserMemoryProvider()],
)

s = mem_agent.create_session()
print(await mem_agent.run("Hello! What's the square root of 9?", session=s))  # asks for name
print(await mem_agent.run("My name is Alice", session=s))                     # stores it
print(await mem_agent.run("What is 2 + 2?", session=s))                       # greets by name

# Inspect what the provider stored:
print("\\n[stored state]", s.state.get("user_memory"))'''
    ),
    md(
        """\
!!! tip "This pattern scales"
    The same two hooks power production memory: store user preferences, retrieved
    documents (RAG), tool results, or a running summary. Agent Framework ships
    richer providers too — `mem0`, Redis, Azure AI Search, and a file-based
    `MemoryStore` (which the harness uses in M4)."""
    ),
    md(
        """\
## 5. Compaction: never overflow the window

Long conversations eventually exceed the context window. **Compaction**
automatically summarizes or trims old history so the agent keeps running.

You won't wire it by hand here — it's one of the batteries the **agent harness**
includes automatically (`max_context_window_tokens` triggers it). The mental model:

```
[ system ][ summary of old turns ][ recent turns ][ new question ]
            ▲ compaction replaces a long tail of turns with a short summary
```

Key idea: **what** you keep (recent + summary + pinned facts) is a *design choice*.
That choice is context engineering."""
    ),
    md(
        """\
## 🧪 Your turn

1. Extend `UserMemoryProvider` to also remember a **hobby** (look for *"I love"*),
   and have it greet the user with both name and hobby.
2. Print `session` history length after several turns to *see* it grow — that's the
   pressure compaction relieves.
3. Skim the upstream `simple_context_provider.py`: it uses the **model itself** to
   extract structured `{name, age}` with a Pydantic schema instead of string
   matching. Why is that more robust?

---

✅ **You can engineer what the agent sees.** Now assemble all of it at once.
→ **[M4 · The Agent Harness](04-agent-harness.ipynb)** ★"""
    ),
]

write_notebook("docs/modules/03-context-engineering.ipynb", cells)
