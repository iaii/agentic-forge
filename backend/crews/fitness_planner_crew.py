from crewai import Agent, Task, Crew, Process
from .llm_config import get_llm

def run_fitness_crew(fitness_goal, task_callback, step_callback=None):
    llm = get_llm()

    nutritionist = Agent(
        role='Nutritionist',
        goal='Define a precise, science-backed nutrition plan tailored to the user\'s dietary restrictions and fitness goals.',
        backstory='You are a certified sports nutritionist with 15 years of experience. You design evidence-based meal plans that align with the user\'s preferences, restrictions, and goals, ensuring optimal fueling for performance and recovery.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    trainer = Agent(
        role='Personal Trainer',
        goal='Design a structured workout plan that complements the nutrition plan and moves the user toward their fitness goal.',
        backstory='You are a certified personal trainer with 10 years of experience across strength, cardio, and mobility training. You build progressive, realistic programs tailored to the user\'s current fitness level and available equipment.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    coach = Agent(
        role='Fitness Coach',
        goal='Synthesize the nutrition and workout plans into a single, cohesive, and sustainable fitness program with lifestyle habits that ensure the user actually achieves their goal.',
        backstory='You are a holistic fitness coach who ensures that nutrition and training plans work in harmony. You add the missing layer: sleep, stress management, habit formation, mindset, and weekly structure — turning two plans into one complete lifestyle program.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

    task1 = Task(
        description=(
            f'The user submitted this fitness request: "{fitness_goal}". '
            'Extract and structure the following: (1) primary fitness goal, (2) time frame, '
            '(3) dietary restrictions and preferences, (4) current fitness level, '
            '(5) available equipment. If any information is missing, make reasonable assumptions and clearly state them. '
            'Then produce a detailed, personalized nutrition plan with daily macros, meal timing, and sample meals.'
        ),
        expected_output=(
            'A structured nutrition profile with labeled sections:\n'
            '- User Profile (goal, timeline, fitness level, equipment)\n'
            '- Assumptions Made\n'
            '- Daily Macro Targets (calories, protein, carbs, fats)\n'
            '- Meal Timing & Frequency\n'
            '- Sample Daily Meal Plan'
        ),
        agent=nutritionist,
        callback=lambda output: task_callback("Nutritionist", output.raw)
    )

    task2 = Task(
        description=(
            'Read the nutritionist\'s user profile and nutrition plan. '
            'Using the user\'s fitness goal, current fitness level, time frame, and available equipment, '
            'design a weekly workout program. Include exercise selection, sets, reps, rest periods, '
            'and how the program progresses over time.'
        ),
        expected_output=(
            'A structured weekly workout plan with labeled sections:\n'
            '- Training Philosophy & Approach\n'
            '- Weekly Schedule (days, muscle groups, session duration)\n'
            '- Exercise List per Session (sets, reps, rest)\n'
            '- Progression Plan (how to increase difficulty week over week)\n'
            '- Recovery & Rest Day Guidance'
        ),
        agent=trainer,
        context=[task1],
        callback=lambda output: task_callback("Personal Trainer", output.raw)
    )

    task3 = Task(
        description=(
            'Read the nutritionist\'s nutrition plan and the personal trainer\'s workout plan. '
            'Synthesize them into one complete, cohesive fitness program. '
            'Ensure the plans complement each other (e.g. nutrition timing around workouts). '
            'Then add the lifestyle layer: sleep targets, stress management, habit-building strategies, '
            'mindset tips, and a simple weekly routine the user can actually follow long-term. '
            'Output the final integrated plan in clean markdown so it can be rendered directly.'
        ),
        expected_output=(
            'A complete integrated fitness program in markdown with sections:\n'
            '## Goal Summary\n'
            '## Nutrition Plan\n'
            '## Workout Plan\n'
            '## Lifestyle & Habits (sleep, stress, mindset)\n'
            '## Weekly Schedule (combining all three)\n'
            '## Key Milestones & How to Track Progress'
        ),
        agent=coach,
        context=[task1, task2],
        callback=lambda output: task_callback("Fitness Coach", output.raw)
    )

    crew = Crew(
        agents=[nutritionist, trainer, coach],
        tasks=[task1, task2, task3],
        verbose=True,
        process=Process.sequential
    )

    return crew.kickoff()
