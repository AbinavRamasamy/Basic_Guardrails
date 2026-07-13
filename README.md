# LangGraph RAG System

A local document Retrieval-Augmented Generation (RAG) sandbox that searches local `.txt` documents for relevant context, guarded by a linear validation pipeline built with **LangGraph**.

---

## Architecture Overview

This project uses a linear state graph to check user queries, retrieve context, and redact sensitive leaks:

```
[START] ──> check_keywords ──> check_constraints ──> retrieve_context ──> generate_response ──> check_leaks ──> evaluate_overall ──> [END]
```

### Active Guardrails
1. **Prohibited Keyword Blocker**: Rejects queries containing administrative keywords (`admin`, `root`, `sudo`, `hack`, `override`).
2. **Input Constraints**: Blocks queries exceeding 100 characters in length or containing HTML/JSX brackets (`[`, `]`, `<`, `>`).
3. **Sensitive Pattern Leak Blocker**: Scans the retrieved file context for Social Security Numbers (SSN) and Credit Card numbers, redacting them before display.

---

## File Structure

* **`api/workflow.py`**: Compiles the LangGraph StateGraph, defines nodes (`check_keywords`, `retrieve_context`, etc.), and handles local file parsing.
* **`api/index.py`**: Exposes FastAPI endpoints (serving Vercel serverless functions).
* **`data/`**: Houses local text knowledge bases (`tasks.txt` and `policies.txt`).
* **`src/`**: React Vite frontend source code.
* **`basic_guardrails.ipynb`**: Interactive Jupyter Notebook demonstrating graph execution.

---

## Local Setup

### Prerequisites
* Python 3.10+
* Node.js 18+

### 1. Run Python Backend
Navigate to the root folder of this project:
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/env/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn api.index:app --reload --port 8000
```

### 2. Run Frontend
In a new terminal window:
```bash
# Install dependencies
npm install

# Start Vite React server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Jupyter Notebook
To run the interactive notebook demo:
```bash
jupyter notebook basic_guardrails.ipynb
```
The notebook imports the compiled graph directly from `api.workflow` to run validation trace test cases interactively.
