# Architecture Overview

Agentic Forge is built with a modern, decoupled architecture designed specifically to solve the "blocking" problem of heavy LLM inference. 

Because local LLM generation is synchronous and CPU/GPU blocking, standard web frameworks will freeze while an agent thinks. This architecture uses background threading and Server-Sent Events (SSE) to maintain a live, pulsing connection with the user interface.

## 1. The Technology Stack
*   **AI Framework:** [CrewAI](https://crewai.com) v1.12.2+ (Orchestrates the agents and tasks).
*   **LLM Router:** [LiteLLM](https://litellm.ai) (Abstracts the local LM Studio API to match OpenAI's format and provides fast 1-shot completion endpoints).
*   **Backend Server:** [FastAPI](https://fastapi.tiangolo.com) & Uvicorn (Handles HTTP routing and async generators).
*   **Frontend UI:** Vanilla HTML, CSS, and Javascript (Zero heavy frameworks, uses Shadow DOM for rendering).

## 2. Directory Structure

``` text
Agentic-AI-Fun/
├── backend/
│   ├── main.py              # The core FastAPI router, SSE generator, and Randomizer
│   └── crews/               # The isolated agentic logic pipelines
│       ├── llm_config.py    # Universal configuration for the local models
│       ├── component_crew.py # Specific agent pipeline
│       └── ...              # Other scenario definitions
├── frontend/
│   ├── index.html           # The main UI
│   ├── style.css            # Glossy, dark-mode CSS styling
│   └── app.js               # SSE listener, dynamic DOM injector, and Shadow DOM engine
├── docs/                    # This documentation folder
├── .env                     # Environment variables pointing to local servers
├── kill_uvicorn.sh          # Utility script to clean up stuck ports
└── requirements.txt         # Python dependencies
```

## 3. Data Flow: How it Works

1.  **Fast Input Randomizer (Optional):** The user clicks "Random Idea". `app.js` hits `/api/randomize`. `main.py` bypasses CrewAI and uses `litellm` directly to call the local model for a blazing-fast, 1-shot JSON generation to autofill the form.
2.  **User Request:** The user hits "Run" on the form.
3.  **JS SSE Connection:** `app.js` opens a new `EventSource` connection to the target FastAPI endpoint (e.g., `/api/teach`).
4.  **FastAPI Threading:** `main.py` intercepts the request. Because CrewAI is synchronous, `main.py` spins off the `crew.kickoff()` command into an isolated `asyncio` background thread.
5.  **Callbacks:** Inside the Crew, the agents are assigned `task_callback` functions. Every time an agent finishes a task, it deposits the raw text into an `asyncio.Queue`.
6.  **Streaming to UI:** The main thread runs a `while True` loop, yielding any data from the `Queue` directly back to the `EventSource` connection on the frontend.
7.  **Shadow DOM Interception:** If the specific scenario returns raw code (e.g., the Component scenario), `app.js` uses Regex to intercept the HTML. It automatically spins up an isolated "Shadow DOM" inside the chat bubble and renders the live CSS/HTML code, sandboxing it from ruining the main website's layout.
8.  **Termination:** Once the final task completes, FastAPI yields `null`, and the Javascript gracefully shuts down the connection.
