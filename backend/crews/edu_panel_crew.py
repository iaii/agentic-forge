from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_edu_panel_crew(topic, task_callback, step_callback=None):
    llm = get_llm()
    
    scientist = Agent(
        role='The Scientist',
        goal='Explain the exact mechanics, math, or physical reality of how the topic works under the hood.',
        backstory='You are a hyper-logical engineer. You care about how things operate on a functional level.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    historian = Agent(
        role='The Historian',
        goal='Explain where this concept came from and the context of its discovery or origin.',
        backstory='You are an archivist who traces the lineage of ideas back to their source.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    visionary = Agent(
        role='The Visionary',
        goal='Explain why this matters for the future and its long-term societal impacts.',
        backstory='You are a futurist who looks decades ahead. You see how individual concepts reshape society.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'Break down the strict mechanics of this topic: "{topic}". How does it actually work?',
        expected_output='A strict mechanical/scientific breakdown.',
        agent=scientist,
        callback=lambda output: task_callback("The Scientist", output.raw)
    )

    task2 = Task(
        description=f'Looking at the topic "{topic}", detail its origins. Who discovered or invented it, and what was the historical context that necessitated it?',
        expected_output='A historical review of the topic\'s origins.',
        agent=historian,
        callback=lambda output: task_callback("The Historian", output.raw)
    )

    task3 = Task(
        description='Read the mechanical and historical reports. Now, write a profound summary of how this topic will shape the future of humanity in 50 years.',
        expected_output='A visionary projection of the topic\'s impact.',
        agent=visionary,
        callback=lambda output: task_callback("The Visionary", output.raw)
    )

    crew = Crew(
        agents=[scientist, historian, visionary],
        tasks=[task1, task2, task3],
        verbose=True,
        # Panel can run sequentially or we could try parallel if crewai supported it easily, but sequential is safer for narrative flow.
        process=Process.sequential 
    )
    
    return crew.kickoff()
