# Agentic AI — Microsoft Agent Framework Workshop

A **one-day, hands-on coding workshop** that teaches how to build, optimize, and
operationalize AI agents with the open-source **[Microsoft Agent
Framework](https://github.com/microsoft/agent-framework)** (Python).

It's **code-first** and **provider-agnostic**: every lab runs on Azure AI Foundry,
OpenAI, Azure OpenAI, Anthropic, Ollama, AWS Bedrock, or Google Gemini — you change
**one environment variable**, not your code.

> 📖 **Workshop site:** <https://monuminu.github.io/DHS-workshop26/>
> *(published from `docs/` via GitHub Pages — see below to enable it)*

---

## What you'll build

Starting from a single LLM call, you assemble a complete **agent harness** —
tools, memory, planning, multi-agent orchestration, evaluation, and observability.

| Module | Concept |
|:--|:--|
| **M1 · Your First Agent** | the agent loop, streaming |
| **M2 · Tools & Function Calling** | `@tool`, the tool loop, approvals |
| **M3 · Context Engineering** | sessions, memory, compaction |
| **M4 · The Agent Harness** ★ | `create_harness_agent` — batteries included |
| **M5 · Multi-Agent Orchestration** | agents-as-nodes workflows, executors + edges |
| **M6 · Evaluating & Optimizing** | `evaluate_agent`, custom checks, CI gates |
| **M7 · Operationalizing** | middleware, OpenTelemetry tracing |
| **M8 · Capstone & Hosting** | combine everything; A2A, Functions, containers |

The labs live in [`docs/modules/`](docs/modules/) as Jupyter notebooks and double
as the site's pages.

---

## Quick start

```bash
git clone https://github.com/monuminu/DHS-workshop26.git
cd DHS-workshop26

# create an environment and install (uv recommended)
uv venv --python 3.12 .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
uv pip install -e ".[docs]"

# register the notebook kernel
python -m ipykernel install --user --name dhs-workshop26 --display-name "DHS Workshop"

# pick a model backend
cp .env.example .env                 # then edit MODEL_PROVIDER + that provider's vars
az login                             # only for the foundry / azure-openai backends
```

Then open `docs/modules/01-first-agent.ipynb` and select the **DHS Workshop**
kernel. Full instructions: **[docs/setup.md](docs/setup.md)**.

> **Why pinned packages?** The labs use `create_harness_agent`, which ships in
> Agent Framework **core 1.8.0**. We pin specific 1.8.0 subpackages rather than the
> `agent-framework` meta-package (which pulls pre-release-only deps and can fail to
> resolve). See [`pyproject.toml`](pyproject.toml).

---

## Repo layout

```
.
├── docs/                       # MkDocs site (also the workshop content)
│   ├── index.md  setup.md  concepts.md
│   ├── assets/                 # generated architecture diagrams
│   └── modules/                # the 8 lab notebooks
├── workshop_utils/clients.py   # get_chat_client() — the provider switcher
├── scripts/                    # notebook generators (gen_mN.py) + nbformat helper
├── mkdocs.yml                  # site config (Material + mkdocs-jupyter)
├── pyproject.toml              # pinned deps + provider extras
├── .env.example                # all provider environment variables
└── .github/workflows/deploy-docs.yml   # build + deploy to GitHub Pages
```

---

## Build the site locally

```bash
mkdocs serve            # http://127.0.0.1:8000
mkdocs build --strict   # production build into ./site
```

## Publish to GitHub Pages

The included workflow ([`.github/workflows/deploy-docs.yml`](.github/workflows/deploy-docs.yml))
builds and deploys on every push to `main`. **One-time setup:** in the repo's
**Settings → Pages → Build and deployment**, set **Source** to **GitHub Actions**.
The site then appears at `https://monuminu.github.io/DHS-workshop26/`.

---

## Provider support

| `MODEL_PROVIDER` | Install |
|:--|:--|
| `foundry` *(default)*, `openai`, `azure-openai`, `gemini` | included |
| `anthropic` | `uv pip install -e ".[anthropic]"` |
| `ollama` | `uv pip install -e ".[ollama]"` |
| `bedrock` | `uv pip install -e ".[bedrock]"` |

Gemini has no native Agent Framework client; it's reached through its
OpenAI-compatible endpoint.

---

## Credits

Built on samples from
[microsoft/agent-framework](https://github.com/microsoft/agent-framework).
Licensed under MIT.
