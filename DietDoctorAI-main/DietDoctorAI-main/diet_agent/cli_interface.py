#!/usr/bin/env python3
"""
Simple CLI interface for testing the Diet Expert AI system
Allows interactive conversations with the diet agent
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agent import root_agent, USER_PROFILE_TEMPLATE
from user_storage import UserStorage, ConversationMemory
from health_utils import calculate_complete_health_profile


def print_header():
    """Print welcome header"""
    print("\n" + "=" * 80)
    print("=" * 80)
    print("||" + " " * 76 + "||")
    print("||" + " " * 23 + "DIET EXPERT AI SYSTEM" + " " * 33 + "||")
    print("||" + " " * 17 + "Your Personal Dietician & Health Coach" + " " * 23 + "||")
    print("||" + " " * 76 + "||")
    print("=" * 80)
    print("=" * 80 + "\n")


def print_menu():
    """Print main menu"""
    print("\n" + "-" * 80)
    print("MAIN MENU")
    print("-" * 80)
    print("1. Start New Conversation")
    print("2. View User Profile")
    print("3. View Conversation History")
    print("4. Calculate Health Metrics")
    print("5. View Progress Updates")
    print("6. Set Reminders")
    print("7. List All Users")
    print("8. Delete User Profile")
    print("9. Run Demo")
    print("0. Exit")
    print("-" * 80)


def start_conversation(user_id: str):
    """Start a conversation with the agent"""
    storage = UserStorage()
    conversation = ConversationMemory()
    
    # Load or create profile
    profile = storage.load_user_profile(user_id)
    if not profile:
        print("\n🆕 New user detected! Creating profile...")
        profile = USER_PROFILE_TEMPLATE.copy()
        storage.save_user_profile(user_id, profile)
        print("✓ Profile created!")
    else:
        print("\n👋 Welcome back!")
        print(f"   First visit: {profile['history']['first_visit']}")
        print(f"   Last visit: {profile['history']['last_visit']}")
    
    print("\n" + "=" * 80)
    print("CONVERSATION MODE (type 'exit' to return to menu)")
    print("=" * 80)
    print("\nDietExpert AI: Hello! I'm your personal dietician and health expert.")
    print("How can I help you today?\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['exit', 'quit', 'back']:
            print("\n✓ Returning to main menu...\n")
            break
        
        if not user_input:
            continue
        
        # Save user message
        conversation.add_message(user_id, 'user', user_input)
        
        # In a real implementation, you would call the agent here
        # For this CLI demo, we'll provide a simulated response
        print("\nDietExpert AI: [Agent response would appear here]")
        print("               (In production, the ADK agent would process your message)")
        print("               and provide a personalized response based on the")
        print("               comprehensive instructions.)\n")


def view_profile(user_id: str):
    """View user profile"""
    storage = UserStorage()
    profile = storage.load_user_profile(user_id)
    
    if not profile:
        print("\n❌ User profile not found!")
        return
    
    print("\n" + "=" * 80)
    print("USER PROFILE")
    print("=" * 80)
    
    # Personal Info
    print("\n📋 PERSONAL INFORMATION:")
    pi = profile['personal_info']
    for key, value in pi.items():
        if value is not None:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Dietary Preferences
    print("\n🥗 DIETARY PREFERENCES:")
    dp = profile['dietary_preferences']
    for key, value in dp.items():
        if value:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Health Metrics
    print("\n📊 HEALTH METRICS:")
    hm = profile['health_metrics']
    for key, value in hm.items():
        if value is not None:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # Goals
    print("\n🎯 GOALS:")
    goals = profile['goals']
    for key, value in goals.items():
        if value:
            print(f"   {key.replace('_', ' ').title()}: {value}")
    
    # History Summary
    print("\n📅 HISTORY:")
    print(f"   First Visit: {profile['history']['first_visit']}")
    print(f"   Last Visit: {profile['history']['last_visit']}")
    print(f"   Progress Updates: {len(profile['history']['progress_updates'])}")
    print(f"   Diet Plans: {len(profile['history']['diet_plans'])}")
    print(f"   Exercise Plans: {len(profile['history']['exercise_plans'])}")
    
    print("=" * 80)


def view_conversation_history(user_id: str):
    """View conversation history"""
    conversation = ConversationMemory()
    history = conversation.get_conversation_history(user_id, limit=50)
    
    if not history:
        print("\n❌ No conversation history found!")
        return
    
    print("\n" + "=" * 80)
    print(f"CONVERSATION HISTORY (Last {len(history)} messages)")
    print("=" * 80)
    
    for msg in history:
        role = msg['role'].upper()
        content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
        timestamp = msg.get('timestamp', 'N/A')
        print(f"\n[{role}] - {timestamp}")
        print(f"{content}")
    
    print("=" * 80)


def calculate_metrics_interactive():
    """Interactive health metrics calculation"""
    print("\n" + "=" * 80)
    print("HEALTH METRICS CALCULATOR")
    print("=" * 80)
    
    try:
        age = int(input("\nAge (years): "))
        gender = input("Gender (male/female): ").strip()
        height_cm = float(input("Height (cm): "))
        weight_kg = float(input("Current weight (kg): "))
        target_kg = float(input("Target weight (kg): "))
        
        print("\nActivity Level Options:")
        print("1. Sedentary")
        print("2. Lightly Active")
        print("3. Moderately Active")
        print("4. Very Active")
        print("5. Extremely Active")
        activity_choice = input("Choose (1-5): ").strip()
        
        activity_map = {
            '1': 'sedentary',
            '2': 'lightly_active',
            '3': 'moderately_active',
            '4': 'very_active',
            '5': 'extremely_active'
        }
        activity = activity_map.get(activity_choice, 'moderately_active')
        
        print("\nGoal Options:")
        print("1. Weight Loss")
        print("2. Weight Gain / Muscle Building")
        print("3. Maintenance")
        goal_choice = input("Choose (1-3): ").strip()
        
        goal_map = {
            '1': 'weight_loss',
            '2': 'weight_gain',
            '3': 'maintenance'
        }
        goal = goal_map.get(goal_choice, 'weight_loss')
        
        # Calculate
        print("\n⏳ Calculating...")
        profile = calculate_complete_health_profile(
            age, gender, height_cm, weight_kg, target_kg, activity, goal
        )
        
        # Display results
        print("\n" + "=" * 80)
        print("RESULTS")
        print("=" * 80)
        
        print(f"\n📊 BMI: {profile['bmi']['value']} ({profile['bmi']['category']})")
        print(f"🔥 BMR: {profile['bmr']} calories/day")
        print(f"⚡ TDEE: {profile['tdee']} calories/day")
        print(f"🎯 Target Calories: {profile['calorie_plan']['target_calories']} calories/day")
        print(f"📉 Weekly Change: {profile['calorie_plan']['weekly_weight_change_kg']} kg/week")
        
        print("\n🍽️  MACRONUTRIENT TARGETS:")
        print(f"   Protein: {profile['macronutrients']['protein']['grams']}g "
              f"({profile['macronutrients']['protein']['percentage']}%)")
        print(f"   Carbs: {profile['macronutrients']['carbohydrates']['grams']}g "
              f"({profile['macronutrients']['carbohydrates']['percentage']}%)")
        print(f"   Fats: {profile['macronutrients']['fats']['grams']}g "
              f"({profile['macronutrients']['fats']['percentage']}%)")
        
        print(f"\n💧 Water Intake: {profile['water_intake']['liters']}L "
              f"({profile['water_intake']['glasses']} glasses/day)")
        
        print(f"\n⏰ TIMELINE:")
        print(f"   Estimated: {profile['timeline']['weeks']} weeks "
              f"({profile['timeline']['months']} months)")
        print(f"   Target Date: {profile['timeline']['target_date']}")
        
        print("=" * 80)
        
    except ValueError as e:
        print(f"\n❌ Error: Invalid input - {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def view_progress_updates(user_id: str):
    """View progress updates"""
    storage = UserStorage()
    profile = storage.load_user_profile(user_id)
    
    if not profile:
        print("\n❌ User profile not found!")
        return
    
    updates = profile['history']['progress_updates']
    
    if not updates:
        print("\n📊 No progress updates yet!")
        return
    
    print("\n" + "=" * 80)
    print(f"PROGRESS UPDATES ({len(updates)} total)")
    print("=" * 80)
    
    for i, update in enumerate(updates, 1):
        print(f"\n[Update #{i}] - {update.get('timestamp', 'N/A')}")
        for key, value in update.items():
            if key != 'timestamp':
                print(f"   {key.replace('_', ' ').title()}: {value}")
    
    print("=" * 80)


def list_all_users():
    """List all registered users"""
    storage = UserStorage()
    users = storage.get_all_users()
    
    if not users:
        print("\n📊 No users found!")
        return
    
    print("\n" + "=" * 80)
    print(f"ALL USERS ({len(users)} total)")
    print("=" * 80)
    
    for user_id in users:
        profile = storage.load_user_profile(user_id)
        if profile:
            name = profile['personal_info'].get('name', 'N/A')
            last_visit = profile['history'].get('last_visit', 'N/A')
            print(f"\n   User ID: {user_id}")
            print(f"   Last Visit: {last_visit}")
    
    print("=" * 80)


def main():
    """Main CLI loop"""
    print_header()
    
    # Get user ID
    user_id = input("Enter your User ID (or press Enter for 'demo_user'): ").strip()
    if not user_id:
        user_id = "demo_user"
    
    print(f"\n✓ Using User ID: {user_id}")
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 Thank you for using Diet Expert AI! Stay healthy! 💪\n")
            break
        elif choice == '1':
            start_conversation(user_id)
        elif choice == '2':
            view_profile(user_id)
        elif choice == '3':
            view_conversation_history(user_id)
        elif choice == '4':
            calculate_metrics_interactive()
        elif choice == '5':
            view_progress_updates(user_id)
        elif choice == '6':
            print("\n⏰ Reminder feature - Coming soon!")
            print("   (You can use set_reminders() from user_storage.py)")
        elif choice == '7':
            list_all_users()
        elif choice == '8':
            confirm = input(f"\n⚠️  Delete profile for {user_id}? (yes/no): ")
            if confirm.lower() == 'yes':
                storage = UserStorage()
                if storage.delete_user_profile(user_id):
                    print("✓ Profile deleted!")
                else:
                    print("❌ Failed to delete profile!")
        elif choice == '9':
            print("\n🚀 Running demo...")
            from example_usage import example_complete_user_flow
            example_complete_user_flow()
        else:
            print("\n❌ Invalid choice! Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Stay healthy! 💪\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)
