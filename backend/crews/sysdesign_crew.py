from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_sysdesign_crew(app_idea, task_callback, step_callback=None):
    llm = get_llm()
    
    pm = Agent(
        role='Product Manager',
        goal='Break the wildly abstract app idea down into exactly 3 core MVP (Minimum Viable Product) features.',
        backstory='You are a hyper-focused PM who hates feature creep. You strip out all the nonsense and distill wild ideas into actionable, buildable products.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    architect = Agent(
        role='Software Architect',
        goal='Define the strict technical stack (frontend, backend, database) and draw a high-level logical architecture.',
        backstory='You are a veteran systems engineer. You don\'t write code, you draw the blueprints of scalable systems.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    security = Agent(
        role='Security & QA Expert',
        goal='Red-team the architecture and point out glaring security flaws or absurd edge cases.',
        backstory='You are a paranoid white-hat hacker. You see exactly how systems will break, crash, or get exploited by malicious actors.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    cto = Agent(
        role='Principal Architect (CTO)',
        goal='Finalize the design by patching the vulnerabilities found by the Security Expert.',
        backstory='You are the decisive CTO. You listen to your architect and your security hacker, resolve their conflicts, and declare the ultimate, bulletproof tech stack.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'Analyze this app concept: "{app_idea}". Distill it into exactly 3 MVP features required to make it work.',
        expected_output='A strict list of 3 core MVP features.',
        agent=pm,
        callback=lambda output: task_callback("Product Manager", output.raw)
    )

    task2 = Task(
        description='Read the PM\'s MVP features. Design a modern Software Architecture (languages, frameworks, DBs) to support this. Describe the data flow.',
        expected_output='A high-level technical architecture and data flow document.',
        agent=architect,
        callback=lambda output: task_callback("Software Architect", output.raw)
    )

    task3 = Task(
        description='Read the proposed architecture. Tear it apart. What are the severe security flaws or edge cases that make this app concept dangerous or absurd?',
        expected_output='A brutal security and QA teardown of the system.',
        agent=security,
        callback=lambda output: task_callback("Security & QA Expert", output.raw)
    )

    task4 = Task(
        description='Read the original architecture AND the security teardown. Create a finalized, bulletproof architecture that specifically patches the security flaws mentioned.',
        expected_output='The final, secure System Architecture.',
        agent=cto,
        callback=lambda output: task_callback("Principal Architect (CTO)", output.raw)
    )

    crew = Crew(
        agents=[pm, architect, security, cto],
        tasks=[task1, task2, task3, task4],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
