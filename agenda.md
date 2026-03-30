# Build Agents with Azure AI

### One-Day Workshop Agenda

> **Audience:** Software Developers
> **Format:** Lecture + Hands-on Labs
> **Duration:** Full Day (9:00 AM - 5:00 PM)
> **Prerequisites:** Azure subscription, basic Python experience, VS Code installed

---

## Schedule at a Glance

| Time | Session | Format |
|:---|:---|:---:|
| 9:00 - 9:45 | Welcome & Introduction to AI Agents on Azure | Lecture |
| 9:45 - 10:45 | Lab 1 - Build Your First Agent | Hands-on |
| 10:45 - 11:00 | Break | - |
| 11:00 - 12:00 | Lab 2 - Supercharging Agents with Tools | Lecture + Hands-on |
| 12:00 - 12:45 | Lunch | - |
| 12:45 - 1:30 | Deep Dive - RAG Agents with Azure AI Search | Lecture |
| 1:30 - 2:30 | Lab 3 - Build a RAG-Powered Agent | Hands-on |
| 2:30 - 2:45 | Break | - |
| 2:45 - 3:30 | Multi-Agent Systems & Orchestration | Lecture |
| 3:30 - 4:30 | Lab 4 - Build a Multi-Agent Solution | Hands-on |
| 4:30 - 5:00 | Production Best Practices & Wrap-up | Lecture + Q&A |

---

## Pre-Workshop Setup

Participants should complete the following before the workshop:

- [ ] **Azure subscription** - [Create a free account](https://azure.microsoft.com/free/) if needed
- [ ] **Python 3.10+** installed - [Download](https://www.python.org/downloads/)
- [ ] **VS Code** with the Python extension - [Download](https://code.visualstudio.com/)
- [ ] **Azure CLI** installed and signed in (`az login`) - [Install](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [ ] **Azure Developer CLI (azd)** installed - [Install](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [ ] **Docker Desktop** installed (for hosted agent lab) - [Download](https://www.docker.com/products/docker-desktop/)

---

## Session Details

---

### 9:00 - 9:45 | Welcome & Introduction to AI Agents on Azure

**Format:** Lecture (45 min)

#### Topics

- **What are AI Agents?**
  - From chatbots to autonomous agents — the evolution
  - Key characteristics: reasoning, tool use, memory, planning
  - Agent design patterns: ReAct, tool-augmented generation, multi-agent

- **Azure AI Foundry Overview**
  - Foundry portal, projects, and resource model
  - Model catalog — GPT-4o, Llama, DeepSeek, Cohere, and more
  - Foundry Agent Service architecture

- **Microsoft Foundry Agent Service**
  - Prompt agents vs. hosted agents
  - Agent runtime, threads, and conversations
  - Built-in tool ecosystem at a glance
  - SDKs: Python (`azure-ai-projects`), C#, TypeScript, Java, REST API

#### Key Takeaways

> Participants understand the Azure AI Foundry landscape and the Foundry Agent Service architecture. They know the difference between prompt agents and hosted agents, and can identify which tools are available.

---

### 9:45 - 10:45 | Lab 1 - Build Your First Agent

**Format:** Hands-on Lab (60 min)

#### Objectives

- Set up the development environment
- Create an Azure AI Foundry project
- Build and run a prompt agent using the Python SDK
- Interact with the agent through threads and conversations

#### Lab Steps

1. **Environment Setup** (15 min)
   - Install the Python SDK:
     ```bash
     pip install azure-ai-projects azure-identity
     ```
   - Configure environment variables (`PROJECT_ENDPOINT`, `MODEL_DEPLOYMENT_NAME`)
   - Authenticate with `az login`

2. **Create Your First Agent** (20 min)
   - Initialize the `AIProjectClient`
   - Create an agent with custom instructions
   - Create a thread, send messages, and process responses
   - Explore streaming vs. non-streaming responses

3. **Portal Exploration** (10 min)
   - Create an agent in the [Foundry portal](https://ai.azure.com) (no-code)
   - Compare the portal experience vs. SDK approach

4. **Experiment & Extend** (15 min)
   - Modify instructions and observe behavior changes
   - Try different models from the catalog
   - Explore conversation history and thread management

#### Resources

- [Microsoft Foundry Quickstart](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code)
- [Python SDK Reference](https://aka.ms/azsdk/azure-ai-projects/python/reference)

---

### 10:45 - 11:00 | Break (15 min)

---

### 11:00 - 12:00 | Lab 2 - Supercharging Agents with Tools

**Format:** Lecture (20 min) + Hands-on Lab (40 min)

#### Lecture: The Agent Tool Ecosystem

- **Built-in Tools Overview**

  | Tool | What It Does |
  |:---|:---|
  | Code Interpreter | Execute Python code, generate charts, process files |
  | File Search | Search and retrieve from uploaded documents |
  | Bing Grounding | Access real-time web information via Bing Search |
  | Azure Functions | Call serverless functions as agent tools |
  | OpenAPI | Connect to any REST API via OpenAPI spec |
  | MCP Servers | Integrate Model Context Protocol tools |

- **Function Calling** — Define custom functions the agent can invoke
- **Tool selection best practices** — When to use which tool

#### Lab Steps

1. **Code Interpreter** (15 min)
   - Attach the Code Interpreter tool to your agent
   - Ask the agent to perform data analysis and generate visualizations
   - Upload a CSV file and have the agent process it

2. **File Search** (10 min)
   - Upload documents to a vector store
   - Create an agent with File Search enabled
   - Query the agent about the uploaded documents

3. **Bing Grounding** (10 min)
   - Set up a Bing Grounding connection
   - Create an agent that can search the web for real-time information
   - Handle citations and source attribution

4. **Custom Function Calling** (5 min)
   - Define a custom function (e.g., get weather, lookup database)
   - Attach it to the agent and test the function calling flow

#### Resources

- [Tool Best Practices](https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice)
- [Code Interpreter Guide](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/code-interpreter)
- [Bing Grounding Guide](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/bing-tools)

---

### 12:00 - 12:45 | Lunch (45 min)

---

### 12:45 - 1:30 | Deep Dive - RAG Agents with Azure AI Search

**Format:** Lecture (45 min)

#### Topics

- **Why RAG for Agents?**
  - Limitations of parametric knowledge
  - Retrieval-Augmented Generation explained
  - RAG vs. fine-tuning vs. prompt engineering

- **Azure AI Search as a Knowledge Source**
  - Index creation and document ingestion
  - Vector search, hybrid search, and semantic ranking
  - Embeddings with Azure OpenAI

- **Integrating Azure AI Search with Agent Service**
  - The Azure AI Search tool for agents
  - Index connection configuration
  - Query strategies: keyword, vector, hybrid
  - Chunking strategies and relevance tuning

- **Architecture Patterns**
  - Simple RAG agent
  - Agentic RAG with iterative retrieval
  - Multi-source RAG (combining search + file search + web)

#### Key Takeaways

> Participants understand how to ground agents in enterprise data using Azure AI Search, and can design effective RAG architectures for their use cases.

---

### 1:30 - 2:30 | Lab 3 - Build a RAG-Powered Agent

**Format:** Hands-on Lab (60 min)

#### Objectives

- Create an Azure AI Search index with sample documents
- Build an agent that retrieves and reasons over enterprise knowledge
- Implement citation handling and source attribution

#### Lab Steps

1. **Set Up Azure AI Search** (15 min)
   - Create an Azure AI Search resource (or use pre-provisioned)
   - Upload sample documents (e.g., product manuals, HR policies)
   - Create a vector index with embeddings

2. **Connect Search to Your Agent** (15 min)
   - Configure the Azure AI Search tool connection
   - Create an agent with search grounding
   - Set instructions for search behavior and citation format

3. **Test and Iterate** (20 min)
   - Ask questions that require document retrieval
   - Observe how the agent combines search results with reasoning
   - Compare keyword vs. vector vs. hybrid search quality

4. **Advanced Patterns** (10 min)
   - Combine Azure AI Search with File Search for multi-source RAG
   - Add Bing Grounding for real-time information alongside enterprise data
   - Test agentic retrieval with follow-up questions

#### Resources

- [Azure AI Search Tool](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/azure-ai-search)
- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)

---

### 2:30 - 2:45 | Break (15 min)

---

### 2:45 - 3:30 | Multi-Agent Systems & Orchestration

**Format:** Lecture (45 min)

#### Topics

- **Why Multi-Agent?**
  - Single agent limitations
  - Specialization, delegation, and collaboration patterns
  - When to use multi-agent vs. a single agent with many tools

- **Connected Agents in Foundry**
  - Architecture: main agent + connected agents
  - How connected agents communicate
  - Response aggregation and handoff patterns
  - The `ConnectedAgentTool` API

- **Agent-to-Agent Protocol (A2A)**
  - What is A2A and why it matters
  - Connecting Foundry agents with external agent endpoints
  - A2A vs. Connected Agents — when to use which

- **Workflows in Foundry**
  - Visual workflow builder
  - Orchestrating agents and business logic
  - Conditional routing and parallel execution

- **Hosted Agents**
  - Containerized agents with Agent Framework or LangGraph
  - Docker + Azure Developer CLI (`azd`) deployment
  - When to choose hosted agents vs. prompt agents

#### Key Takeaways

> Participants can design multi-agent architectures using Connected Agents, understand the A2A protocol, and know when to use hosted agents for complex scenarios.

---

### 3:30 - 4:30 | Lab 4 - Build a Multi-Agent Solution

**Format:** Hands-on Lab (60 min)

#### Objectives

- Design and implement a multi-agent system with specialized agents
- Use Connected Agents to orchestrate collaboration
- Test the end-to-end multi-agent workflow

#### Lab Steps

1. **Design the Agent Team** (10 min)
   - Scenario: Build a "Research Assistant" with specialized sub-agents
   - Define roles:
     - **Research Agent** — searches the web using Bing Grounding
     - **Analysis Agent** — processes data with Code Interpreter
     - **Writer Agent** — synthesizes findings into a report

2. **Build Specialized Agents** (15 min)
   - Create each agent with focused instructions and tools
   - Test each agent individually to verify capability

3. **Connect Agents Together** (20 min)
   - Create the main orchestrator agent
   - Attach sub-agents using `ConnectedAgentTool`
   - Configure how the main agent delegates tasks

4. **Test the Multi-Agent System** (15 min)
   - Send complex queries that require multiple agents to collaborate
   - Observe the orchestration flow and agent interactions
   - Review run steps to understand delegation decisions
   - Iterate on instructions to improve collaboration quality

#### Resources

- [Connected Agents Guide](https://learn.microsoft.com/azure/foundry/agents/how-to/connected-agents)
- [Multi-Agent Training Module](https://learn.microsoft.com/training/modules/develop-multi-agent-azure-ai-foundry/)
- [A2A Protocol Documentation](https://learn.microsoft.com/azure/foundry/agents/how-to/tools/agent-to-agent)

---

### 4:30 - 5:00 | Production Best Practices & Wrap-up

**Format:** Lecture + Q&A (30 min)

#### Topics

- **Observability & Monitoring**
  - End-to-end tracing with Application Insights
  - Monitoring agent decisions, tool calls, and token usage
  - Setting up alerts for failures and performance degradation

- **Security & Identity**
  - Microsoft Entra authentication and RBAC
  - Content filters and safety guardrails
  - Virtual network isolation and data protection
  - Managed credentials and On-Behalf-Of (OBO) authentication

- **Deployment & Scaling**
  - Agent versioning and stable endpoints
  - Hosted agents for custom runtime requirements
  - Publishing to Microsoft Teams and Microsoft 365 Copilot

- **Cost Management**
  - Understanding token consumption and tool call costs
  - Optimizing agent instructions for efficiency
  - Monitoring usage with Azure Cost Management

- **What's Next?**
  - Explore the [Foundry Model Catalog](https://ai.azure.com/explore/models)
  - Try [Agent Framework](https://learn.microsoft.com/agent-framework/) for advanced scenarios
  - Join the [Azure AI community](https://learn.microsoft.com/azure/ai-services/)

#### Q&A Session

> Open floor for questions, architecture discussions, and next steps for your own agent projects.

---

## Additional Resources

| Resource | Link |
|:---|:---|
| Microsoft Foundry Portal | https://ai.azure.com |
| Agent Service Overview | https://learn.microsoft.com/azure/foundry/agents/overview |
| Foundry Quickstart | https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code |
| Tool Best Practices | https://learn.microsoft.com/azure/foundry/agents/concepts/tool-best-practice |
| Python SDK Samples | https://aka.ms/azsdk/azure-ai-projects/python/samples/ |
| Multi-Agent Training | https://learn.microsoft.com/training/modules/develop-multi-agent-azure-ai-foundry/ |
| Agent Framework Docs | https://learn.microsoft.com/agent-framework/ |
| Hosted Agent Quickstart | https://learn.microsoft.com/azure/foundry/agents/quickstarts/quickstart-hosted-agent |

---

*Workshop created for developers building AI agents with Microsoft Foundry Agent Service.*
