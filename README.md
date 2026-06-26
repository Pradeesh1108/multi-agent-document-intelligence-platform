<div align="center">
  <h1>🚀 Multi-Agent Document Intelligence Platform</h1>
  <p><em>An AI-powered document processing engine that reads, understands, and acts on business documents — autonomously.</em></p>

  <!-- Tech Stack Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=python&logoColor=white" alt="LangGraph" />
    <img src="https://img.shields.io/badge/ChromaDB-1D2939?style=for-the-badge&logo=database&logoColor=white" alt="ChromaDB" />
    <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" />
    <img src="https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
    <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
    <img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" />
  </p>
</div>

---

## 📌 The Problem

Every business runs on documents — invoices from vendors, complaints from customers, RFQs from procurement teams, compliance audits, and fraud alerts. In most organizations, these documents arrive in completely different formats (emails, PDFs, JSON payloads, plain text) through different channels (inboxes, API endpoints, ERP systems), and they all need to be **read, understood, classified, and acted upon** — usually by a human sitting at a desk, reading each one, figuring out what it is, routing it to the right person, and hoping nothing slips through the cracks.

This process is:
- **Slow** — A single invoice can take 15+ minutes to triage manually.
- **Error-prone** — Humans miss fraud signals, mislabel priorities, and forget to escalate.
- **Unscalable** — Hiring more people doesn't solve the structural bottleneck.
- **Costly** — According to industry studies, enterprises spend $5–$25 per document on manual processing.

**What if a system could do all of this — read any document, understand its intent, extract structured data, check it against company policies, assess risk, make a decision, and take action — entirely on its own?**

That's exactly what this platform does.

---

## 💡 What This Project Does

The **Multi-Agent Document Intelligence Platform** is an end-to-end AI automation engine that processes incoming business documents through a pipeline of 7 specialized AI agents. Each agent has a single responsibility, and together they form an autonomous decision-making chain that replaces the manual document triage workflow.

Here's what happens when a document enters the system:

| Step | Agent | What It Does |
|------|-------|-------------|
| 1 | **Intake Agent** | Accepts the raw document (email, PDF, JSON, or plain text), detects its format, cleans the content, and normalizes it for downstream processing. |
| 2 | **Intent Agent** | Uses an LLM to classify the document's business intent — Is this an invoice? A customer complaint? A fraud alert? An RFQ? It returns a classification with a confidence score and reasoning. |
| 3 | **Extraction Agent** | Based on the classified intent, dynamically selects the right Pydantic schema and uses LLM structured output to extract type-safe entities (e.g., invoice amount, vendor name, complainant email, urgency level). |
| 4 | **Knowledge Agent** | Queries a ChromaDB vector store loaded with company policies, fraud detection rules, and compliance guidelines to provide business context for the document. |
| 5 | **Risk Agent** | Combines extracted entities, knowledge context, and rule-based checks (high-value amounts, high-risk countries, missing fields) with LLM analysis to produce a risk score (0.0–1.0) and risk level. |
| 6 | **Decision Agent** | Synthesizes all upstream outputs — intent, entities, knowledge context, and risk — to make a final workflow decision: escalate to CRM, create a support ticket, flag for fraud, process the invoice, or route for manual review. |
| 7 | **Action Agent** | Executes the decision by interfacing with external tools — creates CRM tickets, sends email notifications to relevant teams, validates documents, and logs the outcome. |

The entire pipeline runs in seconds. No human in the loop unless the system explicitly decides human review is needed.

---

## 🏗️ System Architecture

The core of the system is a **7-node LangGraph StateGraph** with conditional routing. This isn't a simple linear chain — the graph includes conditional edges that can skip unnecessary steps (e.g., bypassing knowledge retrieval for general inquiries) or abort early on invalid input.

![System Architecture](snaps/System%20Arch.png)

---

## 🔧 How It Works — Under the Hood

### Multi-Format Document Parsing

The system auto-detects and handles 4 input formats:

- **Email** — Parses RFC-style headers (`From:`, `Subject:`, `To:`, `Date:`) and extracts the body. Detects email structure using regex heuristics.
- **PDF** — Extracts text from PDF files using PyMuPDF (fitz), handling multi-page documents.
- **JSON** — Validates and parses structured JSON payloads from API integrations and webhooks.
- **Plain Text** — Accepts raw text with content-based type inference.

### Intent-Aware Entity Extraction

Instead of using a single generic extraction prompt, the system dynamically selects a **Pydantic schema** based on the classified intent:

| Intent | Schema | Fields Extracted |
|--------|--------|-----------------|
| `invoice` | `InvoiceEntities` | invoice_id, vendor, amount, currency, due_date, line_items |
| `complaint` | `ComplaintEntities` | customer_name, customer_email, issue_summary, urgency, category |
| `rfq` | `RFQEntities` | requester_name, requester_email, products_services, quantity, deadline, budget |
| `compliance` | `PDFEntities` | document_type, title, summary, key_entities, regulatory_keywords |
| `fraud_risk` | `GenericEntities` | summary, key_fields, entities_found |

All extraction uses LangChain's `with_structured_output()`, ensuring the LLM returns **validated, type-safe data** — not free-form text that needs post-processing.

### RAG-Powered Knowledge Retrieval

The Knowledge Agent queries a **ChromaDB** vector store pre-loaded with:
- **CRM Escalation Policies** — Priority levels (P0–P3), response SLAs, escalation triggers
- **Fraud Detection Rules** — Financial fraud signals, document fraud indicators, identity fraud patterns, risk scoring guidelines
- **Compliance Guidelines** — Regulatory frameworks, audit requirements

This means the system doesn't just classify documents — it contextualizes them against your company's actual business rules before making decisions.

### Multi-Provider LLM Support

The platform uses a **factory pattern** (`LLMFactory`) that supports runtime provider switching:
- **Google Gemini** — via `langchain-google-genai`
- **Groq (LLaMA)** — via `langchain-groq`

You can switch providers via environment variables or directly from the frontend UI — useful for comparing model performance or falling back to an alternative provider.

### Tool-Based Action Execution

The Action Agent doesn't just output text — it executes real actions through LangChain tools:
- **CRM Tool** — Creates and updates support tickets with priority, category, and assignee routing
- **Email Tool** — Sends notifications to relevant teams (fraud-team@, compliance@, finance@, escalations@)
- **Validation Tool** — Runs document validation checks against business rules
- **Risk Tool** — Performs automated risk checks (high-value amount detection, high-risk country flagging, missing field analysis)

---

## 🖥️ Frontend — Workflow Simulation Dashboard

The platform includes a **glassmorphism-styled monitoring dashboard** that lets you:

- **Upload documents** — Drag-and-drop PDFs, JSON, TXT, or EML files
- **Paste raw text** — Directly input email bodies, JSON payloads, or plain text
- **Select LLM provider** — Switch between Gemini and Groq in real time
- **Override API keys** — Test with your own keys without modifying `.env`
- **View full pipeline results** — See intent classification, extracted entities, knowledge context, risk analysis, decision, and executed actions — all in one view

The frontend communicates with the FastAPI backend through REST endpoints and renders the full agent pipeline output in a structured, readable format.

---

## 🧰 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Orchestration** | LangGraph | Multi-agent StateGraph with conditional edges and typed state |
| **LLM Framework** | LangChain | Agent prompting, structured output, tool binding |
| **LLM Providers** | Gemini, Groq | Multi-provider support with runtime switching |
| **API** | FastAPI | REST endpoints, file upload handling, CORS middleware |
| **Vector Store** | ChromaDB | RAG knowledge retrieval for policy contextualization |
| **Schema Validation** | Pydantic v2 | Type-safe entity extraction and agent output validation |
| **PDF Processing** | PyMuPDF (fitz) | Multi-page PDF text extraction |
| **Frontend** | HTML, CSS, JavaScript | Glassmorphism monitoring dashboard |
| **Containerization** | Docker | Production-ready containerized deployment |
| **Deployment** | Vercel | Serverless deployment configuration |
| **Testing** | pytest | Unit tests for schemas, LLM factory, and workflow |
| **Package Management** | uv | Fast Python dependency management |

---

## 📂 Project Structure

```
multi-agent-doc-intel/
├── src/
│   ├── agents/                  # 7 specialized AI agents
│   │   ├── intake_agent.py      # Document normalization & validation
│   │   ├── intent_agent.py      # Business intent classification
│   │   ├── extraction_agent.py  # Schema-based entity extraction
│   │   ├── knowledge_agent.py   # RAG knowledge retrieval
│   │   ├── risk_agent.py        # Risk scoring & assessment
│   │   ├── decision_agent.py    # Workflow decision synthesis
│   │   └── action_agent.py      # Tool execution & action routing
│   ├── graph/                   # LangGraph pipeline definition
│   │   ├── workflow.py          # StateGraph compilation
│   │   ├── nodes.py             # Node wrappers for each agent
│   │   ├── edges.py             # Conditional routing logic
│   │   └── state.py             # Typed workflow state schema
│   ├── rag/                     # RAG subsystem
│   │   ├── ingestion.py         # Knowledge base document ingestion
│   │   ├── retriever.py         # ChromaDB query interface
│   │   └── vector_store.py      # ChromaDB collection management
│   ├── tools/                   # LangChain tool implementations
│   │   ├── crm_tool.py          # CRM ticket creation & updates
│   │   ├── email_tool.py        # Email notification dispatch
│   │   ├── risk_tool.py         # Automated risk checks
│   │   └── validation_tool.py   # Document validation checks
│   ├── schemas/                 # Pydantic models
│   │   ├── agent_outputs.py     # Structured output schemas for all agents
│   │   ├── documents.py         # Document input schemas
│   │   └── workflow.py          # Workflow request/response schemas
│   ├── core/                    # Core infrastructure
│   │   ├── config.py            # Settings & environment management
│   │   ├── llm_factory.py       # Multi-provider LLM factory
│   │   ├── logging.py           # Structured logging setup
│   │   └── utils.py             # Shared utilities
│   ├── services/                # Business logic services
│   │   ├── document_parser.py   # Multi-format parsing (PDF, Email, JSON)
│   │   └── workflow_service.py  # Workflow execution orchestration
│   ├── api/routes/              # FastAPI route handlers
│   └── main.py                  # Application entry point
├── frontend/                    # Monitoring dashboard (HTML/CSS/JS)
├── knowledge_base/              # RAG source documents
│   ├── policies/                # CRM escalation policies
│   ├── examples/                # Fraud detection rules
│   └── regulations/             # Compliance guidelines
├── tests/                       # pytest test suite
├── Dockerfile                   # Container configuration
├── pyproject.toml               # Project & dependency config
├── vercel.json                  # Serverless deployment config
└── README.md
```

---

## 🚀 Setup & Installation

This project uses `uv` for lightning-fast Python package management.

### Prerequisites
- Python 3.12+
- `uv` installed (`pip install uv` or `curl -LsSf https://astral.sh/uv/install.sh | sh`)

### 1. Clone the Repository
```bash
git clone https://github.com/Pradeesh1108/multi-agent-document-intelligence-platform.git
cd multi-agent-document-intelligence-platform
```

### 2. Install Dependencies
```bash
uv sync
```

### 3. Environment Variables
Copy the example environment file and add your API keys:
```bash
cp .env.example .env
```
Edit `.env` to configure your active LLM provider (`gemini` or `groq`) and insert the respective API keys.

### 4. Run the Engine
```bash
uv run python src/main.py
```
- **API Documentation**: `http://localhost:8000/docs`
- **Monitoring Dashboard**: `http://localhost:8000`

### 5. Docker Deployment
```bash
docker build -t multi-agent-doc-intel .
docker run -p 8000:8000 --env-file .env multi-agent-doc-intel
```

---

## 👨‍💻 Author & Contributions

<div align="center">
  <a href="https://github.com/Pradeesh1108">
    <img src="https://github.com/Pradeesh1108.png" width="100px" style="border-radius: 50%;" alt="Pradeesh1108" />
  </a>
  <br>
  <strong>Built by <a href="https://github.com/Pradeesh1108">Pradeesh1108</a></strong>
</div>

<br>

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Pradeesh1108/multi-agent-document-intelligence-platform/issues) if you want to contribute to the orchestration engine.
