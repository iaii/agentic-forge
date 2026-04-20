from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_edu_escalator_crew(topic, task_callback, step_callback=None):
    llm = get_llm()
    
    kindergarten = Agent(
        role='Kindergarten Teacher',
        goal='Break the topic down to its absolute simplest, most foundational level using playful metaphors.',
        backstory='You love teaching 5-year-olds. You think everything in the universe can be explained using toys, playground analogies, and simple feelings.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    high_school = Agent(
        role='High School Tutor',
        goal='Read the simple explanation and add actual vocabulary, rules, and practical mechanics.',
        backstory='You are a cool high school tutor. You want students to understand the real terms and equations, but keep it accessible enough to pass a test.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    phd = Agent(
        role='PhD Advisor',
        goal='Take the foundation and dive into the cutting-edge, complex nuances, controversies, or future implications of the topic.',
        backstory='You are a serious, tenured professor at a top university. You demand academic rigor and want to discuss the unsolved mysteries of your field.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'Explain this topic: "{topic}" as if the reader is 5 years old. Use a fun metaphor.',
        expected_output='A highly simplified, metaphorical explanation.',
        agent=kindergarten,
        callback=lambda output: task_callback("Kindergarten Teacher", output.raw)
    )

    task2 = Task(
        description='Read the provided simple explanation. Now, rewrite and expand on it for a 16-year-old high school student. Introduce the actual scientific or historical mechanisms and proper terminology.',
        expected_output='An accessible but accurate intermediate explanation.',
        agent=high_school,
        callback=lambda output: task_callback("High School Tutor", output.raw)
    )

    task3 = Task(
        description='Read the high school explanation. Now elevate the discussion to a post-graduate level. What are the current cutting-edge debates, limitations, or deep theoretical complexities regarding this topic?',
        expected_output='A highly advanced academic breakdown of the topic.',
        agent=phd,
        callback=lambda output: task_callback("PhD Advisor", output.raw)
    )

    crew = Crew(
        agents=[kindergarten, high_school, phd],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
