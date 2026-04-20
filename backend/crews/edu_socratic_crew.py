from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_edu_socratic_crew(topic, task_callback, step_callback=None):
    llm = get_llm()
    
    professor = Agent(
        role='Expert Professor',
        goal='Give a solid, factual overview of the topic to set the baseline.',
        backstory='You are a knowledgeable but slightly dry expert who loves presenting the pure facts of a subject.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    student = Agent(
        role='Curious Student',
        goal='Read the Professor\'s overview and ask the most common "dumb" questions or point out confusing parts.',
        backstory='You are eager to learn but get confused easily by jargon. You aren\'t afraid to ask the questions everyone else is thinking.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    metaphor_maker = Agent(
        role='Metaphor Maker',
        goal='Read the student\'s confusion and provide a highly relatable, real-world analogy to make it instantly click.',
        backstory='You don\'t care about textbooks. You care about "Aha!" moments. You compare quantum physics to a bowl of soup if it helps.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'Provide a clear, factual, introductory overview of the following topic: "{topic}". Define what it is.',
        expected_output='A factual baseline explanation of the topic.',
        agent=professor,
        callback=lambda output: task_callback("Expert Professor", output.raw)
    )

    task2 = Task(
        description='Read the Professor\'s explanation. Identify the most confusing part or a common misconception. Ask 2 specific, relatable questions that a beginner would ask.',
        expected_output='A couple of probing, beginner-friendly questions about the topic.',
        agent=student,
        callback=lambda output: task_callback("Curious Student", output.raw)
    )

    task3 = Task(
        description='Read the Professor\'s facts and the Student\'s questions. Answer the student\'s questions directly by creating a brilliant, easy-to-understand real-world metaphor.',
        expected_output='A metaphor-driven explanation answering the student\'s questions.',
        agent=metaphor_maker,
        callback=lambda output: task_callback("Metaphor Maker", output.raw)
    )

    crew = Crew(
        agents=[professor, student, metaphor_maker],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
