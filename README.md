# Agentic Forge

An interactive web app that showcases multi-agent AI collaboration. Pick a scenario, provide a prompt, and watch multiple AI agents with distinct personalities work together in real-time to produce richer, more nuanced outputs than any single model could alone.

Built with [CrewAI](https://crewai.com), FastAPI, and vanilla JavaScript. Streams agent responses live via Server-Sent Events.

![Demo](docs/demo.gif)

---

## Scenarios

| Scenario | Agents | What it does |
|---|---|---|
| **Startup Roaster** | Visionary · Investor · Consumer | Three agents debate your startup idea from wildly different angles |
| **Zombie Survival** | Scout · Quartermaster · Tactician | Plans a 48-hour apocalypse escape from your current location |
| **Excuse Generator** | Storyteller · Skeptic · PR Manager | Collaboratively crafts the most believable excuse possible |
| **RPG Forge** | Genealogist · Psychologist · Chronicler | Builds a rich fantasy character backstory |
| **Time Travel** | Historian · Chaos Theorist · Future Chronicler | Explores "what if" historical scenarios and their ripple effects |
| **Murder Mystery** | Forensic Tech · Psychological Profiler · Detective | Solves a crime scene with forensic, psychological, and noir flair |
| **AI Masterclass — Escalator** | Kindergarten Teacher · High School Tutor · PhD Advisor | Explains any topic at three levels of depth |
| **AI Masterclass — Socratic** | Debate Coach · Students | Teaches through Socratic questioning and debate |
| **AI Masterclass — Panel** | Domain Experts | Multidisciplinary expert panel breaks down a topic |
| **System Design** | PM · Architect · Security Expert | Architects a virtual system end-to-end |
| **Micro-Component** | Designer · Developer | Generates a live-rendered HTML/CSS UI component |
| **Fitness Planner** | Nutritionist · Personal Trainer · Coach | Creates a full fitness and meal plan tailored to your goals |

The **Randomize** button uses AI to generate creative scenario inputs so you can explore without thinking of prompts yourself.

---

## Tech Stack

- **Backend** — Python, FastAPI, Uvicorn
- **AI Orchestration** — CrewAI + LangChain-OpenAI
- **LLM** — OpenAI API or any OpenAI-compatible endpoint (e.g. LM Studio for local inference)
- **Streaming** — Server-Sent Events via `sse-starlette`
- **Frontend** — Vanilla JS, HTML5, CSS3 (no framework)

---

## Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
# For local inference with LM Studio:
OPENAI_API_KEY=lm-studio
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_MODEL_NAME=local-model

# For OpenAI:
# OPENAI_API_KEY=sk-...
# OPENAI_API_BASE=https://api.openai.com/v1
# OPENAI_MODEL_NAME=gpt-4o
```

### 3. Start the server

```bash
uvicorn backend.main:app --reload
```

### 4. Open the app

Visit [http://localhost:8000](http://localhost:8000), select a scenario, fill in the inputs (or hit Randomize), and watch the agents go.

---

## Local LLM (LM Studio)

The default config points to LM Studio running on `localhost:1234`. Download [LM Studio](https://lmstudio.ai), load any model, start the local server, and you're good to go — no API key required.

---

## Project Structure

```
agentic-ai-fun/
├── backend/
│   ├── main.py              # FastAPI app, SSE endpoints, crew orchestration
│   └── crews/               # One file per scenario crew
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
│   ├── index.html
│   └── app.js
├── requirements.txt
└── .env                     # Not committed — see above
```

---

## How It Works

1. The frontend sends the user's inputs to a FastAPI endpoint (e.g. `/api/roast`).
2. The backend instantiates a CrewAI crew and runs tasks sequentially in a thread pool so the async server stays non-blocking.
3. Each agent's output is streamed back to the browser via SSE as it completes.
4. The frontend renders each agent's message in real-time, color-coded by agent, with collapsible intermediate steps and a final system output.

---

## License

MIT
