from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_zombie_crew(input_data, task_callback, step_callback=None):
    location = input_data.get("location", "Unknown Location")
    items = input_data.get("items", "Nothing")
    
    llm = get_llm()
    
    cb1 = lambda step: step_callback("Scout", step) if step_callback else None
    scout = Agent(
        role='The Scout',
        goal='Analyze the current location data for high-ground, resources, and escape routes from zombies.',
        backstory='You are an ex-park ranger who knows how to survive in the wild and read the terrain. You are hyper-vigilant.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb1
    )
    
    cb2 = lambda step: step_callback("Quartermaster", step) if step_callback else None
    quartermaster = Agent(
        role='The Quartermaster',
        goal='Evaluate the items currently available and figure out improvised weapons or tools.',
        backstory='You are a resourceful scavenger who can turn garbage into gold. MacGyver is your hero.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb2
    )
    
    cb3 = lambda step: step_callback("Tactician", step) if step_callback else None
    tactician = Agent(
        role='The Tactician',
        goal='Take the location and item data to write an actionable 48-hour survival plan.',
        backstory='You are a hardcore prepper and tactical genius. You give clear, step-by-step instructions for survival.',
        verbose=True,
        allow_delegation=False,
        llm=llm,
        step_callback=cb3
    )

    task1 = Task(
        description=f'Analyze the location and identify safe zones, hazards, and Chokepoints. Location: "{location}"',
        expected_output='A brief scout report of the location highlighting where to go and what to avoid.',
        agent=scout,
        callback=lambda output: task_callback("Scout", output.raw)
    )

    task2 = Task(
        description=f'Review the user\'s inventory and suggest 3 ways to use them to survive. Inventory: "{items}"',
        expected_output='A creative list of improvised tools and weapons using the provided items.',
        agent=quartermaster,
        callback=lambda output: task_callback("Quartermaster", output.raw)
    )

    task3 = Task(
        description='Read the Scout\'s report and the Quartermaster\'s inventory analysis. Write a step-by-step 48-hour survival plan based on their findings.',
        expected_output='A detailed, step-by-step 48 hour survival plan.',
        agent=tactician,
        callback=lambda output: task_callback("Tactician", output.raw)
    )

    crew = Crew(
        agents=[scout, quartermaster, tactician],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )
    
    return crew.kickoff()
