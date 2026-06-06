# Setup — do this before the workshop

This takes about **15 minutes**. You'll install the workshop, pick a model
provider, and run a 3-line smoke test to confirm everything works.

!!! note "Why so little setup?"
    The whole workshop is **provider-agnostic**. You install a small, pinned set
    of packages once, choose a backend with a single environment variable, and
    every lab just works.

---

## 1. Get the code

```bash
git clone https://github.com/monuminu/DHS-workshop26.git
cd DHS-workshop26
```

## 2. Create an environment and install

We recommend [`uv`](https://docs.astral.sh/uv/) (fast), but plain `pip` works too.

=== "uv (recommended)"

    ```bash
    uv venv --python 3.12 .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    uv pip install -e ".[docs]"
    ```

=== "pip"

    ```bash
    python -m venv .venv
    source .venv/bin/activate          # Windows: .venv\Scripts\activate
    pip install -e ".[docs]"
    ```

!!! warning "Pin to 1.8.0 — don't install the `agent-framework` meta-package"
    This workshop pins specific Agent Framework **1.8.0** subpackages. The labs
    depend on `create_harness_agent`, which ships in core **1.8.0**. The umbrella
    `agent-framework` package pulls in `core[all]` (pre-release-only deps) and can
    fail to resolve — so we install just the providers the labs use. The
    `pyproject.toml` already does this for you.

## 3. Register the Jupyter kernel

```bash
python -m ipykernel install --user --name dhs-workshop26 --display-name "DHS Workshop"
```

When you open a lab notebook, select the **DHS Workshop** kernel.

---

## 4. Pick your model provider

Copy the example env file and edit it:

```bash
cp .env.example .env
```

Set `MODEL_PROVIDER` to your choice and fill in **only that provider's** values.

| `MODEL_PROVIDER` | What you need | Extra install |
|:--|:--|:--|
| `foundry` *(default)* | An Azure AI Foundry project + `az login`. Set `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`. | — (included) |
| `openai` | `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL` | — (included) |
| `azure-openai` | `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_MODEL`, key **or** `az login` | — (included) |
| `anthropic` | `ANTHROPIC_API_KEY`, `ANTHROPIC_CHAT_MODEL` | `uv pip install -e ".[anthropic]"` |
| `ollama` | Local [Ollama](https://ollama.com); `OLLAMA_MODEL` (no key!) | `uv pip install -e ".[ollama]"` |
| `bedrock` | `BEDROCK_REGION`, `BEDROCK_CHAT_MODEL`, AWS creds | `uv pip install -e ".[bedrock]"` |
| `gemini` | `GEMINI_API_KEY`, `GEMINI_MODEL` (OpenAI-compatible endpoint) | — (included) |

!!! info "About Gemini"
    Agent Framework has **no first-class Gemini client**. Gemini offers an
    OpenAI-compatible API, so the workshop points the OpenAI client at Gemini's
    endpoint. It works for the chat-based labs; some advanced provider-specific
    features (e.g. certain hosted tools) may not apply.

### Azure auth (for `foundry` / `azure-openai` with Entra ID)

```bash
az login
```

---

## 5. Smoke test

Run this from the repo root (with your `.venv` active). It builds an agent using
**your** configured provider and runs one prompt:

```python
import asyncio
from workshop_utils import get_chat_client, current_provider
from agent_framework import Agent

async def main():
    print("Provider:", current_provider())
    agent = Agent(
        client=get_chat_client(),
        name="SmokeTest",
        instructions="You are a friendly assistant. Keep answers to one sentence.",
    )
    print("Agent:", await agent.run("Say hello and name one thing an AI agent can do."))

asyncio.run(main())
```

Save it as `smoke_test.py` and run `python smoke_test.py`. A one-sentence reply
means you're ready. 🎉

??? bug "Troubleshooting"
    - **`Model is required` / `endpoint must be provided`** → you haven't filled in
      your provider's variables in `.env`, or `MODEL_PROVIDER` doesn't match the
      section you filled.
    - **`ModuleNotFoundError: agent_framework.<provider>`** → install that provider's
      extra (see the table above).
    - **Azure auth errors** → run `az login` and confirm you can see your project in
      the [Azure AI Foundry portal](https://ai.azure.com).
    - **Ollama connection refused** → start Ollama and `ollama pull llama3.1:8b`.

---

You're set. → Read the **[Concepts](concepts.md)**, then start **[M1 · Your First Agent](modules/01-first-agent.ipynb)**.
