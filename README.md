<div align="center">
  <h1>🚀 Multi-Agent Document Workflow Orchestration System</h1>
  <p>An enterprise-grade AI automation engine that processes incoming business documents and routes them through autonomous decision pipelines.</p>

  <!-- Tech Stack Badges -->
  <p>
    <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
    <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
    <img src="https://img.shields.io/badge/LangGraph-000000?style=for-the-badge&logo=python&logoColor=white" alt="LangGraph" />
    <img src="https://img.shields.io/badge/ChromaDB-1D2939?style=for-the-badge&logo=database&logoColor=white" alt="ChromaDB" />
    <img src="https://img.shields.io/badge/Groq-F55036?style=for-the-badge&logo=groq&logoColor=white" alt="Groq" />
  </p>
</div>

---

## 📖 The Vision: Beyond a Web Dashboard

Many AI projects treat the website as the product. **This project does not.**

In the real world, no employee sits at a dashboard to manually upload PDFs and wait for a progress bar. Instead, documents arrive continuously via email, API calls, or ERP webhooks. 

This project is a true **Backend Workflow Automation Engine**. 

The included frontend is strictly a **Workflow Simulation Dashboard**—a tool designed for developers and operations teams to test, debug, and monitor how the AI orchestrates real-time data flows.

### Real World Implementation Flow

This engine is designed to sit invisibly in the background of an enterprise infrastructure:

```text
External System (Email / ERP / Webhook)
      ↓
POST /documents/process
      ↓
LangGraph Multi-Agent Workflow
      ↓
AI Extracts Data, Checks RAG, Assesses Risk
      ↓
Automated Decision Executed
      ↓
Ticket Created in CRM / Sales Team Notified
```

---

## 🧠 System Architecture & Agent Flow

The core of the system is a 7-node autonomous agent pipeline built on **LangGraph**. Each agent has a specific, isolated responsibility.

```mermaid
flowchart TD
    %% Nodes
    In([Incoming Document])
    Intake(Intake Agent)
---
config:
  flowchart:
    curve: linear
---
graph TD;
	__start__([<p>__start__</p>]):::first
	intake(intake)
	intent(intent)
	extraction(extraction)
	knowledge(knowledge)
	risk(risk)
	decision(decision)
	action(action)
	__end__([<p>__end__</p>]):::last
	__start__ --> intake;
	decision --> action;
	extraction --> knowledge;
	intake --> intent;
	intent --> extraction;
	knowledge --> risk;
	risk --> decision;
	action --> __end__;
	classDef default fill:#f2f0ff,line-height:1.2
	classDef first fill-opacity:0
	classDef last fill:#bfb6fc
```

### Agent Responsibilities
1. **Intake Agent**: Cleans and normalizes incoming payloads (Email, PDF, JSON).
2. **Intent Agent**: Classifies the document (e.g., RFQ, Complaint, Invoice, Fraud Risk).
3. **Extraction Agent**: Dynamically selects a Pydantic schema based on intent and extracts strict, type-safe entities.
4. **Knowledge Agent**: Contextualizes the document against corporate policies using ChromaDB.
5. **Risk Agent**: Assigns a risk score and flags urgent or suspicious activities.
6. **Decision Agent**: Determines the next best action based on the aggregate data.
7. **Action Agent**: Interfaces with external tools (Mock CRM, Email Server) to execute the final decision.

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
- **Workflow Simulator (Frontend)**: `http://localhost:8000`

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
