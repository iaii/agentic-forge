from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_roast_crew(startup_idea, task_callback, step_callback=None):
    llm = get_llm()
    
    cb1 = lambda step: step_callback("Visionary", step) if step_callback else None
    visionary = Agent(
        role='Hyper-Optimistic Visionary',
        goal='Find the hidden billion-dollar potential in any startup idea.',
        backstory='You have funded 10 unicorns and believe even the worst ideas are genius. Your enthusiasm is boundless and often irrational.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb1
    )
    
    cb2 = lambda step: step_callback("Investor", step) if step_callback else None
    investor = Agent(
        role='Brutally Honest Investor',
        goal='Tear down the startup idea with realistic unit economics and harsh market truths.',
        backstory='You are a cynical venture capitalist who has seen thousands of companies fail. You hate buzzwords and focus on why things will not work.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb2
    )
    
    cb3 = lambda step: step_callback("Consumer", step) if step_callback else None
    consumer = Agent(
        role='Confused Consumer',
        goal='Evaluate if a normal person would actually use this product.',
        backstory='You are an average, slightly tech-illiterate person who just wants apps to be simple. You get easily confused by complex ideas and just want to know how it helps your daily life.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb3
    )

    task1 = Task(
        description=f'Analyze this startup idea and explain why it is the next big thing: "{startup_idea}"',
        expected_output='A highly enthusiastic endorsement of the idea, imagining absurdly optimistic market caps.',
        agent=visionary,
        callback=lambda output: task_callback("Visionary", output.raw)
    )

    task2 = Task(
        description='Read the Visionary\'s pitch and brutally roast the idea. Explain the terrible unit economics, the lack of market need, and why it will fail.',
        expected_output='A harsh, cynical breakdown of why the idea is terrible.',
        agent=investor,
        callback=lambda output: task_callback("Investor", output.raw)
    )

    task3 = Task(
        description='Read the previous arguments. Give your final confused take on whether you would actually download or buy this thing.',
        expected_output='A confused, everyday person\'s perspective on the product.',
        agent=consumer,
        callback=lambda output: task_callback("Consumer", output.raw)
    )

    crew = Crew(
        agents=[visionary, investor, consumer],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
