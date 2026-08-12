# 🥗 Diet Expert AI - Comprehensive Health & Fitness Agentic System

A sophisticated AI-powered dietician and health expert system built with Google's ADK (Agent Development Kit). This system provides personalized nutrition planning, exercise guidance, and ongoing health coaching with memory persistence and intelligent conversation management.

---

## 🌟 Features

### Core Capabilities
- **Personalized Diet Planning**: Detailed meal plans with precise macro calculations (carbs, protein, fats, calories)
- **Exercise Routines**: Customized workout plans with proper form guidance, posture instructions, and timing
- **Health Metrics**: Comprehensive calculations including BMI, BMR, TDEE, body composition estimates
- **Memory Persistence**: Remembers user information, conversation history, and progress across sessions
- **Progress Tracking**: Monitors weight changes, compliance, and adjusts plans based on results
- **Reminder System**: Configurable reminders for meals, workouts, and check-ins
- **Focused Expertise**: Strictly limited to diet, exercise, and health topics

### Intelligent Features
- **Contextual Conversations**: Maintains conversation history for natural follow-ups
- **Returning User Recognition**: Welcomes back users with their previous data
- **Adaptive Planning**: Adjusts recommendations based on progress and feedback
- **Goal Timeline Estimation**: Calculates realistic timelines for fitness goals
- **Dietary Accommodation**: Handles allergies, restrictions, preferences (vegetarian, vegan, etc.)
- **Multi-user Support**: Separate profiles and data for each user

---

## 📋 System Requirements

- Python 3.8+
- Google ADK (Agent Development Kit)
- Google API Key or Vertex AI credentials

---

## 🚀 Installation

1. **Install Google ADK** (if not already installed):
```bash
pip install google-adk
```

2. **Set up environment variables**:
Create a `.env` file in the `diet_agent` directory:
```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_api_key_here
```

3. **Verify installation**:
```bash
cd diet_agent
python example_usage.py
```

---

## 📁 Project Structure

```
diet_agent/
│
├── __init__.py                 # Package initialization
├── agent.py                    # Main diet expert AI agent definition
├── user_storage.py            # User profile and conversation storage
├── health_utils.py            # Health calculation utilities
├── example_usage.py           # Demo and usage examples
├── .env                       # Environment variables
│
├── user_data/                 # Directory for user profiles (auto-created)
│   └── user_*.json           # Individual user profile files
│
└── conversation_data/         # Directory for conversation history (auto-created)
    └── conversation_*.json   # Individual conversation files
```

---

## 🎯 How It Works

### 1. User Onboarding Flow

When a user first interacts with the system:

1. **Greeting**: Agent introduces itself and explains capabilities
2. **Information Gathering**: Systematically collects:
   - Personal info (age, gender, height, weight)
   - Dietary preferences (vegetarian, allergies, restrictions)
   - Activity level and current exercise routine
   - Health goals (weight loss, muscle gain, maintenance)
   - Timeline and specific requirements

3. **Health Calculations**: Automatically computes:
   - BMI and category
   - BMR (Basal Metabolic Rate)
   - TDEE (Total Daily Energy Expenditure)
   - Target calorie intake
   - Macronutrient distribution (protein, carbs, fats)
   - Water intake recommendations
   - Goal timeline estimation

4. **Plan Generation**: Creates personalized:
   - 7-day meal plans with detailed macros per meal
   - Exercise routines with form instructions
   - Supplement recommendations (if needed)

### 2. Conversation Management

- **Conversation History**: Stores up to 100 recent messages per user
- **Context Retention**: Agent remembers previous discussions
- **Natural Follow-ups**: Users can ask follow-up questions without repeating context
- **Session Continuity**: Returning users continue where they left off

### 3. Progress Tracking

- **Regular Check-ins**: Users can provide weight updates and feedback
- **Plan Adjustments**: Agent modifies recommendations based on progress
- **Challenge Resolution**: Addresses difficulties and provides solutions
- **Milestone Celebration**: Acknowledges achievements and motivates users

---

## 💻 Usage Examples

### Basic Usage

```python
from agent import root_agent
from user_storage import UserStorage, ConversationMemory

# Initialize storage
storage = UserStorage()
conversation = ConversationMemory()

# Define user ID
user_id = "user123"

# Start conversation
user_message = "Hi, I want to lose weight in 30 days"
conversation.add_message(user_id, 'user', user_message)

# Agent would respond with greeting and information gathering
# (ADK handles the actual conversation flow)
```

### Creating User Profile

```python
from agent import USER_PROFILE_TEMPLATE
from user_storage import UserStorage

storage = UserStorage()
user_id = "user123"

# Create profile
profile = USER_PROFILE_TEMPLATE.copy()
profile['personal_info'] = {
    'age': 28,
    'gender': 'male',
    'height_cm': 175,
    'current_weight_kg': 85,
    'target_weight_kg': 75,
}

profile['dietary_preferences'] = {
    'type': 'Non-vegetarian',
    'allergies': ['peanuts'],
    'food_restrictions': [],
    'favorite_foods': ['chicken', 'rice', 'eggs'],
}

profile['goals'] = {
    'primary_goal': 'weight_loss',
    'timeline_days': 30,
}

# Save profile
storage.save_user_profile(user_id, profile)
```

### Calculating Health Metrics

```python
from health_utils import calculate_complete_health_profile

health_profile = calculate_complete_health_profile(
    age=28,
    gender='male',
    height_cm=175,
    weight_kg=85,
    target_weight=75,
    activity_level='moderately_active',
    goal='weight_loss'
)

print(f"BMI: {health_profile['bmi']['value']}")
print(f"Daily Calories: {health_profile['calorie_plan']['target_calories']}")
print(f"Protein: {health_profile['macronutrients']['protein']['grams']}g")
```

### Adding Progress Updates

```python
from user_storage import UserStorage

storage = UserStorage()
user_id = "user123"

# Add progress update
progress = {
    'weight_kg': 83.5,
    'feedback': 'Feeling great, more energy!',
    'challenges': 'Late night cravings',
    'compliance': '90% on diet, 100% on exercise',
}

storage.add_progress_update(user_id, progress)
```

### Setting Reminders

```python
from user_storage import UserStorage

storage = UserStorage()
user_id = "user123"

# Set meal reminders
storage.set_reminders(user_id, 'meal_times', 
    ['7:00 AM', '10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM', '9:00 PM'])

# Set exercise reminders
storage.set_reminders(user_id, 'exercise_times', 
    ['6:00 AM (Mon, Wed, Fri)', '5:00 PM (Tue, Thu)'])

# Set check-in schedule
storage.set_reminders(user_id, 'check_in_schedule', 
    ['Weekly weigh-in every Monday', 'Monthly progress photos on 1st'])
```

---

## 🧮 Health Calculations Reference

### BMI (Body Mass Index)
```
BMI = weight(kg) / height(m)²
```
**Categories**:
- Underweight: < 18.5
- Normal: 18.5 - 24.9
- Overweight: 25 - 29.9
- Obese: ≥ 30

### BMR (Basal Metabolic Rate) - Mifflin-St Jeor Equation
```
Men: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age + 5
Women: BMR = 10 × weight(kg) + 6.25 × height(cm) - 5 × age - 161
```

### TDEE (Total Daily Energy Expenditure)
```
TDEE = BMR × Activity Multiplier
```
**Activity Multipliers**:
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extremely Active: 1.9

### Calorie Targets
- **Weight Loss**: TDEE - 500 to 750 cal (0.5-1 kg loss/week)
- **Weight Gain**: TDEE + 300 to 500 cal (0.25-0.5 kg gain/week)
- **Maintenance**: TDEE

### Macronutrient Distribution

**Weight Loss/Maintenance**:
- Protein: 1.6-2.2g per kg (30% of calories)
- Fats: 0.8-1g per kg (25% of calories)
- Carbs: Remaining (45% of calories)

**Muscle Gain**:
- Protein: 2-2.5g per kg (30-35% of calories)
- Fats: 1g per kg (25% of calories)
- Carbs: Remaining (40-45% of calories)

**Calorie Values**:
- 1g Protein = 4 calories
- 1g Carbohydrate = 4 calories
- 1g Fat = 9 calories

---

## 🎨 Sample Interactions

### Example 1: First Time User

**User**: "Hi, I want to lose weight"

**Agent**: "Hello! 👋 I'm DietExpert AI, your personal Dietician and Health Expert. I'm here to help you with personalized diet planning, exercise routines, and health guidance. To create the perfect plan for you, I'll need to understand your profile. Let's get started! 🎯

First, could you tell me your age?"

**User**: "I'm 28 years old"

**Agent**: "Great! And what's your gender?"

*[Continues information gathering...]*

### Example 2: Returning User

**User**: "Hi, I'm back with an update"

**Agent**: "Welcome back! 👋 I remember you started your weight loss journey 2 weeks ago. How has it been going? Have you noticed any changes in your weight or how you're feeling?"

**User**: "I've lost 1.5 kg! Feeling great but struggling with late-night snacks"

**Agent**: "That's fantastic progress! 1.5 kg in 2 weeks is excellent and sustainable. Regarding late-night cravings, let me suggest some strategies... [provides tailored advice]"

### Example 3: Follow-up Question

**User**: "What exercises should I do for lower abs?"

**Agent**: "Great question! For targeting lower abs, I recommend these exercises with proper form:

1. **Reverse Crunches**
   - Sets: 3 × 15 reps
   - Posture: Lie flat, hands by sides, legs bent at 90°...
   [provides detailed form instructions]"

---

## 🔒 Data Privacy & Storage

- **Local Storage**: All user data stored locally in JSON files
- **User Isolation**: Each user has separate profile and conversation files
- **No Cloud Sync**: Data remains on your machine unless you implement cloud storage
- **Easy Backup**: Simple JSON format allows easy backup and migration

---

## 🛠️ Customization

### Modifying Agent Instructions

Edit `agent.py` and update `DIET_AGENT_INSTRUCTIONS`:

```python
DIET_AGENT_INSTRUCTIONS = """
[Your custom instructions here]
"""
```

### Adjusting Calculation Formulas

Edit `health_utils.py` to modify BMR, TDEE, or macro calculations.

### Changing Storage Location

```python
storage = UserStorage(storage_dir="custom_user_data")
conversation = ConversationMemory(storage_dir="custom_conversation_data")
```

---

## 📊 Advanced Features

### Multi-Goal Support

The system supports various fitness goals:
- Weight loss
- Weight gain / Muscle building
- Body recomposition
- Athletic performance
- Health maintenance
- Disease management (with medical supervision)

### Dietary Variations

Handles multiple dietary preferences:
- Vegetarian
- Vegan
- Non-vegetarian
- Eggetarian
- Pescatarian
- Keto, Paleo, Mediterranean, etc.

### Exercise Modalities

Provides guidance for:
- Strength training
- Cardiovascular exercise
- HIIT (High-Intensity Interval Training)
- Yoga and flexibility
- Sports-specific training

---

## ⚠️ Important Disclaimers

1. **Not Medical Advice**: This system provides guidance, not medical diagnosis or treatment
2. **Consult Healthcare Providers**: Always consult with doctors before starting new diet/exercise programs
3. **Individual Variation**: Results may vary based on individual factors
4. **Safety First**: The agent prioritizes safe, sustainable approaches over quick fixes
5. **Medical Conditions**: Users with medical conditions should seek professional guidance

---

## 🐛 Troubleshooting

### Issue: Agent not responding
- Check API key in `.env` file
- Verify Google ADK installation: `pip show google-adk`
- Ensure internet connection for API calls

### Issue: Storage files not created
- Check write permissions in directory
- Manually create `user_data/` and `conversation_data/` folders

### Issue: Calculation errors
- Verify input data types (numbers for weight, height, age)
- Check that all required fields are provided

---

## 🚀 Running the Demo

Execute the example usage file to see the system in action:

```bash
cd diet_agent
python example_usage.py
```

This will:
1. Create a demo user profile
2. Calculate health metrics
3. Generate sample diet and exercise plans
4. Demonstrate progress tracking
5. Show conversation history management
6. Display returning user functionality

---

## 📈 Future Enhancements

Potential additions:
- [ ] Integration with fitness trackers (Fitbit, Apple Health)
- [ ] Meal photo analysis with AI vision
- [ ] Recipe database with macro calculations
- [ ] Shopping list generation
- [ ] Restaurant menu navigation assistance
- [ ] Supplement recommendations with scientific backing
- [ ] Video exercise demonstrations
- [ ] Social features (accountability partners)
- [ ] Mobile app integration
- [ ] Calendar sync for reminders

---

## 🤝 Contributing

To contribute improvements:
1. Test thoroughly with various user scenarios
2. Maintain scientific accuracy of calculations
3. Preserve user privacy and data security
4. Document all changes clearly
5. Follow existing code style

---

## 📝 License

[Specify your license here]

---

## 📞 Support

For questions or issues:
- Review the example usage file
- Check health_utils.py for calculation details
- Examine user_storage.py for data management
- Refer to Google ADK documentation

---

## 🙏 Acknowledgments

- Built with Google's Agent Development Kit (ADK)
- Health calculations based on established scientific formulas (Mifflin-St Jeor, etc.)
- Nutrition guidelines from evidence-based sources

---

**Remember**: This is a supportive tool, not a replacement for professional medical or nutritional advice. Always prioritize safety and consult healthcare providers for medical concerns! 💪🥗🏋️

