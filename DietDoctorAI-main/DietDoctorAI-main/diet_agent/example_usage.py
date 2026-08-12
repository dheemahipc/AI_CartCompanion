"""
Example usage of the Diet Expert AI system
This demonstrates how to interact with the diet agent and use storage features
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import diet_agent modules
sys.path.insert(0, str(Path(__file__).parent))

from agent import root_agent, USER_PROFILE_TEMPLATE
from user_storage import UserStorage, ConversationMemory
from health_utils import calculate_complete_health_profile


def initialize_user_profile(user_id: str = "demo_user"):
    """
    Initialize a new user profile with template
    
    Args:
        user_id: Unique identifier for the user
        
    Returns:
        User profile dictionary
    """
    storage = UserStorage()
    
    # Check if user exists
    existing_profile = storage.load_user_profile(user_id)
    if existing_profile:
        print(f"✓ Loaded existing profile for user: {user_id}")
        return existing_profile
    
    # Create new profile
    profile = USER_PROFILE_TEMPLATE.copy()
    storage.save_user_profile(user_id, profile)
    print(f"✓ Created new profile for user: {user_id}")
    return profile


def example_complete_user_flow():
    """
    Example demonstrating complete user flow from onboarding to plan generation
    """
    print("=" * 80)
    print("DIET EXPERT AI - COMPLETE USER FLOW EXAMPLE")
    print("=" * 80)
    
    user_id = "demo_user_001"
    storage = UserStorage()
    conversation = ConversationMemory()
    
    # Step 1: Initialize user profile
    print("\n[STEP 1] Initializing user profile...")
    profile = initialize_user_profile(user_id)
    
    # Step 2: Simulate user providing information
    print("\n[STEP 2] User provides personal information...")
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
        'food_restrictions': ['shellfish'],
        'favorite_foods': ['chicken', 'rice', 'broccoli'],
    }
    
    profile['health_metrics']['activity_level'] = 'moderately_active'
    
    profile['goals'] = {
        'primary_goal': 'weight_loss',
        'timeline_days': 90,
        'specific_requirements': ['Improve cardiovascular health', 'Build lean muscle'],
    }
    
    storage.save_user_profile(user_id, profile)
    print("✓ User profile updated")
    
    # Step 3: Calculate health metrics
    print("\n[STEP 3] Calculating health metrics...")
    health_profile = calculate_complete_health_profile(
        age=profile['personal_info']['age'],
        gender=profile['personal_info']['gender'],
        height_cm=profile['personal_info']['height_cm'],
        weight_kg=profile['personal_info']['current_weight_kg'],
        target_weight=profile['personal_info']['target_weight_kg'],
        activity_level=profile['health_metrics']['activity_level'],
        goal=profile['goals']['primary_goal']
    )
    
    # Update profile with calculated metrics
    profile['health_metrics'].update({
        'bmi': health_profile['bmi']['value'],
        'bmr': health_profile['bmr'],
        'daily_calorie_target': health_profile['calorie_plan']['target_calories'],
    })
    
    storage.save_user_profile(user_id, profile)
    
    # Display health profile
    print("\n--- HEALTH PROFILE ---")
    print(f"BMI: {health_profile['bmi']['value']} ({health_profile['bmi']['category']})")
    print(f"BMR: {health_profile['bmr']} calories/day")
    print(f"TDEE: {health_profile['tdee']} calories/day")
    print(f"Target Calories: {health_profile['calorie_plan']['target_calories']} calories/day")
    print(f"Goal: {health_profile['calorie_plan']['goal_type']}")
    print(f"Expected Weight Change: {health_profile['calorie_plan']['weekly_weight_change_kg']} kg/week")
    
    print("\n--- MACRONUTRIENT TARGETS ---")
    print(f"Protein: {health_profile['macronutrients']['protein']['grams']}g "
          f"({health_profile['macronutrients']['protein']['percentage']}%)")
    print(f"Carbs: {health_profile['macronutrients']['carbohydrates']['grams']}g "
          f"({health_profile['macronutrients']['carbohydrates']['percentage']}%)")
    print(f"Fats: {health_profile['macronutrients']['fats']['grams']}g "
          f"({health_profile['macronutrients']['fats']['percentage']}%)")
    
    print("\n--- TIMELINE ESTIMATE ---")
    print(f"Estimated time to goal: {health_profile['timeline']['weeks']} weeks "
          f"({health_profile['timeline']['months']} months)")
    print(f"Target date: {health_profile['timeline']['target_date']}")
    
    print("\n--- WATER INTAKE ---")
    print(f"Daily water: {health_profile['water_intake']['liters']} liters "
          f"({health_profile['water_intake']['glasses']} glasses)")
    
    # Step 4: Simulate conversation with agent
    print("\n[STEP 4] Starting conversation with Diet Expert AI...")
    
    # Add greeting message to conversation
    greeting = """Hello! 👋 I'm DietExpert AI, your personal Dietician and Health Expert.

I can see this is your first time here. I'm excited to help you achieve your health goals!
Based on your profile, you're looking to lose weight. I've calculated your personalized nutrition targets.

Would you like me to:
1. Create a detailed 7-day meal plan
2. Design a customized exercise routine
3. Provide detailed nutrition guidance
4. Answer any specific questions you have

What would you like to start with?"""
    
    conversation.add_message(user_id, 'assistant', greeting)
    print("\n[ASSISTANT]", greeting)
    
    # User asks for meal plan
    user_query = "I'd like a detailed 7-day meal plan with macros for each meal."
    conversation.add_message(user_id, 'user', user_query)
    print(f"\n[USER] {user_query}")
    
    # Step 5: Add sample diet plan to history
    print("\n[STEP 5] Generating diet plan...")
    sample_diet_plan = {
        'plan_name': '7-Day Weight Loss Meal Plan',
        'target_calories': health_profile['calorie_plan']['target_calories'],
        'macros': health_profile['macronutrients'],
        'notes': 'Non-vegetarian plan with no peanuts or shellfish',
    }
    
    storage.add_diet_plan(user_id, sample_diet_plan)
    print("✓ Diet plan saved to user history")
    
    # Step 6: Add sample exercise plan
    print("\n[STEP 6] Creating exercise plan...")
    sample_exercise_plan = {
        'plan_name': '12-Week Fat Loss & Conditioning Program',
        'frequency': '4 days per week',
        'duration': '60 minutes per session',
        'split': 'Upper/Lower body split',
        'focus': 'Weight loss, cardiovascular health, lean muscle preservation',
    }
    
    storage.add_exercise_plan(user_id, sample_exercise_plan)
    print("✓ Exercise plan saved to user history")
    
    # Step 7: Set reminders
    print("\n[STEP 7] Setting up reminders...")
    storage.set_reminders(user_id, 'meal_times', 
                         ['7:00 AM', '10:00 AM', '1:00 PM', '4:00 PM', '7:00 PM'])
    storage.set_reminders(user_id, 'exercise_times', 
                         ['6:00 AM (Mon, Wed, Fri)', '6:00 PM (Tue, Thu)'])
    storage.set_reminders(user_id, 'check_in_schedule', 
                         ['Weekly weigh-in every Monday morning', 'Monthly progress photos'])
    print("✓ Reminders configured")
    
    # Step 8: Simulate progress update after 2 weeks
    print("\n[STEP 8] Simulating progress update (after 2 weeks)...")
    progress_update = {
        'weight_kg': 83.5,
        'feedback': 'Feeling great! More energy and sleeping better.',
        'challenges': 'Struggled with late-night cravings on weekend',
        'compliance': '90% on diet, 100% on workouts',
    }
    
    storage.add_progress_update(user_id, progress_update)
    print("✓ Progress update recorded")
    print(f"   Weight change: {profile['personal_info']['current_weight_kg'] - progress_update['weight_kg']:.1f} kg lost")
    
    # Step 9: Display conversation history
    print("\n[STEP 9] Conversation history...")
    history = conversation.get_conversation_history(user_id, limit=5)
    print(f"✓ {len(history)} messages in conversation history")
    
    # Step 10: Load complete user profile
    print("\n[STEP 10] Loading complete user profile...")
    final_profile = storage.load_user_profile(user_id)
    print(f"✓ Profile loaded successfully")
    print(f"   First visit: {final_profile['history']['first_visit']}")
    print(f"   Last visit: {final_profile['history']['last_visit']}")
    print(f"   Progress updates: {len(final_profile['history']['progress_updates'])}")
    print(f"   Diet plans: {len(final_profile['history']['diet_plans'])}")
    print(f"   Exercise plans: {len(final_profile['history']['exercise_plans'])}")
    
    print("\n" + "=" * 80)
    print("EXAMPLE COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print(f"\nUser data stored in: user_data/user_{user_id}.json")
    print(f"Conversation stored in: conversation_data/conversation_{user_id}.json")
    print("\nThe Diet Expert AI agent is ready to provide personalized guidance!")


def example_returning_user():
    """
    Example showing how the system handles returning users with existing data
    """
    print("\n" + "=" * 80)
    print("RETURNING USER EXAMPLE")
    print("=" * 80)
    
    user_id = "demo_user_001"
    storage = UserStorage()
    
    # Load existing profile
    print("\n[RETURNING USER] Loading profile...")
    profile = storage.load_user_profile(user_id)
    
    if profile:
        print("✓ Welcome back!")
        print(f"   First visit: {profile['history']['first_visit']}")
        print(f"   Last visit: {profile['history']['last_visit']}")
        print(f"   Previous progress updates: {len(profile['history']['progress_updates'])}")
        
        # Show latest progress if available
        if profile['history']['progress_updates']:
            latest = profile['history']['progress_updates'][-1]
            print(f"\n   Latest progress update:")
            print(f"   - Weight: {latest.get('weight_kg', 'N/A')} kg")
            print(f"   - Feedback: {latest.get('feedback', 'N/A')}")
    else:
        print("No existing profile found. This would be a new user.")


def example_agent_interaction():
    """
    Example showing direct interaction with the agent
    """
    print("\n" + "=" * 80)
    print("DIRECT AGENT INTERACTION EXAMPLE")
    print("=" * 80)
    
    print("\nAgent details:")
    print(f"Name: {root_agent.name}")
    print(f"Model: {root_agent.model}")
    print(f"Description: {root_agent.description}")
    
    print("\n✓ Agent is ready to receive queries!")
    print("\nThe agent will:")
    print("  • Greet new users and explain capabilities")
    print("  • Systematically collect user information")
    print("  • Perform detailed health calculations")
    print("  • Generate personalized diet plans with macro breakdowns")
    print("  • Create exercise routines with form guidance")
    print("  • Remember conversation history and user progress")
    print("  • Stay focused on diet, exercise, and health topics only")


if __name__ == "__main__":
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█" + " " * 20 + "DIET EXPERT AI SYSTEM DEMO" + " " * 32 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    # Run examples
    example_complete_user_flow()
    example_returning_user()
    example_agent_interaction()
    
    print("\n" + "█" * 80)
    print("█" + " " * 25 + "DEMO COMPLETED!" + " " * 39 + "█")
    print("█" * 80 + "\n")
