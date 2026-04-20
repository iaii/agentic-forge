from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_rpg_crew(character_prompt, task_callback, step_callback=None):
    llm = get_llm()
    
    cb1 = lambda step: step_callback("Genealogist", step) if step_callback else None
    genealogist = Agent(
        role='The Genealogist',
        goal='Create a deep ancestral and geographical background for the character.',
        backstory='You are a master lore-keeper. You understand how where someone comes from shapes who they are.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb1
    )
    
    cb2 = lambda step: step_callback("Psychologist", step) if step_callback else None
    psychologist = Agent(
        role='The Psychologist',
        goal='Analyze the background to define the character\'s core flaw, fear, and ultimate motivation.',
        backstory='You are an expert in character arcs and trauma. You know exactly what makes a hero tick...',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb2
    )
    
    cb3 = lambda step: step_callback("Chronicler", step) if step_callback else None
    chronicler = Agent(
        role='The Chronicler',
        goal='Write a cinematic, gripping prologue summarizing the character\'s origins and current mission.',
        backstory='You are an epic fantasy author. You take raw facts and spin them into gold.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb3
    )

    task1 = Task(
        description=f'Establish the hometown, family, and childhood events for this character: "{character_prompt}"',
        expected_output='A detailed summary of the character\'s early life and geography.',
        agent=genealogist,
        callback=lambda output: task_callback("Genealogist", output.raw)
    )

    task2 = Task(
        description='Based on the Genealogist\'s report, what is this character\'s greatest fear, their fatal flaw, and their true motivation?',
        expected_output='A psychological profile of the character.',
        agent=psychologist,
        callback=lambda output: task_callback("Psychologist", output.raw)
    )

    task3 = Task(
        description='Read the previous reports. Write a 2-paragraph cinematic prologue introducing this character on the first day of their adventure.',
        expected_output='An epic, narrative prologue chapter.',
        agent=chronicler,
        callback=lambda output: task_callback("Chronicler", output.raw)
    )

    crew = Crew(
        agents=[genealogist, psychologist, chronicler],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
