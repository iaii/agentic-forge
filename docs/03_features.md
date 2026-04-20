# Scenarios & Features

The platform currently supports 9 radically different multi-agent pipelines designed to demonstrate different emergent behaviors of Agentic AI, plus powerful global platform features.

## Global Platform Features

### The LLM Randomizer
Instead of struggling to think of prompts, every scenario includes a 🎲 **Random Idea** button. When pressed, the backend hits LM Studio directly with a 1-shot fast completion request (bypassing the slow CrewAI pipeline). It hallucinates a bizarre, highly creative JSON payload tailored *specifically* for that scenario and auto-fills your UI inputs instantly.

### Shadow DOM Live Rendering
For scenarios that output code (like the Micro-Component Forge), the javascript engine automatically detects markdown blocks containing ````html ... ````. It extracts the code and physically builds an isolated Shadow DOM inside the chat interface, allowing you to visually interact with the AI-generated UI component live in the browser without its CSS bleeding out and ruining the master website styling.

---

## Agentic Scenarios

### 1. Startup Roaster (`roast_crew.py`)
**Demonstrates:** Critical Debate and Assessment
*   **Input:** A wild startup idea.
*   **The Agents:** A Hyper-Optimistic Visionary, a Brutally Honest Investor, and a Confused Consumer.

### 2. Zombie Survival (`zombie_crew.py`)
**Demonstrates:** Tactical Planning & Constraint Satisfaction
*   **Input:** A specific location and a random list of pocket items.
*   **The Agents:** The Scout, The Quartermaster, and The Tactician.

### 3. Excuse Generator (`excuse_crew.py`)
**Demonstrates:** Creative Refinement and Fact-Checking
*   **Input:** An event you desperately want to get out of.
*   **The Agents:** The Storyteller (invents), The Skeptic (finds plot holes), and The PR Manager (writes the text message).

### 4. RPG Backstory Forge (`rpg_crew.py`)
**Demonstrates:** Narrative Collaboration
*   **Input:** A basic, one-sentence D&D character concept.
*   **The Agents:** The Genealogist, The Psychologist, and The Chronicler.

### 5. Time Travel Butterfly Effect (`time_crew.py`)
**Demonstrates:** Extrapolation and Consequence Mapping
*   **Input:** A historical paradox or change.
*   **The Agents:** The Historian, The Chaos Theorist, and The Future Chronicler.

### 6. Unsolved Murder Mystery (`murder_crew.py`)
**Demonstrates:** Deductive Reasoning
*   **Input:** A chaotic crime scene and a list of odd suspects.
*   **The Agents:** The CSI Tech, The Profiler, and The Hardboiled Detective.

### 7. AI Masterclass (`edu_*_crew.py`)
**Demonstrates:** Dynamic Tool Routing and Pedagogical Styles
*   **Input:** ANY educational topic, and a choice of 3 teaching styles (Escalator, Socratic, or Panel).
*   **The Agents:** Ranges from Kindergarten Teachers to PhDs depending on the dropdown selection!

### 8. System Design (`sysdesign_crew.py`)
**Demonstrates:** Architectural Planning without Code Bloat
*   **Input:** A wild concept for a new software application.
*   **The Agents:** The Product Manager (strips it down to 3 MVP points), The Software Architect (picks the structural tech stack), and the QA/Security Hacker (tears the architecture apart for severe vulnerabilities).

### 9. Micro-Component Forge (`component_crew.py`)
**Demonstrates:** Software Engineering and Live Rendering
*   **Input:** A request for a specific, tiny UI element (e.g. a glossy button).
*   **The Agents:** The UI Designer (specs the aesthetic rules), The Junior Developer (writes the raw HTML/CSS), and the strict Senior Code Reviewer (fixes the bugs and packages it securely so the frontend Shadow DOM can render it live).
