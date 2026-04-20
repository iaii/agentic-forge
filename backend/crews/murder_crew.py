from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_murder_crew(input_data, task_callback, step_callback=None):
    scene = input_data.get("scene", "Unknown scene.")
    suspects = input_data.get("suspects", "No suspects.")
    
    llm = get_llm()
    
    csi = Agent(
        role='CSI Forensic Tech',
        goal='Scan the scene description, highlight physical anomalies, and determine the literal events.',
        backstory='You are a cold, calculating forensic scientist. You don\'t care about feelings, only evidence, blood spatter, and physical traces.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    profiler = Agent(
        role='Psychological Profiler',
        goal='Evaluate the suspects based on the forensics and assign a dark, hidden motive to each.',
        backstory='You are a brilliant behavioral analyst. You can look at a suspect\'s name and read their darkest secrets and insecurities.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    detective = Agent(
        role='Hardboiled Detective',
        goal='Review the forensics and profiles to build an airtight case and dramatically accuse the true culprit.',
        backstory='You are a cynical, chain-smoking detective from a noir novel. You\'ve seen it all, and you always get your guy (or gal, or dog).',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'Examine the following crime scene: "{scene}". Write a forensic report on what physical events likely occurred here.',
        expected_output='A detailed, cold forensic analysis of the crime scene constraints.',
        agent=csi,
        callback=lambda output: task_callback("CSI Forensic Tech", output.raw)
    )

    task2 = Task(
        description=f'Read the CSI report. Then look at this list of suspects: "{suspects}". Build a psychological profile and establish a plausible motive for why EACH suspect might have committed the crime based on the forensics.',
        expected_output='A deep psychological profile and motive for all listed suspects.',
        agent=profiler,
        callback=lambda output: task_callback("Psychological Profiler", output.raw)
    )

    task3 = Task(
        description='Read the forensic facts and the psychological motives. Deduce who the killer is. Write a dramatic monologue pointing the finger at the culprit and explaining exactly how and why they did it.',
        expected_output='A dramatic, noir-style accusation solving the case.',
        agent=detective,
        callback=lambda output: task_callback("Hardboiled Detective", output.raw)
    )

    crew = Crew(
        agents=[csi, profiler, detective],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
