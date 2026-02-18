from pydantic import BaseModel


class QuestionOption(BaseModel):
    """Option for a questionnaire question."""
    value: str
    label: str


class Question(BaseModel):
    """Questionnaire question with multiple choice options."""
    id: str
    question: str
    options: list[QuestionOption]


class GoalTemplate(BaseModel):
    """Predefined goal template with fixed primary metric."""
    id: str
    name: str
    description: str
    primary_metric_name: str  # e.g., "Weight", "Study hours", "Pages read"
    primary_metric_unit: str  # e.g., "kg", "hours", "pages"
    icon: str  # emoji or icon name
    category: str  # "fitness", "productivity", "learning", "health", "finance"
    example_habits: list[str]  # Examples to show in UI (not auto-created)
    questionnaire: list[Question] = []  # Questions to understand user context


# Predefined goal templates - GENERIC GOALS
GOAL_TEMPLATES = [
    # Fitness Goals
    GoalTemplate(
        id="weight-loss",
        name="Lose Weight",
        description="Track your weight and build sustainable habits to reach your target",
        primary_metric_name="Weight",
        primary_metric_unit="kg",
        icon="🏃",
        category="fitness",
        example_habits=[
            "Walk 10,000 steps daily",
            "Track meals and calories",
            "Drink 2L of water",
            "Exercise 3x per week"
        ],
        questionnaire=[
            Question(
                id="activity_level",
                question="What's your current activity level?",
                options=[
                    QuestionOption(value="sedentary", label="Sedentary (desk job, little to no exercise)"),
                    QuestionOption(value="light", label="Lightly active (light exercise 1-3 days/week)"),
                    QuestionOption(value="moderate", label="Moderately active (exercise 3-5 days/week)"),
                    QuestionOption(value="very", label="Very active (hard exercise 6-7 days/week)"),
                ]
            ),
            Question(
                id="exercise_preference",
                question="What type of exercise do you prefer?",
                options=[
                    QuestionOption(value="cardio", label="Cardio (running, cycling, swimming)"),
                    QuestionOption(value="strength", label="Strength training (gym, weights)"),
                    QuestionOption(value="sports", label="Sports (tennis, basketball, etc.)"),
                    QuestionOption(value="walking", label="Walking/hiking"),
                    QuestionOption(value="home_workout", label="Home workouts (yoga, HIIT)"),
                    QuestionOption(value="none", label="I don't enjoy exercise yet"),
                ]
            ),
            Question(
                id="diet_approach",
                question="What diet approach interests you most?",
                options=[
                    QuestionOption(value="calorie_counting", label="Calorie counting"),
                    QuestionOption(value="portion_control", label="Portion control (no counting)"),
                    QuestionOption(value="intermittent_fasting", label="Intermittent fasting"),
                    QuestionOption(value="keto", label="Keto/low-carb"),
                    QuestionOption(value="balanced", label="Balanced eating (whole foods)"),
                    QuestionOption(value="unsure", label="Not sure yet"),
                ]
            ),
            Question(
                id="cooking_frequency",
                question="How often do you cook at home?",
                options=[
                    QuestionOption(value="daily", label="Daily or almost daily"),
                    QuestionOption(value="few_times", label="A few times a week"),
                    QuestionOption(value="weekends", label="Only on weekends"),
                    QuestionOption(value="rarely", label="Rarely (mostly eat out/order)"),
                ]
            ),
            Question(
                id="schedule",
                question="When are you most free for exercise?",
                options=[
                    QuestionOption(value="early_morning", label="Early morning (5-7 AM)"),
                    QuestionOption(value="morning", label="Morning (7-10 AM)"),
                    QuestionOption(value="midday", label="Midday/lunch break"),
                    QuestionOption(value="evening", label="Evening (5-8 PM)"),
                    QuestionOption(value="night", label="Night (after 8 PM)"),
                    QuestionOption(value="variable", label="Varies day to day"),
                ]
            ),
            Question(
                id="biggest_challenge",
                question="What's your biggest challenge with weight loss?",
                options=[
                    QuestionOption(value="consistency", label="Staying consistent"),
                    QuestionOption(value="motivation", label="Motivation after a few weeks"),
                    QuestionOption(value="cravings", label="Food cravings and snacking"),
                    QuestionOption(value="time", label="Finding time to exercise"),
                    QuestionOption(value="energy", label="Low energy levels"),
                    QuestionOption(value="social", label="Social events and eating out"),
                ]
            ),
            Question(
                id="previous_attempts",
                question="Have you tried losing weight before?",
                options=[
                    QuestionOption(value="first_time", label="This is my first serious attempt"),
                    QuestionOption(value="few_times", label="Yes, a few times"),
                    QuestionOption(value="many_times", label="Yes, many times (yo-yo dieting)"),
                    QuestionOption(value="recently", label="Yes, recently but gained it back"),
                ]
            ),
            Question(
                id="stress_eating",
                question="Do you eat in response to stress or emotions?",
                options=[
                    QuestionOption(value="often", label="Yes, very often"),
                    QuestionOption(value="sometimes", label="Sometimes"),
                    QuestionOption(value="rarely", label="Rarely"),
                    QuestionOption(value="never", label="No, not really"),
                ]
            ),
            Question(
                id="sleep_quality",
                question="How would you rate your sleep quality?",
                options=[
                    QuestionOption(value="excellent", label="Excellent (7-9 hrs, feel rested)"),
                    QuestionOption(value="good", label="Good (mostly 6-8 hrs)"),
                    QuestionOption(value="fair", label="Fair (5-7 hrs, sometimes tired)"),
                    QuestionOption(value="poor", label="Poor (less than 6 hrs or poor quality)"),
                ]
            ),
            Question(
                id="support_system",
                question="Do you have support for this goal?",
                options=[
                    QuestionOption(value="strong", label="Yes, strong support (family/friends)"),
                    QuestionOption(value="some", label="Some support"),
                    QuestionOption(value="neutral", label="Neutral (not encouraging or discouraging)"),
                    QuestionOption(value="none", label="No support (doing this alone)"),
                ]
            ),
            Question(
                id="tracking_preference",
                question="How comfortable are you with tracking?",
                options=[
                    QuestionOption(value="love_it", label="I love tracking everything"),
                    QuestionOption(value="okay", label="I'm okay with it"),
                    QuestionOption(value="minimal", label="Prefer minimal tracking"),
                    QuestionOption(value="dislike", label="I dislike tracking"),
                ]
            ),
        ]
    ),
    GoalTemplate(
        id="weight-gain",
        name="Gain Weight",
        description="Build muscle and reach your target weight through strength training and nutrition",
        primary_metric_name="Weight",
        primary_metric_unit="kg",
        icon="💪",
        category="fitness",
        example_habits=[
            "Strength training 4x per week",
            "Eat 3000+ calories daily",
            "Track protein (150g+)",
            "Pre/post workout meals"
        ],
        questionnaire=[
            Question(
                id="training_experience",
                question="What's your strength training experience?",
                options=[
                    QuestionOption(value="beginner", label="Complete beginner"),
                    QuestionOption(value="some", label="Some experience (less than 6 months)"),
                    QuestionOption(value="intermediate", label="Intermediate (6 months - 2 years)"),
                    QuestionOption(value="advanced", label="Advanced (2+ years)"),
                ]
            ),
            Question(
                id="gym_access",
                question="Do you have access to a gym?",
                options=[
                    QuestionOption(value="full_gym", label="Yes, full gym with weights"),
                    QuestionOption(value="basic", label="Yes, basic equipment only"),
                    QuestionOption(value="home_equipment", label="No, but I have home equipment"),
                    QuestionOption(value="bodyweight", label="No equipment (bodyweight only)"),
                ]
            ),
            Question(
                id="eating_frequency",
                question="How many meals can you realistically eat per day?",
                options=[
                    QuestionOption(value="2-3", label="2-3 meals"),
                    QuestionOption(value="4-5", label="4-5 meals"),
                    QuestionOption(value="6plus", label="6+ meals/snacks"),
                ]
            ),
            Question(
                id="appetite",
                question="How's your appetite?",
                options=[
                    QuestionOption(value="low", label="Low (struggle to eat enough)"),
                    QuestionOption(value="normal", label="Normal"),
                    QuestionOption(value="high", label="High (easy to eat a lot)"),
                ]
            ),
            Question(
                id="protein_intake",
                question="Do you currently track protein intake?",
                options=[
                    QuestionOption(value="yes_track", label="Yes, I track it regularly"),
                    QuestionOption(value="estimate", label="I estimate roughly"),
                    QuestionOption(value="no_track", label="No, never tracked"),
                ]
            ),
            Question(
                id="training_schedule",
                question="How many days per week can you train?",
                options=[
                    QuestionOption(value="2-3", label="2-3 days"),
                    QuestionOption(value="4-5", label="4-5 days"),
                    QuestionOption(value="6plus", label="6+ days"),
                ]
            ),
            Question(
                id="goal_type",
                question="What's your primary goal?",
                options=[
                    QuestionOption(value="muscle", label="Build muscle (lean bulk)"),
                    QuestionOption(value="strength", label="Gain strength"),
                    QuestionOption(value="size", label="Get bigger (muscle + some fat)"),
                    QuestionOption(value="recover", label="Recover from being underweight"),
                ]
            ),
            Question(
                id="dietary_restrictions",
                question="Do you have dietary restrictions?",
                options=[
                    QuestionOption(value="none", label="No restrictions"),
                    QuestionOption(value="vegetarian", label="Vegetarian"),
                    QuestionOption(value="vegan", label="Vegan"),
                    QuestionOption(value="other", label="Other restrictions (allergies, etc.)"),
                ]
            ),
            Question(
                id="supplement_use",
                question="Are you open to using supplements?",
                options=[
                    QuestionOption(value="already_use", label="Already using (protein, creatine, etc.)"),
                    QuestionOption(value="open", label="Open to it"),
                    QuestionOption(value="maybe", label="Maybe, need guidance"),
                    QuestionOption(value="no", label="Prefer whole foods only"),
                ]
            ),
            Question(
                id="previous_attempts",
                question="Have you tried gaining weight before?",
                options=[
                    QuestionOption(value="first_time", label="First serious attempt"),
                    QuestionOption(value="few_times", label="Yes, a few times"),
                    QuestionOption(value="struggled", label="Yes, but always struggled to gain"),
                ]
            ),
            Question(
                id="time_commitment",
                question="How much time can you dedicate per workout?",
                options=[
                    QuestionOption(value="30min", label="30 minutes or less"),
                    QuestionOption(value="45min", label="45 minutes"),
                    QuestionOption(value="60min", label="60 minutes"),
                    QuestionOption(value="90min", label="90+ minutes"),
                ]
            ),
        ]
    ),
    GoalTemplate(
        id="run-distance",
        name="Run Longer",
        description="Increase running distance and endurance progressively",
        primary_metric_name="Running distance",
        primary_metric_unit="km",
        icon="🏃‍♂️",
        category="fitness",
        example_habits=[
            "Run 3-4x per week",
            "Increase distance 10% weekly",
            "Track pace and distance",
            "Rest day between runs"
        ],
        questionnaire=[
            Question(
                id="running_experience",
                question="What's your running experience?",
                options=[
                    QuestionOption(value="beginner", label="Complete beginner (never run regularly)"),
                    QuestionOption(value="returning", label="Returning runner (took a break)"),
                    QuestionOption(value="intermediate", label="Intermediate (run regularly for months)"),
                    QuestionOption(value="experienced", label="Experienced (run for years)"),
                ]
            ),
            Question(
                id="current_frequency",
                question="How often do you currently run?",
                options=[
                    QuestionOption(value="never", label="Not running currently"),
                    QuestionOption(value="1-2", label="1-2 times per week"),
                    QuestionOption(value="3-4", label="3-4 times per week"),
                    QuestionOption(value="5plus", label="5+ times per week"),
                ]
            ),
            Question(
                id="injury_history",
                question="Do you have any running-related injuries or concerns?",
                options=[
                    QuestionOption(value="none", label="No injuries or concerns"),
                    QuestionOption(value="past", label="Past injuries (fully recovered)"),
                    QuestionOption(value="chronic", label="Chronic issues (knee, shin, etc.)"),
                    QuestionOption(value="recovering", label="Currently recovering from injury"),
                ]
            ),
            Question(
                id="terrain_preference",
                question="Where do you prefer to run?",
                options=[
                    QuestionOption(value="treadmill", label="Treadmill/indoor"),
                    QuestionOption(value="pavement", label="Pavement/road"),
                    QuestionOption(value="trail", label="Trail/nature paths"),
                    QuestionOption(value="track", label="Running track"),
                    QuestionOption(value="mixed", label="Mix of different terrains"),
                ]
            ),
            Question(
                id="running_time",
                question="When do you prefer to run?",
                options=[
                    QuestionOption(value="early_morning", label="Early morning (before 7 AM)"),
                    QuestionOption(value="morning", label="Morning (7-10 AM)"),
                    QuestionOption(value="midday", label="Midday"),
                    QuestionOption(value="evening", label="Evening (5-8 PM)"),
                    QuestionOption(value="flexible", label="Flexible/varies"),
                ]
            ),
            Question(
                id="motivation_type",
                question="What motivates you most?",
                options=[
                    QuestionOption(value="distance", label="Increasing distance"),
                    QuestionOption(value="speed", label="Getting faster"),
                    QuestionOption(value="health", label="Health and fitness"),
                    QuestionOption(value="events", label="Training for races/events"),
                    QuestionOption(value="mental", label="Mental clarity and stress relief"),
                ]
            ),
            Question(
                id="cross_training",
                question="Do you do other forms of exercise?",
                options=[
                    QuestionOption(value="none", label="No, just running"),
                    QuestionOption(value="strength", label="Yes, strength training"),
                    QuestionOption(value="yoga", label="Yes, yoga/stretching"),
                    QuestionOption(value="cycling", label="Yes, cycling/swimming"),
                    QuestionOption(value="mixed", label="Yes, various activities"),
                ]
            ),
            Question(
                id="biggest_challenge",
                question="What's your biggest running challenge?",
                options=[
                    QuestionOption(value="consistency", label="Staying consistent"),
                    QuestionOption(value="breathing", label="Breathing/endurance"),
                    QuestionOption(value="pain", label="Aches and pains"),
                    QuestionOption(value="motivation", label="Motivation/boredom"),
                    QuestionOption(value="time", label="Finding time"),
                ]
            ),
            Question(
                id="recovery_focus",
                question="How do you approach recovery?",
                options=[
                    QuestionOption(value="active", label="Active recovery (stretching, foam rolling)"),
                    QuestionOption(value="rest_days", label="Rest days only"),
                    QuestionOption(value="minimal", label="Minimal recovery (run through soreness)"),
                    QuestionOption(value="unsure", label="Not sure what I should do"),
                ]
            ),
            Question(
                id="weather_impact",
                question="Does weather affect your running?",
                options=[
                    QuestionOption(value="no_issue", label="I run in any weather"),
                    QuestionOption(value="prefer_good", label="Prefer good weather but flexible"),
                    QuestionOption(value="fair_only", label="Only run in fair weather"),
                    QuestionOption(value="indoor_backup", label="Switch to indoor if bad weather"),
                ]
            ),
        ]
    ),
    GoalTemplate(
        id="general-fitness",
        name="General Fitness",
        description="Build overall fitness through consistent exercise and healthy habits",
        primary_metric_name="Active minutes",
        primary_metric_unit="minutes",
        icon="🔥",
        category="fitness",
        example_habits=[
            "30-minute workout daily",
            "10,000 steps daily",
            "Stretch for 10 minutes",
            "Track water intake"
        ],
        questionnaire=[
            Question(
                id="fitness_level",
                question="How would you rate your current fitness level?",
                options=[
                    QuestionOption(value="low", label="Low (rarely exercise)"),
                    QuestionOption(value="moderate", label="Moderate (some activity)"),
                    QuestionOption(value="good", label="Good (regular exercise)"),
                    QuestionOption(value="high", label="High (very active)"),
                ]
            ),
            Question(
                id="activity_types",
                question="What activities interest you most?",
                options=[
                    QuestionOption(value="cardio", label="Cardio (running, cycling, etc.)"),
                    QuestionOption(value="strength", label="Strength training"),
                    QuestionOption(value="group", label="Group classes (Zumba, spin, etc.)"),
                    QuestionOption(value="outdoor", label="Outdoor activities (hiking, sports)"),
                    QuestionOption(value="home", label="Home workouts (YouTube, apps)"),
                    QuestionOption(value="variety", label="Mix of different activities"),
                ]
            ),
            Question(
                id="time_available",
                question="How much time can you commit daily?",
                options=[
                    QuestionOption(value="15min", label="15 minutes"),
                    QuestionOption(value="30min", label="30 minutes"),
                    QuestionOption(value="45min", label="45 minutes"),
                    QuestionOption(value="60min", label="60+ minutes"),
                ]
            ),
            Question(
                id="schedule_flexibility",
                question="Is your daily schedule consistent?",
                options=[
                    QuestionOption(value="very", label="Very consistent (same time daily)"),
                    QuestionOption(value="mostly", label="Mostly consistent"),
                    QuestionOption(value="varies", label="Varies (shift work, irregular hours)"),
                    QuestionOption(value="unpredictable", label="Unpredictable (hard to plan)"),
                ]
            ),
            Question(
                id="fitness_goal",
                question="What's your primary fitness goal?",
                options=[
                    QuestionOption(value="weight_loss", label="Lose weight"),
                    QuestionOption(value="build_muscle", label="Build muscle/strength"),
                    QuestionOption(value="endurance", label="Improve endurance"),
                    QuestionOption(value="health", label="General health and energy"),
                    QuestionOption(value="habit", label="Build exercise habit"),
                ]
            ),
            Question(
                id="equipment_access",
                question="What equipment do you have access to?",
                options=[
                    QuestionOption(value="gym", label="Full gym membership"),
                    QuestionOption(value="home_full", label="Home gym (weights, equipment)"),
                    QuestionOption(value="basic", label="Basic equipment (dumbbells, mat)"),
                    QuestionOption(value="none", label="No equipment (bodyweight only)"),
                ]
            ),
            Question(
                id="social_preference",
                question="Do you prefer exercising alone or with others?",
                options=[
                    QuestionOption(value="alone", label="Alone (me time)"),
                    QuestionOption(value="partner", label="With a workout partner"),
                    QuestionOption(value="group", label="Group settings"),
                    QuestionOption(value="no_preference", label="No preference"),
                ]
            ),
            Question(
                id="energy_levels",
                question="When do you have the most energy?",
                options=[
                    QuestionOption(value="morning", label="Morning"),
                    QuestionOption(value="midday", label="Midday"),
                    QuestionOption(value="evening", label="Evening"),
                    QuestionOption(value="varies", label="Varies day to day"),
                ]
            ),
            Question(
                id="past_exercise",
                question="Have you exercised regularly in the past?",
                options=[
                    QuestionOption(value="never", label="No, never consistently"),
                    QuestionOption(value="long_ago", label="Yes, but long ago"),
                    QuestionOption(value="on_off", label="On and off (struggle with consistency)"),
                    QuestionOption(value="recently", label="Yes, recently but stopped"),
                ]
            ),
            Question(
                id="barriers",
                question="What's your biggest barrier to fitness?",
                options=[
                    QuestionOption(value="time", label="Time/busy schedule"),
                    QuestionOption(value="motivation", label="Motivation"),
                    QuestionOption(value="energy", label="Energy/fatigue"),
                    QuestionOption(value="knowledge", label="Don't know what to do"),
                    QuestionOption(value="pain", label="Pain/discomfort"),
                ]
            ),
        ]
    ),
    # Productivity Goals
    GoalTemplate(
        id="deep-work",
        name="Deep Work Focus",
        description="Increase focused work time and productivity through deliberate practice",
        primary_metric_name="Deep work hours",
        primary_metric_unit="hours",
        icon="🎯",
        category="productivity",
        example_habits=[
            "2-hour deep work session daily",
            "No phone during focus blocks",
            "Plan tomorrow tonight",
            "Track distractions"
        ],
        questionnaire=[
            Question(
                id="current_focus_time",
                question="How much focused work do you currently do daily?",
                options=[
                    QuestionOption(value="none", label="Almost none (constant distractions)"),
                    QuestionOption(value="1hr", label="About 1 hour"),
                    QuestionOption(value="2-3hr", label="2-3 hours"),
                    QuestionOption(value="4plus", label="4+ hours"),
                ]
            ),
            Question(
                id="work_type",
                question="What type of work do you do?",
                options=[
                    QuestionOption(value="creative", label="Creative work (writing, design, etc.)"),
                    QuestionOption(value="technical", label="Technical (coding, analysis, etc.)"),
                    QuestionOption(value="knowledge", label="Knowledge work (research, planning)"),
                    QuestionOption(value="mixed", label="Mix of different types"),
                ]
            ),
            Question(
                id="biggest_distraction",
                question="What distracts you most?",
                options=[
                    QuestionOption(value="phone", label="Phone/notifications"),
                    QuestionOption(value="social_media", label="Social media/internet"),
                    QuestionOption(value="people", label="People/interruptions"),
                    QuestionOption(value="email", label="Email/messages"),
                    QuestionOption(value="thoughts", label="My own thoughts/mental wandering"),
                ]
            ),
            Question(
                id="environment",
                question="Where do you work?",
                options=[
                    QuestionOption(value="home_quiet", label="Home (quiet, private space)"),
                    QuestionOption(value="home_distracting", label="Home (shared, distracting)"),
                    QuestionOption(value="office", label="Office (open plan)"),
                    QuestionOption(value="office_private", label="Office (private room)"),
                    QuestionOption(value="varies", label="Varies (remote/hybrid)"),
                ]
            ),
            Question(
                id="best_time",
                question="When are you most focused?",
                options=[
                    QuestionOption(value="early_morning", label="Early morning (5-8 AM)"),
                    QuestionOption(value="morning", label="Morning (8-12 PM)"),
                    QuestionOption(value="afternoon", label="Afternoon (12-5 PM)"),
                    QuestionOption(value="evening", label="Evening (5-10 PM)"),
                    QuestionOption(value="night", label="Late night (after 10 PM)"),
                ]
            ),
            Question(
                id="session_length",
                question="How long can you currently focus without a break?",
                options=[
                    QuestionOption(value="15min", label="15-20 minutes"),
                    QuestionOption(value="30min", label="30-45 minutes"),
                    QuestionOption(value="60min", label="60-90 minutes"),
                    QuestionOption(value="2hrplus", label="2+ hours"),
                ]
            ),
            Question(
                id="planning_habit",
                question="Do you plan your work in advance?",
                options=[
                    QuestionOption(value="daily", label="Yes, daily planning"),
                    QuestionOption(value="weekly", label="Yes, weekly planning"),
                    QuestionOption(value="sometimes", label="Sometimes/inconsistent"),
                    QuestionOption(value="never", label="No, I just start working"),
                ]
            ),
            Question(
                id="energy_management",
                question="How do you manage energy throughout the day?",
                options=[
                    QuestionOption(value="intentional", label="Intentionally (breaks, nutrition, exercise)"),
                    QuestionOption(value="breaks", label="Take breaks when needed"),
                    QuestionOption(value="power_through", label="Power through (caffeine, willpower)"),
                    QuestionOption(value="struggle", label="Struggle with energy dips"),
                ]
            ),
            Question(
                id="meeting_load",
                question="How many meetings/calls do you have daily?",
                options=[
                    QuestionOption(value="none", label="Almost none"),
                    QuestionOption(value="few", label="1-3 meetings"),
                    QuestionOption(value="many", label="4-6 meetings"),
                    QuestionOption(value="back_to_back", label="Back-to-back all day"),
                ]
            ),
            Question(
                id="tracking_experience",
                question="Do you currently track your productivity?",
                options=[
                    QuestionOption(value="detailed", label="Yes, detailed tracking"),
                    QuestionOption(value="basic", label="Basic tracking (to-do lists)"),
                    QuestionOption(value="tried", label="Tried but didn't stick"),
                    QuestionOption(value="never", label="Never tracked"),
                ]
            ),
            Question(
                id="motivation",
                question="What motivates you to improve focus?",
                options=[
                    QuestionOption(value="career", label="Career growth/performance"),
                    QuestionOption(value="project", label="Specific project/goal"),
                    QuestionOption(value="learning", label="Learning and skill development"),
                    QuestionOption(value="balance", label="Work-life balance (finish faster)"),
                    QuestionOption(value="fulfillment", label="Personal fulfillment"),
                ]
            ),
        ]
    ),
    GoalTemplate(
        id="side-project",
        name="Build Side Project",
        description="Make consistent progress on your side project or business",
        primary_metric_name="Hours worked",
        primary_metric_unit="hours",
        icon="🚀",
        category="productivity",
        example_habits=[
            "Work on project 1 hour daily",
            "Ship one feature per week",
            "Review progress weekly",
            "Connect with users"
        ],
        questionnaire=[
            Question(
                id="project_type",
                question="What type of project are you building?",
                options=[
                    QuestionOption(value="app", label="App/software product"),
                    QuestionOption(value="content", label="Content (blog, YouTube, etc.)"),
                    QuestionOption(value="service", label="Service business"),
                    QuestionOption(value="ecommerce", label="E-commerce/physical product"),
                    QuestionOption(value="other", label="Other"),
                ]
            ),
            Question(
                id="project_stage",
                question="What stage is your project at?",
                options=[
                    QuestionOption(value="idea", label="Idea phase (planning)"),
                    QuestionOption(value="early", label="Early development (no launch)"),
                    QuestionOption(value="launched", label="Launched (has users)"),
                    QuestionOption(value="growing", label="Growing (iterating based on feedback)"),
                ]
            ),
            Question(
                id="time_available",
                question="How much time can you dedicate daily?",
                options=[
                    QuestionOption(value="30min", label="30 minutes"),
                    QuestionOption(value="1hr", label="1 hour"),
                    QuestionOption(value="2hr", label="2 hours"),
                    QuestionOption(value="3hrplus", label="3+ hours"),
                ]
            ),
            Question(
                id="schedule_consistency",
                question="When can you work on your project?",
                options=[
                    QuestionOption(value="morning", label="Morning before work"),
                    QuestionOption(value="lunch", label="Lunch breaks"),
                    QuestionOption(value="evening", label="Evenings after work"),
                    QuestionOption(value="weekends", label="Weekends only"),
                    QuestionOption(value="varies", label="Varies (irregular schedule)"),
                ]
            ),
            Question(
                id="main_bottleneck",
                question="What's your main bottleneck?",
                options=[
                    QuestionOption(value="time", label="Time (too busy)"),
                    QuestionOption(value="consistency", label="Consistency (starting but not finishing)"),
                    QuestionOption(value="skills", label="Skills (learning as I build)"),
                    QuestionOption(value="motivation", label="Motivation (losing interest)"),
                    QuestionOption(value="direction", label="Direction (not sure what to build)"),
                ]
            ),
            Question(
                id="energy_levels",
                question="How's your energy after your day job?",
                options=[
                    QuestionOption(value="high", label="High (ready to work)"),
                    QuestionOption(value="moderate", label="Moderate (can push through)"),
                    QuestionOption(value="low", label="Low (usually exhausted)"),
                    QuestionOption(value="no_day_job", label="No day job (full-time on this)"),
                ]
            ),
            Question(
                id="accountability",
                question="Do you have accountability partners?",
                options=[
                    QuestionOption(value="yes", label="Yes (co-founder, mentor, or group)"),
                    QuestionOption(value="informal", label="Informal (friends following progress)"),
                    QuestionOption(value="none", label="No, working solo"),
                ]
            ),
            Question(
                id="measurement",
                question="How do you currently measure progress?",
                options=[
                    QuestionOption(value="shipped", label="Features shipped"),
                    QuestionOption(value="time", label="Time/hours worked"),
                    QuestionOption(value="users", label="Users/customers acquired"),
                    QuestionOption(value="revenue", label="Revenue/sales"),
                    QuestionOption(value="no_tracking", label="Don't track formally"),
                ]
            ),
            Question(
                id="biggest_challenge",
                question="What's your biggest challenge?",
                options=[
                    QuestionOption(value="starting", label="Starting (procrastination)"),
                    QuestionOption(value="continuing", label="Continuing (lose steam after a few days)"),
                    QuestionOption(value="scope_creep", label="Scope creep (too ambitious)"),
                    QuestionOption(value="perfectionism", label="Perfectionism (never shipping)"),
                    QuestionOption(value="validation", label="Validation (is this worth building?)"),
                ]
            ),
            Question(
                id="past_projects",
                question="Have you completed side projects before?",
                options=[
                    QuestionOption(value="many", label="Yes, several successful projects"),
                    QuestionOption(value="few", label="Yes, a few"),
                    QuestionOption(value="unfinished", label="Started but never finished"),
                    QuestionOption(value="first", label="This is my first serious attempt"),
                ]
            ),
            Question(
                id="goal_timeline",
                question="What's your goal timeline?",
                options=[
                    QuestionOption(value="1month", label="Launch in 1 month"),
                    QuestionOption(value="3months", label="Launch in 3 months"),
                    QuestionOption(value="6months", label="Build over 6+ months"),
                    QuestionOption(value="long_term", label="Long-term (1+ year)"),
                ]
            ),
        ]
    ),
    # Learning Goals
    GoalTemplate(
        id="read-books",
        name="Read More Books",
        description="Build a consistent reading habit and finish more books",
        primary_metric_name="Pages read",
        primary_metric_unit="pages",
        icon="📚",
        category="learning",
        example_habits=[
            "Read 30 pages daily",
            "Read before bed",
            "Take notes on key insights",
            "Review weekly"
        ],
        questionnaire=[
            Question(
                id="current_reading",
                question="How much do you currently read?",
                options=[
                    QuestionOption(value="rarely", label="Rarely (less than 1 book/year)"),
                    QuestionOption(value="few", label="A few books per year"),
                    QuestionOption(value="monthly", label="About 1 book per month"),
                    QuestionOption(value="weekly", label="1+ books per week"),
                ]
            ),
            Question(
                id="reading_format",
                question="What format do you prefer?",
                options=[
                    QuestionOption(value="physical", label="Physical books"),
                    QuestionOption(value="ebook", label="E-books (Kindle, etc.)"),
                    QuestionOption(value="audiobook", label="Audiobooks"),
                    QuestionOption(value="mixed", label="Mix of different formats"),
                ]
            ),
            Question(
                id="genre_preference",
                question="What genres interest you most?",
                options=[
                    QuestionOption(value="nonfiction", label="Non-fiction (self-help, business, etc.)"),
                    QuestionOption(value="fiction", label="Fiction (novels, stories)"),
                    QuestionOption(value="technical", label="Technical/professional books"),
                    QuestionOption(value="varied", label="Varied genres"),
                ]
            ),
            Question(
                id="best_reading_time",
                question="When do you prefer to read?",
                options=[
                    QuestionOption(value="morning", label="Morning (before day starts)"),
                    QuestionOption(value="commute", label="During commute"),
                    QuestionOption(value="breaks", label="During breaks/lunch"),
                    QuestionOption(value="evening", label="Evening (before bed)"),
                    QuestionOption(value="weekend", label="Weekends"),
                ]
            ),
            Question(
                id="biggest_barrier",
                question="What prevents you from reading more?",
                options=[
                    QuestionOption(value="time", label="No time (too busy)"),
                    QuestionOption(value="distractions", label="Distractions (phone, TV, etc.)"),
                    QuestionOption(value="tired", label="Too tired at end of day"),
                    QuestionOption(value="focus", label="Can't focus/mind wanders"),
                    QuestionOption(value="motivation", label="Lose interest quickly"),
                ]
            ),
            Question(
                id="reading_speed",
                question="How would you rate your reading speed?",
                options=[
                    QuestionOption(value="slow", label="Slow (savor every word)"),
                    QuestionOption(value="moderate", label="Moderate"),
                    QuestionOption(value="fast", label="Fast reader"),
                ]
            ),
            Question(
                id="comprehension",
                question="Do you retain what you read?",
                options=[
                    QuestionOption(value="excellent", label="Yes, I remember well"),
                    QuestionOption(value="okay", label="Sometimes, but forget details"),
                    QuestionOption(value="poor", label="I forget most of it"),
                    QuestionOption(value="take_notes", label="I take notes to remember"),
                ]
            ),
            Question(
                id="starting_vs_finishing",
                question="Do you finish books you start?",
                options=[
                    QuestionOption(value="always", label="Almost always finish"),
                    QuestionOption(value="mostly", label="Finish most books"),
                    QuestionOption(value="half", label="Finish about half"),
                    QuestionOption(value="rarely", label="Start many, finish few"),
                ]
            ),
            Question(
                id="reading_environment",
                question="Where do you read best?",
                options=[
                    QuestionOption(value="bed", label="In bed"),
                    QuestionOption(value="couch", label="Couch/comfy chair"),
                    QuestionOption(value="quiet_space", label="Quiet dedicated space"),
                    QuestionOption(value="public", label="Coffee shop/public spaces"),
                    QuestionOption(value="anywhere", label="Anywhere works"),
                ]
            ),
            Question(
                id="goal_motivation",
                question="Why do you want to read more?",
                options=[
                    QuestionOption(value="learn", label="Learn and grow"),
                    QuestionOption(value="career", label="Career/professional development"),
                    QuestionOption(value="enjoyment", label="Enjoyment and relaxation"),
                    QuestionOption(value="habit", label="Build a healthy habit"),
                    QuestionOption(value="specific", label="Specific reading list/goals"),
                ]
            ),
        ]
    ),
    GoalTemplate(
        id="learn-skill",
        name="Learn New Skill",
        description="Master a new skill through deliberate practice and consistency",
        primary_metric_name="Practice hours",
        primary_metric_unit="hours",
        icon="🎓",
        category="learning",
        example_habits=[
            "Practice 1 hour daily",
            "Track progress weekly",
            "Review fundamentals",
            "Build projects"
        ],
        questionnaire=[
            Question(
                id="skill_type",
                question="What type of skill are you learning?",
                options=[
                    QuestionOption(value="technical", label="Technical (programming, design, etc.)"),
                    QuestionOption(value="creative", label="Creative (music, art, writing)"),
                    QuestionOption(value="language", label="Language learning"),
                    QuestionOption(value="professional", label="Professional (public speaking, etc.)"),
                    QuestionOption(value="physical", label="Physical (instrument, sport)"),
                ]
            ),
            Question(
                id="learning_stage",
                question="What stage are you at?",
                options=[
                    QuestionOption(value="complete_beginner", label="Complete beginner"),
                    QuestionOption(value="beginner", label="Beginner (some basics)"),
                    QuestionOption(value="intermediate", label="Intermediate (building fluency)"),
                    QuestionOption(value="advanced", label="Advanced (refining expertise)"),
                ]
            ),
            Question(
                id="time_commitment",
                question="How much time can you practice daily?",
                options=[
                    QuestionOption(value="15min", label="15-30 minutes"),
                    QuestionOption(value="1hr", label="1 hour"),
                    QuestionOption(value="2hr", label="2 hours"),
                    QuestionOption(value="3hrplus", label="3+ hours"),
                ]
            ),
            Question(
                id="learning_style",
                question="How do you learn best?",
                options=[
                    QuestionOption(value="courses", label="Online courses/structured programs"),
                    QuestionOption(value="books", label="Books and documentation"),
                    QuestionOption(value="videos", label="YouTube/video tutorials"),
                    QuestionOption(value="practice", label="Learning by doing/projects"),
                    QuestionOption(value="instructor", label="Instructor/teacher/mentor"),
                ]
            ),
            Question(
                id="practice_consistency",
                question="How consistent have you been with practice?",
                options=[
                    QuestionOption(value="very", label="Very consistent (daily)"),
                    QuestionOption(value="moderate", label="Moderate (few times a week)"),
                    QuestionOption(value="sporadic", label="Sporadic (on and off)"),
                    QuestionOption(value="just_started", label="Just starting"),
                ]
            ),
            Question(
                id="motivation_type",
                question="Why are you learning this skill?",
                options=[
                    QuestionOption(value="career", label="Career advancement"),
                    QuestionOption(value="career_change", label="Career change/new job"),
                    QuestionOption(value="passion", label="Personal passion/interest"),
                    QuestionOption(value="side_income", label="Side income/freelancing"),
                    QuestionOption(value="challenge", label="Personal challenge/growth"),
                ]
            ),
            Question(
                id="accountability",
                question="Do you have learning accountability?",
                options=[
                    QuestionOption(value="teacher", label="Teacher/mentor"),
                    QuestionOption(value="community", label="Community/study group"),
                    QuestionOption(value="informal", label="Informal (friends/family)"),
                    QuestionOption(value="solo", label="Solo (no accountability)"),
                ]
            ),
            Question(
                id="progress_tracking",
                question="How do you track progress?",
                options=[
                    QuestionOption(value="projects", label="Building projects/portfolio"),
                    QuestionOption(value="exercises", label="Completing exercises/drills"),
                    QuestionOption(value="time", label="Hours practiced"),
                    QuestionOption(value="milestones", label="Milestones/certifications"),
                    QuestionOption(value="no_tracking", label="Don't track formally"),
                ]
            ),
            Question(
                id="biggest_challenge",
                question="What's your biggest learning challenge?",
                options=[
                    QuestionOption(value="consistency", label="Staying consistent"),
                    QuestionOption(value="plateau", label="Hitting plateaus (not improving)"),
                    QuestionOption(value="overwhelm", label="Too much to learn (overwhelmed)"),
                    QuestionOption(value="motivation", label="Losing motivation"),
                    QuestionOption(value="application", label="Applying what I learn"),
                ]
            ),
            Question(
                id="feedback",
                question="Do you get feedback on your work?",
                options=[
                    QuestionOption(value="regular", label="Yes, regular feedback"),
                    QuestionOption(value="sometimes", label="Sometimes"),
                    QuestionOption(value="rarely", label="Rarely"),
                    QuestionOption(value="self", label="Only self-assessment"),
                ]
            ),
            Question(
                id="energy_levels",
                question="When are you most alert for learning?",
                options=[
                    QuestionOption(value="morning", label="Morning"),
                    QuestionOption(value="afternoon", label="Afternoon"),
                    QuestionOption(value="evening", label="Evening"),
                    QuestionOption(value="night", label="Night"),
                ]
            ),
        ]
    ),
    # Health Goals
    GoalTemplate(
        id="sleep-better",
        name="Improve Sleep",
        description="Build better sleep habits and track sleep quality",
        primary_metric_name="Sleep hours",
        primary_metric_unit="hours",
        icon="😴",
        category="health",
        example_habits=[
            "Bed by 10 PM",
            "No screens 1 hour before bed",
            "Morning sunlight exposure",
            "Track sleep quality"
        ],
        questionnaire=[
            Question(
                id="current_sleep",
                question="How many hours do you currently sleep?",
                options=[
                    QuestionOption(value="less_5", label="Less than 5 hours"),
                    QuestionOption(value="5-6", label="5-6 hours"),
                    QuestionOption(value="6-7", label="6-7 hours"),
                    QuestionOption(value="7-8", label="7-8 hours"),
                    QuestionOption(value="8plus", label="8+ hours"),
                ]
            ),
            Question(
                id="sleep_quality",
                question="How would you rate your sleep quality?",
                options=[
                    QuestionOption(value="poor", label="Poor (wake up exhausted)"),
                    QuestionOption(value="fair", label="Fair (somewhat rested)"),
                    QuestionOption(value="good", label="Good (mostly rested)"),
                    QuestionOption(value="excellent", label="Excellent (very rested)"),
                ]
            ),
            Question(
                id="falling_asleep",
                question="How long does it take you to fall asleep?",
                options=[
                    QuestionOption(value="fast", label="Under 15 minutes"),
                    QuestionOption(value="moderate", label="15-30 minutes"),
                    QuestionOption(value="long", label="30-60 minutes"),
                    QuestionOption(value="very_long", label="Over 1 hour"),
                ]
            ),
            Question(
                id="night_waking",
                question="Do you wake up during the night?",
                options=[
                    QuestionOption(value="never", label="Rarely or never"),
                    QuestionOption(value="once", label="Once per night"),
                    QuestionOption(value="multiple", label="Multiple times"),
                    QuestionOption(value="often", label="Frequently (hard to get back to sleep)"),
                ]
            ),
            Question(
                id="bedtime_consistency",
                question="How consistent is your bedtime?",
                options=[
                    QuestionOption(value="very", label="Very consistent (same time daily)"),
                    QuestionOption(value="mostly", label="Mostly consistent"),
                    QuestionOption(value="varies", label="Varies (1-2 hour range)"),
                    QuestionOption(value="irregular", label="Very irregular"),
                ]
            ),
            Question(
                id="screen_time",
                question="Do you use screens before bed?",
                options=[
                    QuestionOption(value="none", label="No screens 1+ hours before bed"),
                    QuestionOption(value="minimal", label="Minimal use"),
                    QuestionOption(value="moderate", label="Use until 30 mins before bed"),
                    QuestionOption(value="heavy", label="Use right until bed"),
                ]
            ),
            Question(
                id="caffeine",
                question="When do you have your last caffeinated drink?",
                options=[
                    QuestionOption(value="morning", label="Morning only"),
                    QuestionOption(value="noon", label="Before noon"),
                    QuestionOption(value="afternoon", label="Early afternoon"),
                    QuestionOption(value="evening", label="Late afternoon/evening"),
                    QuestionOption(value="no_caffeine", label="Don't drink caffeine"),
                ]
            ),
            Question(
                id="exercise",
                question="Do you exercise regularly?",
                options=[
                    QuestionOption(value="daily", label="Yes, daily"),
                    QuestionOption(value="few_times", label="A few times a week"),
                    QuestionOption(value="occasionally", label="Occasionally"),
                    QuestionOption(value="rarely", label="Rarely or never"),
                ]
            ),
            Question(
                id="sleep_environment",
                question="How is your sleep environment?",
                options=[
                    QuestionOption(value="optimal", label="Optimal (dark, quiet, cool)"),
                    QuestionOption(value="good", label="Good (mostly comfortable)"),
                    QuestionOption(value="fair", label="Fair (some issues)"),
                    QuestionOption(value="poor", label="Poor (noisy, light, uncomfortable)"),
                ]
            ),
            Question(
                id="stress_levels",
                question="How stressed are you before bed?",
                options=[
                    QuestionOption(value="low", label="Low (relaxed)"),
                    QuestionOption(value="moderate", label="Moderate"),
                    QuestionOption(value="high", label="High (racing thoughts)"),
                    QuestionOption(value="very_high", label="Very high (anxious)"),
                ]
            ),
            Question(
                id="biggest_issue",
                question="What's your biggest sleep issue?",
                options=[
                    QuestionOption(value="falling_asleep", label="Falling asleep"),
                    QuestionOption(value="staying_asleep", label="Staying asleep"),
                    QuestionOption(value="waking_up", label="Waking up feeling tired"),
                    QuestionOption(value="consistency", label="Inconsistent schedule"),
                    QuestionOption(value="duration", label="Not enough hours"),
                ]
            ),
        ]
    ),
    GoalTemplate(
        id="meditation",
        name="Meditation Practice",
        description="Build a consistent meditation practice for mental clarity",
        primary_metric_name="Meditation minutes",
        primary_metric_unit="minutes",
        icon="🧘",
        category="health",
        example_habits=[
            "Meditate 10 minutes daily",
            "Morning meditation",
            "Track mood and energy",
            "Use guided sessions"
        ],
        questionnaire=[
            Question(
                id="experience_level",
                question="What's your meditation experience?",
                options=[
                    QuestionOption(value="complete_beginner", label="Complete beginner"),
                    QuestionOption(value="tried_few", label="Tried a few times"),
                    QuestionOption(value="inconsistent", label="On and off for months"),
                    QuestionOption(value="regular", label="Regular practice"),
                ]
            ),
            Question(
                id="meditation_type",
                question="What type of meditation interests you?",
                options=[
                    QuestionOption(value="mindfulness", label="Mindfulness (breath awareness)"),
                    QuestionOption(value="guided", label="Guided meditation"),
                    QuestionOption(value="body_scan", label="Body scan"),
                    QuestionOption(value="loving_kindness", label="Loving-kindness/metta"),
                    QuestionOption(value="transcendental", label="Transcendental/mantra"),
                    QuestionOption(value="unsure", label="Not sure yet"),
                ]
            ),
            Question(
                id="duration_preference",
                question="How long can you meditate currently?",
                options=[
                    QuestionOption(value="5min", label="5 minutes or less"),
                    QuestionOption(value="10min", label="10 minutes"),
                    QuestionOption(value="20min", label="20 minutes"),
                    QuestionOption(value="30min", label="30+ minutes"),
                ]
            ),
            Question(
                id="best_time",
                question="When would you prefer to meditate?",
                options=[
                    QuestionOption(value="early_morning", label="Early morning (upon waking)"),
                    QuestionOption(value="morning", label="Mid-morning"),
                    QuestionOption(value="midday", label="Midday/lunch break"),
                    QuestionOption(value="evening", label="Evening (after work)"),
                    QuestionOption(value="before_bed", label="Before bed"),
                ]
            ),
            Question(
                id="main_goal",
                question="What's your primary goal for meditating?",
                options=[
                    QuestionOption(value="stress", label="Reduce stress/anxiety"),
                    QuestionOption(value="focus", label="Improve focus/concentration"),
                    QuestionOption(value="sleep", label="Better sleep"),
                    QuestionOption(value="awareness", label="Self-awareness/mindfulness"),
                    QuestionOption(value="spiritual", label="Spiritual growth"),
                    QuestionOption(value="habit", label="Build a daily practice"),
                ]
            ),
            Question(
                id="biggest_challenge",
                question="What's your biggest meditation challenge?",
                options=[
                    QuestionOption(value="mind_wanders", label="Mind wanders constantly"),
                    QuestionOption(value="restless", label="Feel restless/can't sit still"),
                    QuestionOption(value="consistency", label="Can't maintain consistency"),
                    QuestionOption(value="time", label="Finding time"),
                    QuestionOption(value="sleepy", label="Fall asleep during meditation"),
                ]
            ),
            Question(
                id="guidance_preference",
                question="Do you prefer guided or silent meditation?",
                options=[
                    QuestionOption(value="guided", label="Guided (with voice/instructions)"),
                    QuestionOption(value="silent", label="Silent (no guidance)"),
                    QuestionOption(value="music", label="With calming music"),
                    QuestionOption(value="mix", label="Mix of different styles"),
                ]
            ),
            Question(
                id="environment",
                question="Where can you meditate?",
                options=[
                    QuestionOption(value="quiet_room", label="Quiet dedicated space"),
                    QuestionOption(value="bedroom", label="Bedroom"),
                    QuestionOption(value="living_space", label="Living room/shared space"),
                    QuestionOption(value="outdoors", label="Outdoors/nature"),
                    QuestionOption(value="anywhere", label="Anywhere (flexible)"),
                ]
            ),
            Question(
                id="app_usage",
                question="Have you used meditation apps?",
                options=[
                    QuestionOption(value="regularly", label="Yes, use them regularly"),
                    QuestionOption(value="tried", label="Tried but didn't stick"),
                    QuestionOption(value="never", label="Never tried"),
                ]
            ),
            Question(
                id="stress_level",
                question="How would you rate your current stress level?",
                options=[
                    QuestionOption(value="low", label="Low (calm, balanced)"),
                    QuestionOption(value="moderate", label="Moderate (manageable)"),
                    QuestionOption(value="high", label="High (frequently stressed)"),
                    QuestionOption(value="very_high", label="Very high (overwhelmed)"),
                ]
            ),
        ]
    ),
    # Finance Goals
    GoalTemplate(
        id="save-money",
        name="Save Money",
        description="Build savings through consistent contributions and spending tracking",
        primary_metric_name="Money saved",
        primary_metric_unit="$",
        icon="💰",
        category="finance",
        example_habits=[
            "Track all expenses daily",
            "Save 20% of income",
            "No impulse purchases",
            "Review budget weekly"
        ],
        questionnaire=[
            Question(
                id="current_savings",
                question="How much do you currently save per month?",
                options=[
                    QuestionOption(value="none", label="Nothing (living paycheck to paycheck)"),
                    QuestionOption(value="little", label="A little (under 10% of income)"),
                    QuestionOption(value="moderate", label="Moderate (10-20% of income)"),
                    QuestionOption(value="good", label="Good (20%+ of income)"),
                ]
            ),
            Question(
                id="tracking_expenses",
                question="Do you currently track your expenses?",
                options=[
                    QuestionOption(value="detailed", label="Yes, detailed tracking (apps, spreadsheets)"),
                    QuestionOption(value="rough", label="Roughly (know general spending)"),
                    QuestionOption(value="sometimes", label="Sometimes (inconsistent)"),
                    QuestionOption(value="never", label="No, never tracked"),
                ]
            ),
            Question(
                id="biggest_expense",
                question="What's your biggest spending category?",
                options=[
                    QuestionOption(value="housing", label="Housing/rent"),
                    QuestionOption(value="food", label="Food (dining out, groceries)"),
                    QuestionOption(value="entertainment", label="Entertainment/subscriptions"),
                    QuestionOption(value="shopping", label="Shopping/online purchases"),
                    QuestionOption(value="transport", label="Transportation/car"),
                    QuestionOption(value="unsure", label="Not sure"),
                ]
            ),
            Question(
                id="impulse_buying",
                question="How often do you make impulse purchases?",
                options=[
                    QuestionOption(value="rarely", label="Rarely (very disciplined)"),
                    QuestionOption(value="sometimes", label="Sometimes"),
                    QuestionOption(value="often", label="Often (struggle with it)"),
                    QuestionOption(value="very_often", label="Very often (major issue)"),
                ]
            ),
            Question(
                id="saving_goal",
                question="What are you saving for?",
                options=[
                    QuestionOption(value="emergency", label="Emergency fund"),
                    QuestionOption(value="big_purchase", label="Big purchase (car, house, etc.)"),
                    QuestionOption(value="debt", label="Pay off debt"),
                    QuestionOption(value="retirement", label="Retirement/long-term"),
                    QuestionOption(value="general", label="General savings"),
                    QuestionOption(value="multiple", label="Multiple goals"),
                ]
            ),
            Question(
                id="budget_system",
                question="Do you have a budget?",
                options=[
                    QuestionOption(value="strict", label="Yes, strict budget I follow"),
                    QuestionOption(value="loose", label="Yes, but loosely follow it"),
                    QuestionOption(value="tried", label="Tried but didn't stick"),
                    QuestionOption(value="none", label="No budget"),
                ]
            ),
            Question(
                id="income_stability",
                question="How stable is your income?",
                options=[
                    QuestionOption(value="very_stable", label="Very stable (fixed salary)"),
                    QuestionOption(value="stable", label="Stable (regular income)"),
                    QuestionOption(value="variable", label="Variable (commission, freelance)"),
                    QuestionOption(value="unpredictable", label="Unpredictable"),
                ]
            ),
            Question(
                id="debt_status",
                question="Do you have debt?",
                options=[
                    QuestionOption(value="none", label="No debt"),
                    QuestionOption(value="low", label="Low debt (manageable)"),
                    QuestionOption(value="moderate", label="Moderate debt"),
                    QuestionOption(value="high", label="High debt (overwhelming)"),
                ]
            ),
            Question(
                id="spending_triggers",
                question="What triggers your spending?",
                options=[
                    QuestionOption(value="stress", label="Stress/emotional spending"),
                    QuestionOption(value="social", label="Social situations (friends, eating out)"),
                    QuestionOption(value="boredom", label="Boredom/online browsing"),
                    QuestionOption(value="sales", label="Sales/deals (FOMO)"),
                    QuestionOption(value="needs", label="Genuine needs only"),
                ]
            ),
            Question(
                id="financial_knowledge",
                question="How would you rate your financial literacy?",
                options=[
                    QuestionOption(value="high", label="High (understand investing, budgeting)"),
                    QuestionOption(value="moderate", label="Moderate (know basics)"),
                    QuestionOption(value="low", label="Low (learning as I go)"),
                    QuestionOption(value="very_low", label="Very low (need guidance)"),
                ]
            ),
            Question(
                id="accountability",
                question="Do you have financial accountability?",
                options=[
                    QuestionOption(value="partner", label="Yes (spouse/partner)"),
                    QuestionOption(value="advisor", label="Yes (financial advisor/coach)"),
                    QuestionOption(value="informal", label="Informal (friends/family)"),
                    QuestionOption(value="solo", label="No, managing alone"),
                ]
            ),
        ]
    ),
]


def get_template_by_id(template_id: str) -> GoalTemplate | None:
    """Get a goal template by ID."""
    for template in GOAL_TEMPLATES:
        if template.id == template_id:
            return template
    return None
