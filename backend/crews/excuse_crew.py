from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_excuse_crew(event, task_callback, step_callback=None):
    llm = get_llm()
    
    cb1 = lambda step: step_callback("Storyteller", step) if step_callback else None
    storyteller = Agent(
        role='The Creative Storyteller',
        goal='Come up with a wild, imaginative, but semi-plausible excuse to get out of an event.',
        backstory='You are a master of tall tales. You believe the best excuses involve wild animals, sudden plagues, or acts of god.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb1
    )
    
    cb2 = lambda step: step_callback("Skeptic", step) if step_callback else None
    skeptic = Agent(
        role='The Skeptic',
        goal='Review the excuse and point out the obvious logical flaws and plot holes.',
        backstory='You are a hyper-analytical fact-checker who trusts no one. You see through lies instantly.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb2
    )
    
    cb3 = lambda step: step_callback("PR Manager", step) if step_callback else None
    pr_manager = Agent(
        role='The PR Manager',
        goal='Take the wild story and the skeptic\'s concerns, and refine it into a polished, polite, and believable text message.',
        backstory='You are an expert at crisis communication. You know how to spin any situation to make the client look like the victim of unfortunate circumstances.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb3
    )

    task1 = Task(
        description=f'Generate a completely unhinged but highly detailed excuse for getting out of this event: "{event}"',
        expected_output='A wild and elaborate story/excuse.',
        agent=storyteller,
        callback=lambda output: task_callback("Storyteller", output.raw)
    )

    task2 = Task(
        description='Read the Storyteller\'s excuse and brutally critique its believability. What are the plot holes?',
        expected_output='A critical analysis pointing out exactly why the excuse won\'t work.',
        agent=skeptic,
        callback=lambda output: task_callback("Skeptic", output.raw)
    )

    task3 = Task(
        description='Read both the original excuse and the critique. Rewrite the excuse into a smooth, polite, 3-sentence text message that smooths over the absurdity and sounds believable.',
        expected_output='A polished, ready-to-send text message.',
        agent=pr_manager,
        callback=lambda output: task_callback("PR Manager", output.raw)
    )

    crew = Crew(
        agents=[storyteller, skeptic, pr_manager],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
