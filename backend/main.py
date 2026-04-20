import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles

from backend.crews.roast_crew import run_roast_crew
from backend.crews.zombie_crew import run_zombie_crew
from backend.crews.excuse_crew import run_excuse_crew
from backend.crews.rpg_crew import run_rpg_crew
from backend.crews.time_crew import run_time_crew
from backend.crews.murder_crew import run_murder_crew
from backend.crews.edu_escalator_crew import run_edu_escalator_crew
from backend.crews.edu_socratic_crew import run_edu_socratic_crew
from backend.crews.edu_panel_crew import run_edu_panel_crew
from backend.crews.sysdesign_crew import run_sysdesign_crew
from backend.crews.component_crew import run_component_crew
from backend.crews.fitness_planner_crew import run_fitness_crew

from openai import AsyncOpenAI
import os
import json

app = FastAPI()

app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("frontend/index.html", "r") as f:
        return f.read()

async def stream_crew_output(crew_func, input_data):
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    
    def task_callback(agent_name, text):
        asyncio.run_coroutine_threadsafe(
            queue.put({"agent": agent_name, "text": text, "type": "task"}), 
            loop
        )

    def step_callback(agent_name, step_output):
        # Step outputs can be messy internal python representations,
        # so we intentionally pass to keep the UI clean across different models.
        pass

    def run_crew_sync():
        try:
            result = crew_func(input_data, task_callback, step_callback)
            final_output = str(result)
            
            asyncio.run_coroutine_threadsafe(
                queue.put({"agent": "System (Final Result)", "text": final_output, "type": "task"}), 
                loop
            )
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(
                queue.put({"agent": "Error", "text": str(e), "type": "task"}), 
                loop
            )
            asyncio.run_coroutine_threadsafe(queue.put(None), loop)

    task = loop.run_in_executor(None, run_crew_sync)
    
    while True:
        try:
            # 10 second timeout for heartbeat ping
            data = await asyncio.wait_for(queue.get(), timeout=10.0)
            if data is None:
                yield "data: null\n\n"
                break
            yield f"data: {json.dumps(data)}\n\n"
        except asyncio.TimeoutError:
            # Heartbeat to keep connection alive!
            ping_data = {"agent": "System", "text": "*Still thinking...*", "type": "ping"}
            yield f"data: {json.dumps(ping_data)}\n\n"

@app.get("/api/roast")
async def roast_endpoint(input: str = ""):
    return StreamingResponse(
        stream_crew_output(run_roast_crew, input), 
        media_type="text/event-stream"
    )

@app.get("/api/zombie")
async def zombie_endpoint(location: str = "", items: str = ""):
    data = {"location": location, "items": items}
    return StreamingResponse(
        stream_crew_output(run_zombie_crew, data), 
        media_type="text/event-stream"
    )

@app.get("/api/excuse")
async def excuse_endpoint(input: str = ""):
    return StreamingResponse(
        stream_crew_output(run_excuse_crew, input), 
        media_type="text/event-stream"
    )

@app.get("/api/rpg")
async def rpg_endpoint(input: str = ""):
    return StreamingResponse(
        stream_crew_output(run_rpg_crew, input), 
        media_type="text/event-stream"
    )

@app.get("/api/time")
async def time_endpoint(change: str = ""):
    return StreamingResponse(
        stream_crew_output(run_time_crew, change), 
        media_type="text/event-stream"
    )

@app.get("/api/murder")
async def murder_endpoint(scene: str = "", suspects: str = ""):
    data = {"scene": scene, "suspects": suspects}
    return StreamingResponse(
        stream_crew_output(run_murder_crew, data), 
        media_type="text/event-stream"
    )

@app.get("/api/teach")
async def teach_endpoint(topic: str = "", mode: str = "escalator"):
    if mode == "socratic":
        crew_func = run_edu_socratic_crew
    elif mode == "panel":
        crew_func = run_edu_panel_crew
    else:
        crew_func = run_edu_escalator_crew

    return StreamingResponse(
        stream_crew_output(crew_func, topic), 
        media_type="text/event-stream"
    )

@app.get("/api/sysdesign")
async def sysdesign_endpoint(input: str = ""):
    return StreamingResponse(
        stream_crew_output(run_sysdesign_crew, input), 
        media_type="text/event-stream"
    )

@app.get("/api/component")
async def component_endpoint(input: str = ""):
    return StreamingResponse(
        stream_crew_output(run_component_crew, input), 
        media_type="text/event-stream"
    )

@app.get("/api/fitness")
async def fitness_endpoint(input: str = ""):
    return StreamingResponse(
        stream_crew_output(run_fitness_crew, input),
        media_type="text/event-stream"
    )

import random

@app.get("/api/randomize")
async def randomize_endpoint(scenario: str = ""):
    teach_domains = ["World History", "Photography", "Astronomy", "Philosophy", "Classical Art", "Culinary Arts", "Marine Biology", "Psychology", "Music Theory", "Architecture", "Economics", "Linguistics", "Literature"]
    sysdesign_types = ["enterprise architecture like Netflix", "a highly scalable casual multiplayer game", "a real-time social media feed", "a globally distributed ride-sharing app", "a massive virtual pet simulator"]
    
    instructions = {
        "roast": "Generate a realistic but slightly flawed startup idea that a typical first-time founder might pitch. Keep it under 10 words. Output JSON with key 'input'.",
        "zombie": "Generate a realistic, everyday location and 3 common, mundane pocket items for a theoretical disaster survival scenario. Output JSON with keys 'location' and 'items'.",
        "excuse": "Generate a highly relatable, tedious professional or personal event that someone would casually want to skip. Output JSON with key 'input'.",
        "rpg": "Generate a serious, grounded concept for a classic fantasy tabletop character with a compelling motivation. Output JSON with key 'input'.",
        "time": "Generate a serious, grounded historical 'What If' scenario that would drastically alter the course of modern history. Output JSON with key 'change'.",
        "murder": "Generate a realistic, grounded police-procedural crime scene and a list of 3 plausible suspects. Output JSON with keys 'scene' and 'suspects'.",
        "teach": f"Generate a highly specific, fascinating learning topic entirely focused on the domain of {random.choice(teach_domains)}. Output JSON with key 'topic'.",
        "sysdesign": f"Generate a technical system design question specifically asking to design {random.choice(sysdesign_types)}. Output JSON with key 'input'.",
        "component": "Generate a realistic request for a modern, sleek UI web component commonly used in professional SaaS dashboards. Output JSON with key 'input'.",
        "fitness": "Generate a realistic fitness plan to help the user achieve their fitness goal based on their requirements. Output JSON with key 'input'."
    }
    
    examples = {
        "roast": '{"input": "A food delivery app exclusively for late-night breakfast food"}',
        "zombie": '{"location": "A typical suburban grocery store", "items": "A set of car keys, a smartphone with 12% battery, and a half-empty water bottle"}',
        "excuse": '{"input": "A mandatory out-of-state corporate team-building retreat on a weekend"}',
        "rpg": '{"input": "A veteran Human Paladin seeking redemption after failing to protect their liege"}',
        "time": '{"change": "What if the Library of Alexandria never burned down?"}',
        "murder": '{"scene": "A wealthy CEO found poisoned in his locked penthouse office", "suspects": "His business partner, his estranged wife, and his private accountant"}',
        "teach": '{"topic": "The physiological and psychological impact of lighting in portrait photography"}',
        "sysdesign": '{"input": "Design a globally distributed backend for a real-time multiplayer virtual pet simulator"}',
        "component": '{"input": "A responsive, minimalist sidebar navigation menu with a dark mode toggle"}',
        "fitness": '{"input": "I want to lose 10lbs in the next 2 months. I am a vegetarian 23y/o woman weighing 230lbs"}'
    }

    instruction = instructions.get(scenario, "Generate a creative text input.")
    example = examples.get(scenario, '{"input": "Example text"}')
    
    full_prompt = f"Goal: {instruction}\n\nHere is an example to show you the VIBE and exact JSON structure you MUST output. Do not copy the idea, hallucinate a completely new, highly creative value:\n{example}\n\nWARNING: Output ONLY strict valid raw JSON. Do not include markdown formatting, backticks, or conversational text. Start directly with {{."

    try:
        client = AsyncOpenAI(
            base_url=os.environ.get("OPENAI_API_BASE", "http://localhost:1234/v1"),
            api_key=os.environ.get("OPENAI_API_KEY", "lm-studio")
        )
        
        response = await client.chat.completions.create(
            model=os.environ.get("OPENAI_MODEL_NAME", "local-model"),
            messages=[
                {"role": "system", "content": "You are a helpful JSON generator. Output only valid JSON based on the user's requested structure."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.9,
            max_tokens=200
        )
        content = response.choices[0].message.content.strip()
        
        # Clean markdown if model hallucinated it
        if content.startswith('```json'):
            content = content[7:]
        if content.endswith('```'):
            content = content[:-3]
        return json.loads(content)
    except Exception as e:
        print(f"Randomize failed: {e}")
        return json.loads(example)
