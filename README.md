# Agentic Forge

A multi-agent AI playground built with CrewAI and FastAPI. Pick a scenario, provide a prompt, and watch specialized agents collaborate sequentially — each reading the previous agent's output — streamed live to the browser via Server-Sent Events.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser                                │
│                                                                 │
│  ┌─────────────┐   form submit    ┌────────────────────────┐   │
│  │  Scenario   │ ──────────────▶  │    EventSource (SSE)   │   │
│  │  Hub (UI)   │                  │  GET /api/<scenario>   │   │
│  └─────────────┘                  └───────────┬────────────┘   │
│                                               │ stream events  │
│  ┌────────────────────────────────────────────▼────────────┐   │
│  │                    Chat Panel                           │   │
│  │  Agent 1 msg (collapsed) │ Agent 2 msg │ Final result   │   │
│  └────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP GET + SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     FastAPI (backend/main.py)                   │
│                                                                 │
│  stream_crew_output()                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  asyncio.Queue  ◀──── task_callback (thread-safe put)    │  │
│  │                                                          │  │
│  │  loop.run_in_executor(None, run_crew_sync)               │  │
│  │    └── crew_func(input, task_callback, step_callback)    │  │
│  │                                                          │  │
│  │  queue.get(timeout=10s) ──▶ yield SSE event              │  │
│  │  TimeoutError            ──▶ yield heartbeat ping        │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CrewAI (backend/crews/)                        │
│                                                                 │
│  Crew(process=Process.sequential)                               │
│                                                                 │
│  Agent 1 ──task_callback──▶ queue                               │
│     │ (output fed as context)                                   │
│  Agent 2 ──task_callback──▶ queue                               │
│     │                                                           │
│  Agent 3 ──task_callback──▶ queue ──▶ Final result ──▶ queue    │
│                                                                 │
│  Each agent backed by crewai.LLM (LiteLLM-routed, OpenAI API)  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌──────────────────────────────────────┐
│   LLM Backend (via llm_config.py)    │
│                                      │
│   LM Studio  localhost:1234/v1       │
│   — OR —                             │
│   OpenAI API  api.openai.com/v1      │
│   — OR —                             │
│   Any OpenAI-compatible endpoint     │
│                                      │
│   Model prefixed openai/<name>       │
│   for LiteLLM routing                │
└──────────────────────────────────────┘
```

### Key design decisions

**Sync crew in a thread pool** — CrewAI's `crew.kickoff()` is synchronous. Running it in `loop.run_in_executor(None, ...)` keeps FastAPI's async event loop unblocked so the SSE stream can flush events as they arrive.

**Queue + `asyncio.run_coroutine_threadsafe`** — Each crew's `task_callback` is invoked from the thread pool thread. `run_coroutine_threadsafe` safely enqueues the message onto the main event loop's `asyncio.Queue`, which the SSE generator then drains.

**Heartbeat ping at 10s** — `queue.get(timeout=10.0)` raises `TimeoutError` when an agent is thinking. A `{"type":"ping"}` event is emitted to prevent the browser's SSE connection from timing out on slow models.

**`step_callback` intentionally dropped** — CrewAI step callbacks expose raw Python object representations (tool calls, intermediate thoughts). These are suppressed to keep the UI clean; only `task_callback` (completed agent outputs) surfaces in the UI.

**Sequential process with context propagation** — Tasks are run with `Process.sequential`. Later tasks pass `context=[task1, task2, ...]` so each agent's LLM call includes prior agents' outputs as grounding context.

**Shadow DOM for component rendering** — The Micro-Component scenario extracts HTML from the agent's markdown code fence and injects it into a `attachShadow({mode:'open'})` element, isolating the generated styles from the host page.

---

## Streaming Protocol

```
Client                          Server
  │                               │
  │  GET /api/roast?input=...     │
  │ ──────────────────────────▶  │
  │                               │  run_crew_sync() in executor
  │  data: {"agent":"Visionary",  │  ◀── task_callback fires
  │          "text":"...",        │
  │          "type":"task"}       │
  │ ◀──────────────────────────  │
  │                               │  (agent 2 thinking, >10s)
  │  data: {"agent":"System",     │
  │          "text":"*Still...*", │
  │          "type":"ping"}       │
  │ ◀──────────────────────────  │
  │                               │  ◀── task_callback fires
  │  data: {"agent":"Investor",   │
  │          "text":"...",        │
  │          "type":"task"}       │
  │ ◀──────────────────────────  │
  │                               │
  │  data: null                   │  sentinel — crew finished
  │ ◀──────────────────────────  │
  │                               │
  │  [EventSource closed]         │
```

The frontend distinguishes three event shapes:
- `type: "task"` — render agent message bubble
- `type: "ping"` — update typing indicator text only
- `data: null` — close `EventSource`, re-enable Run button

---

## LLM Configuration (`backend/crews/llm_config.py`)

All crews share a single `get_llm()` factory. It reads three env vars and returns a `crewai.LLM` instance backed by LiteLLM:

```python
LLM(
    model="openai/<OPENAI_MODEL_NAME>",   # openai/ prefix forces LiteLLM OpenAI routing
    base_url=OPENAI_API_BASE,             # any OpenAI-compatible endpoint
    api_key=OPENAI_API_KEY,
    temperature=0.7,
    max_tokens=1500
)
```

Model names are automatically prefixed with `openai/` if not already present, so LiteLLM routes them through the OpenAI-compatible path regardless of actual provider.

---

## Scenarios & Agent Crews

Each scenario is a self-contained file in `backend/crews/`. All follow the same pattern: instantiate agents with role/goal/backstory, define tasks with callbacks, assemble a `Crew`, call `kickoff()`.

| Scenario | Endpoint | Agents | Task flow |
|---|---|---|---|
| Startup Roaster | `GET /api/roast?input=` | Hyper-Optimistic Visionary · Brutally Honest Investor · Confused Consumer | Sequential pitch → roast → consumer reaction |
| Zombie Survival | `GET /api/zombie?location=&items=` | Scout · Quartermaster · Tactician | Recon → resource improvisation → action plan |
| Excuse Generator | `GET /api/excuse?input=` | Storyteller · Skeptic · PR Manager | Draft excuse → stress-test it → polish delivery |
| RPG Backstory | `GET /api/rpg?input=` | Genealogist · Psychologist · Chronicler | Heritage → trauma/motivation → narrative backstory |
| Time Travel | `GET /api/time?change=` | Historian · Chaos Theorist · Future Chronicler | Historical grounding → butterfly effects → alternate timeline |
| Murder Mystery | `GET /api/murder?scene=&suspects=` | CSI Forensic Tech · Psychological Profiler · Hardboiled Detective | Evidence → motive profiling → accusation |
| AI Masterclass | `GET /api/teach?topic=&mode=` | Mode-dependent (see below) | Progressive explanation |
| System Design | `GET /api/sysdesign?input=` | Product Manager · Architect · Security Expert | Requirements → architecture → threat model |
| Micro-Component | `GET /api/component?input=` | UI Designer · Frontend Developer | Design spec → raw HTML/CSS (live-rendered via Shadow DOM) |
| Fitness Planner | `GET /api/fitness?input=` | Nutritionist · Personal Trainer · Fitness Coach | Macro/meal plan → workout program → integrated lifestyle plan |

### AI Masterclass modes (`?mode=`)

| Mode | Agents | Approach |
|---|---|---|
| `escalator` (default) | Kindergarten Teacher · High School Tutor · PhD Advisor | Same topic explained at increasing complexity |
| `socratic` | Debate Coach + Students | Socratic questioning and classroom debate |
| `panel` | Domain Experts | Multidisciplinary panel breakdown |

### Randomize endpoint

`GET /api/randomize?scenario=<key>` calls the LLM directly (no crew) with a scenario-specific prompt at `temperature=0.9`, returning a JSON object whose keys match the scenario's form field IDs. Falls back to a hardcoded example if the LLM call fails.

---

## API Reference

| Method | Path | Query params | Response |
|---|---|---|---|
| GET | `/api/roast` | `input` | SSE stream |
| GET | `/api/zombie` | `location`, `items` | SSE stream |
| GET | `/api/excuse` | `input` | SSE stream |
| GET | `/api/rpg` | `input` | SSE stream |
| GET | `/api/time` | `change` | SSE stream |
| GET | `/api/murder` | `scene`, `suspects` | SSE stream |
| GET | `/api/teach` | `topic`, `mode` | SSE stream |
| GET | `/api/sysdesign` | `input` | SSE stream |
| GET | `/api/component` | `input` | SSE stream |
| GET | `/api/fitness` | `input` | SSE stream |
| GET | `/api/randomize` | `scenario` | JSON |

All SSE endpoints return `Content-Type: text/event-stream`. Each `data:` line is a JSON object `{"agent": string, "text": string, "type": "task" | "ping"}`, terminated by `data: null`.

---

## Project Structure

```
agentic-ai-fun/
├── backend/
│   ├── main.py                    # FastAPI app, SSE streaming, crew orchestration
│   └── crews/
│       ├── llm_config.py          # Shared LLM factory (LiteLLM via crewai.LLM)
│       ├── roast_crew.py
│       ├── zombie_crew.py
│       ├── excuse_crew.py
│       ├── rpg_crew.py
│       ├── time_crew.py
│       ├── murder_crew.py
│       ├── edu_escalator_crew.py
│       ├── edu_socratic_crew.py
│       ├── edu_panel_crew.py
│       ├── sysdesign_crew.py
│       ├── component_crew.py
│       └── fitness_planner_crew.py
├── frontend/
│   ├── index.html                 # Single-page app shell
│   └── app.js                    # Scenario config, SSE client, rendering
├── requirements.txt
└── .env                           # Not committed — configure locally
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI + Uvicorn (ASGI) |
| Multi-agent orchestration | CrewAI |
| LLM routing | LiteLLM (via `crewai.LLM`) |
| LLM provider | OpenAI API or any OpenAI-compatible endpoint |
| Local inference | LM Studio (`localhost:1234/v1`) |
| Streaming | Server-Sent Events (`text/event-stream`) |
| Frontend | Vanilla JS, HTML5, CSS3 |

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure `.env`

```env
# Local inference (LM Studio default):
OPENAI_API_KEY=lm-studio
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_MODEL_NAME=local-model

# OpenAI:
OPENAI_API_KEY=sk-...
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL_NAME=gpt-4o
```

### 3. Start the server

```bash
uvicorn backend.main:app --reload
```

The app is served at `http://localhost:8000`. The frontend is mounted from `frontend/` as a static directory; `GET /` returns `index.html`.

### Local inference with LM Studio

Download [LM Studio](https://lmstudio.ai), load any instruction-tuned model, and start the local server on port `1234`. The default `.env` values point there with no further config needed.

---

## License

MIT
