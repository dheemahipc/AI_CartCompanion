"""
Configuration settings for Diet Expert AI system
Modify these values to customize system behavior
"""

# ============================================================================
# AGENT CONFIGURATION
# ============================================================================

# Agent Model Settings
AGENT_MODEL = 'gemini-2.5-flash'  # Google AI model to use
AGENT_NAME = 'diet_expert_ai'
AGENT_DESCRIPTION = 'Expert Dietician and Health Coach'

# ============================================================================
# STORAGE CONFIGURATION
# ============================================================================

# Storage Directories
USER_DATA_DIR = 'user_data'
CONVERSATION_DATA_DIR = 'conversation_data'

# Storage Limits
MAX_CONVERSATION_MESSAGES = 100  # Maximum messages to store per user
MAX_PROGRESS_UPDATES = 1000      # Maximum progress updates per user

# ============================================================================
# HEALTH CALCULATION SETTINGS
# ============================================================================

# BMI Categories (kg/m²)
BMI_UNDERWEIGHT = 18.5
BMI_NORMAL_MAX = 24.9
BMI_OVERWEIGHT_MAX = 29.9
# Above 29.9 is considered obese

# Activity Multipliers for TDEE
ACTIVITY_MULTIPLIERS = {
    'sedentary': 1.2,
    'lightly_active': 1.375,
    'moderately_active': 1.55,
    'very_active': 1.725,
    'extremely_active': 1.9,
}

# Calorie Adjustments for Goals (calories/day)
WEIGHT_LOSS_DEFICIT = 500        # Standard deficit for 0.5kg/week loss
WEIGHT_LOSS_AGGRESSIVE = 750     # Aggressive deficit for 0.75kg/week loss
WEIGHT_GAIN_SURPLUS = 350        # Standard surplus for 0.35kg/week gain
WEIGHT_GAIN_AGGRESSIVE = 500     # Aggressive surplus for 0.5kg/week gain

# Macro Calculation Settings (grams per kg body weight)
PROTEIN_WEIGHT_LOSS = 2.2
PROTEIN_WEIGHT_GAIN = 2.0
PROTEIN_MAINTENANCE = 1.8

FAT_WEIGHT_LOSS = 0.9
FAT_WEIGHT_GAIN = 1.0
FAT_MAINTENANCE = 1.0

# Water Intake Calculation
WATER_ML_PER_KG = 35             # Base water intake (ml per kg body weight)
WATER_BONUS_MODERATE = 250       # Extra ml for moderate activity
WATER_BONUS_HIGH = 500           # Extra ml for high activity

# ============================================================================
# SAFETY SETTINGS
# ============================================================================

# Minimum/Maximum Calorie Targets (safety bounds)
MIN_DAILY_CALORIES_MALE = 1500
MIN_DAILY_CALORIES_FEMALE = 1200
MAX_DAILY_CALORIES = 5000

# Minimum protein intake (grams per kg)
MIN_PROTEIN_PER_KG = 0.8

# Safe weight change rates (kg per week)
MAX_WEIGHT_LOSS_PER_WEEK = 1.0
MAX_WEIGHT_GAIN_PER_WEEK = 0.5
MIN_TIMELINE_WEEKS = 4  # Minimum recommended timeline for goals

# ============================================================================
# AGENT BEHAVIOR SETTINGS
# ============================================================================

# Conversation Settings
GREETING_EMOJI = "👋"
SUCCESS_EMOJI = "✓"
WARNING_EMOJI = "⚠️"
FITNESS_EMOJI = "💪"
NUTRITION_EMOJI = "🥗"
EXERCISE_EMOJI = "🏋️"

# Response Style
USE_EMOJIS = True
DETAILED_EXPLANATIONS = True
ENCOURAGE_MEDICAL_CONSULTATION = True

# Scope Restrictions
STRICT_HEALTH_FOCUS = True  # Only answer health/fitness/diet questions
PROVIDE_MEDICAL_ADVICE = False  # Never provide medical diagnosis
RECOMMEND_SUPPLEMENTS = True  # Can recommend common supplements
RECOMMEND_MEDICATIONS = False  # Never recommend medications

# ============================================================================
# REMINDER SETTINGS
# ============================================================================

# Default Meal Times
DEFAULT_MEAL_TIMES = [
    '7:00 AM',   # Breakfast
    '10:00 AM',  # Mid-morning snack
    '1:00 PM',   # Lunch
    '4:00 PM',   # Afternoon snack
    '7:00 PM',   # Dinner
    '9:00 PM',   # Evening snack (optional)
]

# Default Exercise Schedule
DEFAULT_EXERCISE_SCHEDULE = [
    'Monday 6:00 AM',
    'Wednesday 6:00 AM',
    'Friday 6:00 AM',
    'Sunday 6:00 AM',
]

# Check-in Frequency
DEFAULT_CHECKIN_SCHEDULE = [
    'Weekly weigh-in every Monday morning',
    'Monthly progress photos on 1st of month',
    'Bi-weekly measurements every other Monday',
]

# ============================================================================
# MEAL PLAN SETTINGS
# ============================================================================

# Meal Plan Generation
DEFAULT_PLAN_DURATION_DAYS = 7
MEALS_PER_DAY = 5  # Breakfast, snack, lunch, snack, dinner
INCLUDE_MEAL_PREP_TIPS = True
INCLUDE_SUBSTITUTIONS = True

# Food Database (simplified - expand as needed)
VEGETARIAN_PROTEIN_SOURCES = [
    'Paneer', 'Tofu', 'Lentils', 'Chickpeas', 'Greek yogurt',
    'Eggs', 'Quinoa', 'Soy', 'Nuts', 'Seeds'
]

NON_VEG_PROTEIN_SOURCES = [
    'Chicken breast', 'Fish', 'Eggs', 'Turkey', 'Lean beef',
    'Prawns', 'Tuna', 'Salmon', 'Cottage cheese'
]

COMPLEX_CARBS = [
    'Brown rice', 'Quinoa', 'Oats', 'Sweet potato', 'Whole wheat bread',
    'Whole wheat pasta', 'Barley', 'Millet', 'Buckwheat'
]

HEALTHY_FATS = [
    'Olive oil', 'Avocado', 'Nuts', 'Seeds', 'Nut butter',
    'Coconut oil', 'Ghee (moderate)', 'Fatty fish'
]

VEGETABLES = [
    'Broccoli', 'Spinach', 'Kale', 'Cauliflower', 'Bell peppers',
    'Tomatoes', 'Carrots', 'Cucumber', 'Lettuce', 'Zucchini'
]

FRUITS = [
    'Apple', 'Banana', 'Orange', 'Berries', 'Papaya',
    'Mango', 'Watermelon', 'Grapes', 'Kiwi', 'Pineapple'
]

# ============================================================================
# EXERCISE PLAN SETTINGS
# ============================================================================

# Workout Plan Defaults
DEFAULT_WORKOUT_FREQUENCY = 4  # Days per week
DEFAULT_WORKOUT_DURATION = 60  # Minutes per session
DEFAULT_REST_BETWEEN_SETS = 60  # Seconds

# Exercise Categories
STRENGTH_EXERCISES = [
    'Push-ups', 'Pull-ups', 'Squats', 'Deadlifts', 'Bench press',
    'Overhead press', 'Rows', 'Lunges', 'Planks', 'Dips'
]

CARDIO_EXERCISES = [
    'Running', 'Cycling', 'Swimming', 'Jump rope', 'HIIT',
    'Rowing', 'Stair climbing', 'Elliptical', 'Walking', 'Dancing'
]

FLEXIBILITY_EXERCISES = [
    'Yoga', 'Stretching', 'Pilates', 'Foam rolling', 'Dynamic stretches'
]

# Training Splits
TRAINING_SPLITS = {
    '3_day': 'Full Body',
    '4_day': 'Upper/Lower',
    '5_day': 'Push/Pull/Legs',
    '6_day': 'PPL × 2',
}

# ============================================================================
# LOCALIZATION SETTINGS
# ============================================================================

# Unit Preferences
DEFAULT_WEIGHT_UNIT = 'kg'  # 'kg' or 'lbs'
DEFAULT_HEIGHT_UNIT = 'cm'  # 'cm' or 'inches'
DEFAULT_TEMPERATURE_UNIT = 'celsius'  # 'celsius' or 'fahrenheit'

# Language Support
DEFAULT_LANGUAGE = 'en'  # English (expand for multi-language support)

# Regional Food Preferences
DEFAULT_CUISINE = 'international'  # Can be 'indian', 'mediterranean', etc.

# ============================================================================
# LOGGING & DEBUGGING
# ============================================================================

# Logging Settings
ENABLE_LOGGING = True
LOG_LEVEL = 'INFO'  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
LOG_FILE = 'diet_agent.log'

# Debug Mode
DEBUG_MODE = False  # Set to True for detailed debugging output

# ============================================================================
# API & INTEGRATION SETTINGS
# ============================================================================

# External API Integration (optional)
ENABLE_NUTRITION_API = False
ENABLE_EXERCISE_VIDEO_API = False
ENABLE_RECIPE_API = False

# API Keys (set in .env file, not here)
# NUTRITION_API_KEY = os.getenv('NUTRITION_API_KEY')
# RECIPE_API_KEY = os.getenv('RECIPE_API_KEY')

# ============================================================================
# ADVANCED FEATURES
# ============================================================================

# Enable/Disable Features
ENABLE_PROGRESS_CHARTS = False  # Requires matplotlib
ENABLE_MEAL_PHOTO_ANALYSIS = False  # Requires vision API
ENABLE_BARCODE_SCANNING = False  # Requires barcode API
ENABLE_RECIPE_GENERATION = True
ENABLE_SHOPPING_LIST = True
ENABLE_SOCIAL_FEATURES = False

# ============================================================================
# EXPORT SETTINGS
# ============================================================================

# Data Export Formats
EXPORT_FORMATS = ['json', 'csv', 'pdf']
DEFAULT_EXPORT_FORMAT = 'json'

# ============================================================================
# NOTIFICATION SETTINGS (for future implementation)
# ============================================================================

# Notification Channels
ENABLE_EMAIL_NOTIFICATIONS = False
ENABLE_SMS_NOTIFICATIONS = False
ENABLE_PUSH_NOTIFICATIONS = False

# Notification Timing
REMINDER_ADVANCE_MINUTES = 15  # Remind X minutes before scheduled time

# ============================================================================
# NOTES
# ============================================================================

"""
CUSTOMIZATION TIPS:

1. MODEL SELECTION:
   - Use 'gemini-2.5-flash' for fast responses
   - Use 'gemini-2.5-pro' for more detailed analysis
   
2. CALORIE ADJUSTMENTS:
   - Adjust deficits/surpluses based on your target audience
   - More aggressive = faster results but harder to sustain
   
3. MACRO RATIOS:
   - Current settings are evidence-based
   - Adjust protein/fat/carb ratios for specific diets (keto, high-carb, etc.)
   
4. FOOD LISTS:
   - Expand with regional foods
   - Add more variety for better meal plans
   
5. SAFETY BOUNDS:
   - Never lower minimum calorie limits
   - Adjust max weight change rates conservatively
   
6. FEATURES:
   - Enable advanced features as you implement them
   - Start simple, add complexity gradually

For questions about specific settings, refer to README.md
"""
