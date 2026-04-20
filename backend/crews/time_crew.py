from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_time_crew(change_prompt, task_callback, step_callback=None):
    llm = get_llm()
    
    historian = Agent(
        role='The Historian',
        goal='Establish the exact historical context and how the change disrupts the immediate timeline.',
        backstory='You are a meticulous professor of world history. You understand exactly what was happening at any given moment in the past and how delicate the timeline is.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    chaos = Agent(
        role='The Chaos Theorist',
        goal='Extrapolate wildly out-of-control chain reactions based on the historian\'s timeline disruption.',
        backstory='You are a brilliant mathematician obsessed with the butterfly effect. You know that stepping on a bug in 1900 leads to the moon being blown up in 1950.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    chronicler = Agent(
        role='The Future Chronicler',
        goal='Describe the final, bizarre dystopian or utopian reality of the year 2500 resulting from these ripples.',
        backstory='You are a mysterious traveler from the year 2500, forced to live in whatever timeline is created. You narrate the state of the world.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'Analyze this theoretical change to history: "{change_prompt}". Describe what the exact historical context was and how this precise change alters the immediate following 5 years.',
        expected_output='A factual, historical breakdown of the immediate timeline disruption.',
        agent=historian,
        callback=lambda output: task_callback("Historian", output.raw)
    )

    task2 = Task(
        description='Read the Historian\'s report. Calculate the butterfly effect. Describe how this seemingly small historical shift cascades into massive, unpredictable societal and global changes over the next 100 years.',
        expected_output='A wild but statistically reasoned chain reaction of historical events.',
        agent=chaos,
        callback=lambda output: task_callback("Chaos Theorist", output.raw)
    )

    task3 = Task(
        description='Read the timeline changes from the Chaos Theorist. Fast forward to the year 2500. Write a 2-paragraph cinematic summary describing the bizarre dystopia or utopia that humanity now lives in as a direct result.',
        expected_output='A cinematic vision of the year 2500.',
        agent=chronicler,
        callback=lambda output: task_callback("Future Chronicler", output.raw)
    )

    crew = Crew(
        agents=[historian, chaos, chronicler],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
