# 🚀 Quick Start Guide - Diet Expert AI

Get up and running with your personal AI dietician in 5 minutes!

---

## Step 1: Setup Environment (1 minute)

1. Make sure you have Python 3.8+ installed:
```bash
python --version
```

2. Install dependencies:
```bash
pip install google-adk python-dotenv
```

3. Set your Google API key in `.env` file (already created):
```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=your_actual_api_key_here
```

---

## Step 2: Test the System (1 minute)

Run the demo to see everything in action:

```bash
python example_usage.py
```

This will create a sample user profile and demonstrate all features.

---

## Step 3: Integrate with Your Application (3 minutes)

### Basic Integration

```python
# Import the agent
from diet_agent.agent import root_agent
from diet_agent.user_storage import UserStorage, ConversationMemory
from diet_agent.health_utils import calculate_complete_health_profile

# Initialize storage
storage = UserStorage()
conversation = ConversationMemory()

# Your user's unique identifier
user_id = "user_12345"

# Check if user exists
profile = storage.load_user_profile(user_id)
if not profile:
    # New user - initialize profile
    from diet_agent.agent import USER_PROFILE_TEMPLATE
    profile = USER_PROFILE_TEMPLATE.copy()
    storage.save_user_profile(user_id, profile)
    print("New user created!")
else:
    print("Welcome back!")

# Now you can interact with the agent
# The agent will handle conversation and data collection
```

### Using the Agent in Conversations

```python
# Method 1: Direct interaction (using ADK's built-in methods)
# The exact method depends on how ADK handles conversations
# Refer to ADK documentation for specific API

# Method 2: Store conversation manually
user_message = "I want to lose 10kg in 3 months"
conversation.add_message(user_id, 'user', user_message)

# Agent processes and responds
# (ADK handles the actual response generation)

# Store agent's response
agent_response = "Great goal! Let me calculate your personalized plan..."
conversation.add_message(user_id, 'assistant', agent_response)
```

### Calculate Health Metrics

```python
# Once you have user's basic info
health_profile = calculate_complete_health_profile(
    age=28,
    gender='male',
    height_cm=175,
    weight_kg=85,
    target_weight=75,
    activity_level='moderately_active',
    goal='weight_loss'
)

# Access the results
print(f"Daily Calories: {health_profile['calorie_plan']['target_calories']}")
print(f"Protein: {health_profile['macronutrients']['protein']['grams']}g")
print(f"Carbs: {health_profile['macronutrients']['carbohydrates']['grams']}g")
print(f"Fats: {health_profile['macronutrients']['fats']['grams']}g")
```

### Track Progress

```python
# When user provides an update
progress_update = {
    'weight_kg': 83.5,
    'feedback': 'Feeling great!',
    'challenges': 'Late night cravings',
    'compliance': '90% diet, 100% exercise'
}

storage.add_progress_update(user_id, progress_update)
```

---

## Step 4: Understanding the Agent's Behavior

### What the Agent Does Automatically:

1. **Greets new users** with a warm introduction
2. **Collects information** systematically:
   - Age, gender, height, weight
   - Dietary preferences and allergies
   - Activity level and goals
   - Timeline and specific needs

3. **Performs calculations**:
   - BMI, BMR, TDEE
   - Calorie targets
   - Macro distribution
   - Timeline estimates

4. **Generates detailed plans**:
   - 7-day meal plans with macros
   - Exercise routines with form guidance
   - Water intake recommendations

5. **Provides ongoing support**:
   - Answers follow-up questions
   - Adjusts plans based on progress
   - Motivates and encourages
   - Addresses challenges

### What the Agent WON'T Do:

❌ Answer non-health/fitness questions
❌ Provide medical diagnosis
❌ Recommend unsafe practices
❌ Give advice outside its expertise

---

## Step 5: Common Use Cases

### Use Case 1: New User Onboarding

```python
user_id = "new_user_001"
storage = UserStorage()

# Create profile
from diet_agent.agent import USER_PROFILE_TEMPLATE
profile = USER_PROFILE_TEMPLATE.copy()

# Collect info from user (via your app's interface)
profile['personal_info'] = {
    'age': 30,
    'gender': 'female',
    'height_cm': 165,
    'current_weight_kg': 70,
    'target_weight_kg': 60,
}

profile['goals'] = {
    'primary_goal': 'weight_loss',
    'timeline_days': 90,
}

# Save
storage.save_user_profile(user_id, profile)
```

### Use Case 2: Returning User

```python
user_id = "existing_user_001"
storage = UserStorage()

# Load profile
profile = storage.load_user_profile(user_id)

if profile:
    # Show personalized greeting
    first_visit = profile['history']['first_visit']
    last_visit = profile['history']['last_visit']
    print(f"Welcome back! Last visit: {last_visit}")
    
    # Load conversation history
    conversation = ConversationMemory()
    history = conversation.get_conversation_history(user_id, limit=10)
    print(f"Previous messages: {len(history)}")
```

### Use Case 3: Progress Check-in

```python
user_id = "user_001"
storage = UserStorage()

# User provides update
new_weight = 68.5
feedback = "Lost 1.5kg this week! Feeling energetic!"

# Record progress
progress = {
    'weight_kg': new_weight,
    'feedback': feedback,
}
storage.add_progress_update(user_id, progress)

# Agent can now reference this in future conversations
```

---

## 💡 Tips for Best Results

1. **Collect Complete Information**: More data = better recommendations
2. **Use Unique User IDs**: Ensures proper data isolation
3. **Regular Check-ins**: Encourage users to update progress weekly
4. **Leverage Conversation History**: Provides context for better responses
5. **Combine with UI**: Create a nice interface for user interaction

---

## 🔧 Customization Quick Tips

### Change Agent's Personality
Edit `DIET_AGENT_INSTRUCTIONS` in `agent.py`

### Modify Calculations
Edit functions in `health_utils.py`

### Adjust Storage Location
```python
storage = UserStorage(storage_dir="my_custom_path")
```

### Add Custom Meal Templates
Create your own meal plan templates and reference them in the agent

---

## 📱 Integration Ideas

- **Web App**: Flask/FastAPI backend with React/Vue frontend
- **Mobile App**: React Native or Flutter with Python backend
- **Chat Interface**: WhatsApp, Telegram, Discord bots
- **Voice Assistant**: Alexa or Google Home integration
- **Fitness Tracker**: Sync with Fitbit, Apple Health, etc.

---

## 🆘 Troubleshooting

**Problem**: Import errors
```bash
# Solution: Install in correct environment
pip install google-adk
```

**Problem**: API key not working
```bash
# Solution: Check .env file
cat .env
# Make sure GOOGLE_API_KEY is set correctly
```

**Problem**: Files not saving
```bash
# Solution: Check permissions
ls -la user_data/
# Create directories manually if needed
mkdir -p user_data conversation_data
```

---

## 🎯 Next Steps

1. ✅ Run `example_usage.py` to see it in action
2. ✅ Read the full `README.md` for detailed documentation
3. ✅ Explore `health_utils.py` to understand calculations
4. ✅ Customize agent instructions for your use case
5. ✅ Build your UI/interface
6. ✅ Deploy and help users achieve their health goals!

---

## 📚 Additional Resources

- **Main README**: `README.md` - Complete documentation
- **Example Code**: `example_usage.py` - Working examples
- **Health Calculations**: `health_utils.py` - All formulas
- **Storage Management**: `user_storage.py` - Data handling
- **Agent Definition**: `agent.py` - AI agent configuration

---

**You're all set! Your AI dietician is ready to help users achieve their health goals! 💪🥗**

Questions? Review the full README.md or examine the example code!
