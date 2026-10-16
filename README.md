# ⚡ StateCraft: Production-Grade Stateful Agentic Workflows with LangGraph

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![LangGraph 1.2+](https://img.shields.io/badge/LangGraph-1.2%2B-orange.svg)](https://github.com/langchain-ai/langgraph)
[![LangChain 1.4+](https://img.shields.io/badge/LangChain-1.4%2B-green.svg)](https://github.com/langchain-ai/langchain)
[![Pytest 14/14 Passing](https://img.shields.io/badge/tests-14%2F14%20passing-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**StateCraft** is an enterprise-grade learning and portfolio project demonstrating **stateful, resilient, self-healing agentic workflows** using **LangGraph** and **LangChain**.

It bridges the gap between toy linear chains and production autonomous systems by implementing:
- 🔀 **Dynamic Branching & Conditional Routing** (Intent and risk-based graph traversal)
- 🔄 **Self-Correction & Evaluator-Optimizer Loop** (AST static validation + sandboxed unit test reflection)
- 🛡️ **Resilience, Retries & Fallback Circuit** (Transient 429/503 fault tolerance with backoff & L2 cache)
- 👤 **Human-in-the-Loop (HITL) Checkpoints** (LangGraph native `interrupt()` and `Command(resume=...)` with time-travel)
- 👑 **Hierarchical Supervisor Multi-Agent Subgraphs** (Specialized Researcher, Engineer, and Auditor delegation)
- 🚀 **Flagship Enterprise Orchestrator Engine** (Autonomous software feature & security release gate)

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    START([User Ticket Ingest]) --> Triage[1. Triage & Risk Branching]
    Triage -->|Risk Assessment| Router{Risk Tier}
    
    Router -->|TIER_1: Standard| FastTrack[Standard Prep]
    Router -->|TIER_2/3: High Risk| ResilientFetch[2. Resilient SecOps Fetch<br/><i>Exponential Retries</i>]
    
    ResilientFetch --> SpecGen[3. Spec & Code Synthesis]
    FastTrack --> SpecGen
    
    SpecGen --> Evaluator[4. Evaluator-Optimizer<br/><i>AST & Unit Test Sandbox</i>]
    Evaluator -->|Fails & iter < max| SpecGen
    Evaluator -->|Passes| GovGate{Human Signoff Needed?}
    
    GovGate -->|TIER_1 Standard| Deploy[6. Production Deployment]
    GovGate -->|TIER_2/3 Elevated| Checkpoint[5. HITL Checkpoint<br/><b>interrupt()</b>]
    
    Checkpoint -->|<Human Review Decision>| Verdict{Approved?}
    Verdict -->|Approve / Edit| Deploy
    Verdict -->|Reject| Abort[Incident Aborted & Logged]
    
    Deploy --> END([Release Live in Production])
    Abort --> END
```

---

## ⚡ Quickstart

### 1. Zero-Cost Offline Mode (Default)
StateCraft includes a built-in **Deterministic Mock LLM Engine**. You can run the entire test suite, CLI, Streamlit studio, and API **100% locally with ZERO API keys or cloud costs!**

```bash
# Clone and enter repository
git clone https://github.com/subasah/statecraft-langgraph.git
cd statecraft-langgraph

# Create and activate virtual environment (using uv or standard python)
uv venv .venv
source .venv/bin/activate

# Install dependencies and statecraft package in editable mode
uv pip install -e .
```

### 2. Optional: Connect Real LLMs (OpenAI / Google Gemini)
Copy `.env.example` to `.env` and set your preferred provider:
```bash
cp .env.example .env
# Set LLM_PROVIDER=openai or LLM_PROVIDER=google
```

---

## 🛠️ The 3 Ways to Run & Showcase

### 1. Interactive Streamlit Visual Studio
Launch the browser UI to visually step through graphs, trigger human interrupts, and view live state transitions:
```bash
streamlit run streamlit_app.py
```
*Access in browser at `http://localhost:8501`*

### 2. Rich Terminal CLI
Interactive terminal with colored banners, ASCII tables, and prompt runners:
```bash
python -m statecraft.cli
# Or using the installed entry point:
statecraft
```

### 3. FastAPI REST Server
Start the production headless orchestration API:
```bash
uvicorn statecraft.api:app --reload --port 8000
```
*Interactive Swagger docs available at `http://localhost:8000/docs`*

---

## 🧪 Automated Test Suite

Run all 14 unit and integration tests verifying every pattern:
```bash
pytest tests/ -v
```
Output:
```text
tests/test_branching.py::test_branching_security PASSED                  [  7%]
tests/test_branching.py::test_branching_technical PASSED                 [ 14%]
tests/test_branching.py::test_branching_billing PASSED                   [ 21%]
tests/test_branching.py::test_branching_general_fast_path PASSED         [ 28%]
tests/test_enterprise_pipeline.py::test_enterprise_pipeline_standard_track PASSED [ 35%]
tests/test_enterprise_pipeline.py::test_enterprise_pipeline_critical_track_with_hitl_signoff PASSED [ 42%]
tests/test_human_in_the_loop.py::test_hitl_low_risk_auto_approves PASSED [ 50%]
tests/test_human_in_the_loop.py::test_hitl_high_risk_pauses_and_resumes_with_approval PASSED [ 57%]
tests/test_human_in_the_loop.py::test_hitl_resumes_with_human_edits_mutating_state PASSED [ 64%]
tests/test_resilience.py::test_resilience_flaky_service_recovers PASSED  [ 71%]
tests/test_resilience.py::test_resilience_down_service_trips_circuit_breaker PASSED [ 78%]
tests/test_self_correction.py::test_self_correction_recovers_and_passes PASSED [ 85%]
tests/test_self_correction.py::test_self_correction_bounds_iteration_limit PASSED [ 92%]
tests/test_supervisor.py::test_supervisor_orchestrates_all_specialists PASSED [100%]
============================== 14 passed in 1.19s ==============================
```

---

## 📚 Complete Documentation Catalog

- 📄 **[Interactive Web Documentation Portal](docs/index.html)**: Browser-based portal with rendered Mermaid diagrams, code walkthroughs, and an interactive state simulator.
- 📐 **[01. High-Level Architecture Guide](docs/01_HIGH_LEVEL_ARCHITECTURE.md)**: Core theory, why stateful graphs beat linear DAGs, and system trade-offs.
- 🔬 **[02. Low-Level Engineering Guide](docs/02_LOW_LEVEL_ENGINEERING.md)**: State schemas, channel reducers (`Annotated[list, append_list]`), checkpointer internals, and modern `interrupt()` mechanics.
- 📦 **[03. Reusable Patterns Catalog](docs/03_REUSABLE_PATTERNS.md)**: Deep dive into all 5 orchestration patterns, failure modes, and best practices.
- 💼 **[04. Recruiter & Interview Cheat Sheet](docs/04_RECRUITER_INTERVIEW_CHEATSHEET.md)**: 60-second elevator pitch, STAR method interview questions, and system design answers.

---

## 📁 Repository Structure

```text
├── docs/
│   ├── index.html                 # Interactive Web Documentation Portal
│   ├── 01_HIGH_LEVEL_ARCHITECTURE.md
│   ├── 02_LOW_LEVEL_ENGINEERING.md
│   ├── 03_REUSABLE_PATTERNS.md
│   └── 04_RECRUITER_INTERVIEW_CHEATSHEET.md
├── src/
│   └── statecraft/
│       ├── __init__.py
│       ├── state.py               # TypedDict schemas and append reducers
│       ├── llm.py                 # Multi-provider LLM adapter (Mock, OpenAI, Google)
│       ├── patterns/
│       │   ├── dynamic_branching.py       # Pattern 1
│       │   ├── self_correction.py         # Pattern 2
│       │   ├── resilience_retries.py      # Pattern 3
│       │   ├── human_in_the_loop.py       # Pattern 4
│       │   └── hierarchical_supervisor.py # Pattern 5
│       ├── orchestrator/
│       │   └── enterprise_pipeline.py     # Flagship Unified Engine
│       ├── cli.py                 # Rich Terminal CLI
│       └── api.py                 # FastAPI REST Endpoints
├── tests/                         # Pytest test suite (14 passing tests)
├── streamlit_app.py               # Interactive Streamlit Visual Playground
├── pyproject.toml                 # Package configuration
├── requirements.txt               # Pinned dependencies
├── Makefile                       # One-command CLI targets
└── README.md
```

---

## 💼 Recruiter Talking Points (Quick Summary)

- **Why LangGraph over standard chains?** Real reasoning is non-linear and requires cycles (Evaluator-Optimizer). LangGraph is a state machine that natively supports cyclic graphs, persistent checkpoints, and time travel.
- **How does Human-in-the-Loop work without blocking threads?** Using LangGraph 1.2+'s `interrupt()`, the graph serializes state to storage (Postgres/Redis/Memory) and yields execution immediately. When a reviewer submits a verdict via Web UI or API, `Command(resume=decision)` awakens the thread at the exact checkpoint.
- **How do you avoid infinite loops in self-correction?** State tracks both error critiques and an iteration counter. Conditional edges enforce `iterations < max_iterations`, safely diverting to human escalation if the budget is exhausted.
