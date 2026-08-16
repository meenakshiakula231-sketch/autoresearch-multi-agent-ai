# Autoresearch: Multi-Agent AI Literature Review, Summarization, and Citation Mapping

Autoresearch is an automated, NLP-focused literature review system powered by a simulated multi-agent AI architecture. It retrieves academic research papers from arXiv, generates extractive summaries, synthesizes overarching thematic reports, and builds interactive visual semantic networks mapping papers, authors, and concepts.

Developed as a modern web-based application, it features a glassmorphic dashboard with live agent logs detailing individual agent operations in real time.

---

## Architecture Overview

The system uses three coordinated agents managed by a central Orchestrator:

```
                  ┌──────────────────────┐
                  │  System Orchestrator │
                  └──────────┬───────────┘
                             │
            ┌────────────────┼────────────────┐
            ▼                ▼                ▼
     ┌─────────────┐  ┌──────────────┐  ┌─────────────┐
     │ SearchAgent │  │ Summarizer   │  │ MappingAgent│
     │             │  │ Agent        │  │             │
     └──────┬──────┘  └──────┬───────┘  └──────┬──────┘
            │                │                 │
            ▼                ▼                 ▼
       [arXiv API]     [Extractive NLP]  [Cytoscape Graph]
```

1. **Search & Retrieval Agent**: Queries academic literature endpoints (arXiv). If offline or network errors occur, it gracefully falls back to a relevant pre-packaged mock database to ensure a smooth demo.
2. **Summarization Agent**: Performs extractive NLP summarization on abstracts using sentence scoring based on normalized word frequencies (TF-IDF approximation), extracts primary keyword entities, and synthesizes overall themes across retrieved papers.
3. **Citation & Mapping Agent**: Constructs semantic graphs by analyzing relationships (e.g. co-authorship, publication chronological correlations, and keyword overlaps).

---

## File Structure

```
├── backend/
│   ├── __init__.py
│   ├── agents.py       # Core Multi-Agent classes (Orchestrator, Search, Summarizer, Mapping)
│   └── main.py         # FastAPI backend server & static file routing
├── frontend/
│   ├── app.js          # Tab routing, Cytoscape graph rendering, simulated log delays
│   ├── index.html      # Main dashboard structure & layouts
│   └── style.css       # Premium glassmorphic futuristic styling
├── requirements.txt    # Python library dependencies
└── README.md           # Instructions and documentation
```

---

## Prerequisites

Ensure you have the following installed on your machine:
- **Python 3.10+** (Python 3.13 is fully supported)
- **Visual Studio Code** (VS Code)

---

## How to Execute in Visual Studio Code

Follow these step-by-step instructions to open, configure, and run the project inside VS Code:

### Step 1: Open the Project in VS Code
1. Open **VS Code**.
2. Click `File` -> `Open Folder...` from the top menu.
3. Select the project folder: `c:\Users\DELL\Desktop\New folder`.

### Step 2: Open the Integrated Terminal
1. Open the terminal inside VS Code by pressing **``Ctrl + ` ``** (Control + Backtick) or selecting `Terminal` -> `New Terminal` from the menu.

### Step 3: Set Up a Python Virtual Environment (Recommended)
Creating a virtual environment ensures that the packages are isolated to this project:
```powershell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Windows (CMD):
.\venv\Scripts\activate.bat
```
*(Once activated, you will see `(venv)` prepended to your command prompt line).*

### Step 4: Install Dependencies
Install all the required python packages using pip:
```powershell
pip install -r requirements.txt
```

### Step 5: Start the Development Server
Run the FastAPI application using Uvicorn:
```powershell
python -m uvicorn backend.main:app --reload
```
You should see output similar to this:
```text
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...] using StatReload
INFO:     Started server process [...]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 6: Access the Web Dashboard
1. Open your web browser.
2. Navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**
3. Enter keywords in the input box (e.g. `Multi-Agent System`, `RAG Systems`) or click one of the quick query buttons to execute the multi-agent literature review pipeline!
