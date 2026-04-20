from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_component_crew(component_request, task_callback, step_callback=None):
    llm = get_llm()
    
    designer = Agent(
        role='UI/UX Designer',
        goal='Define the precise color scheme, spacing, and styling rules for the requested component.',
        backstory='You are a pixel-perfect designer. You care deeply about aesthetics, modern styling, and ensuring everything looks premium and harmonious.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    jr_dev = Agent(
        role='Junior Developer',
        goal='Write a raw HTML and embedded CSS snippet based on the designer\'s specs.',
        backstory='You are an enthusiastic junior developer who writes functional code, though it might be a bit messy or lack polish.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )
    
    sr_dev = Agent(
        role='Senior Code Reviewer',
        goal='Critique the junior\'s code, fix it, and output exactly one final, polished HTML snippet with embedded CSS.',
        backstory='You are a strict, veteran developer. You demand perfection and perfectly self-contained code snippets. You ALWAYS output your final code inside ```html blocks.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=f'The user wants this UI element: "{component_request}". Describe a premium, modern design system (colors, padding, border radius, hover effects) for it.',
        expected_output='A strict design specification (colors, layout properties).',
        agent=designer,
        callback=lambda output: task_callback("UI/UX Designer", output.raw)
    )

    task2 = Task(
        description='Read the designer\'s specs. Write a single HTML file (with inline `<style>` tags) that builds this component perfectly.',
        expected_output='A self-contained functional HTML/CSS snippet.',
        agent=jr_dev,
        callback=lambda output: task_callback("Junior Developer", output.raw)
    )

    task3 = Task(
        description='Read the Junior Dev\'s code. Refine it for elegance. YOU MUST OUTPUT THE FINAL CODE ENCLOSED EXACTLY IN ```html ... ``` tags so the UI can parse it visually.',
        expected_output='A polished snippet. The code MUST be wrapped in ```html ... ```',
        agent=sr_dev,
        callback=lambda output: task_callback("Senior Code Reviewer", output.raw)
    )

    crew = Crew(
        agents=[designer, jr_dev, sr_dev],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
