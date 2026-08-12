"""
User data storage and management for the Diet Expert AI system
Handles persistent storage of user profiles, conversation history, and progress tracking
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path


class UserStorage:
    """Manages user profile storage and retrieval"""
    
    def __init__(self, storage_dir: str = "user_data"):
        """
        Initialize user storage
        
        Args:
            storage_dir: Directory to store user data files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_user_file_path(self, user_id: str) -> Path:
        """Get the file path for a user's data"""
        return self.storage_dir / f"user_{user_id}.json"
    
    def save_user_profile(self, user_id: str, profile: Dict[str, Any]) -> bool:
        """
        Save user profile to storage
        
        Args:
            user_id: Unique identifier for the user
            profile: User profile dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update last visit timestamp
            profile['history']['last_visit'] = datetime.now().isoformat()
            
            # If this is first save, set first visit
            if profile['history']['first_visit'] is None:
                profile['history']['first_visit'] = datetime.now().isoformat()
            
            file_path = self._get_user_file_path(user_id)
            with open(file_path, 'w') as f:
                json.dump(profile, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving user profile: {e}")
            return False
    
    def load_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Load user profile from storage
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            User profile dictionary if found, None otherwise
        """
        try:
            file_path = self._get_user_file_path(user_id)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error loading user profile: {e}")
            return None
    
    def add_progress_update(self, user_id: str, update: Dict[str, Any]) -> bool:
        """
        Add a progress update to user's history
        
        Args:
            user_id: Unique identifier for the user
            update: Progress update dictionary (weight, measurements, feedback, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile = self.load_user_profile(user_id)
            if profile:
                update['timestamp'] = datetime.now().isoformat()
                profile['history']['progress_updates'].append(update)
                return self.save_user_profile(user_id, profile)
            return False
        except Exception as e:
            print(f"Error adding progress update: {e}")
            return False
    
    def add_diet_plan(self, user_id: str, diet_plan: Dict[str, Any]) -> bool:
        """
        Add a diet plan to user's history
        
        Args:
            user_id: Unique identifier for the user
            diet_plan: Diet plan dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile = self.load_user_profile(user_id)
            if profile:
                diet_plan['created_at'] = datetime.now().isoformat()
                profile['history']['diet_plans'].append(diet_plan)
                return self.save_user_profile(user_id, profile)
            return False
        except Exception as e:
            print(f"Error adding diet plan: {e}")
            return False
    
    def add_exercise_plan(self, user_id: str, exercise_plan: Dict[str, Any]) -> bool:
        """
        Add an exercise plan to user's history
        
        Args:
            user_id: Unique identifier for the user
            exercise_plan: Exercise plan dictionary
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile = self.load_user_profile(user_id)
            if profile:
                exercise_plan['created_at'] = datetime.now().isoformat()
                profile['history']['exercise_plans'].append(exercise_plan)
                return self.save_user_profile(user_id, profile)
            return False
        except Exception as e:
            print(f"Error adding exercise plan: {e}")
            return False
    
    def set_reminders(self, user_id: str, reminder_type: str, reminders: List[str]) -> bool:
        """
        Set reminders for the user
        
        Args:
            user_id: Unique identifier for the user
            reminder_type: Type of reminder ('meal_times', 'exercise_times', 'check_in_schedule')
            reminders: List of reminder times/schedules
            
        Returns:
            True if successful, False otherwise
        """
        try:
            profile = self.load_user_profile(user_id)
            if profile and reminder_type in profile['reminders']:
                profile['reminders'][reminder_type] = reminders
                return self.save_user_profile(user_id, profile)
            return False
        except Exception as e:
            print(f"Error setting reminders: {e}")
            return False
    
    def get_all_users(self) -> List[str]:
        """
        Get list of all user IDs
        
        Returns:
            List of user IDs
        """
        user_files = self.storage_dir.glob("user_*.json")
        return [f.stem.replace("user_", "") for f in user_files]
    
    def delete_user_profile(self, user_id: str) -> bool:
        """
        Delete a user's profile
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_user_file_path(user_id)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting user profile: {e}")
            return False


class ConversationMemory:
    """Manages conversation history for context retention"""
    
    def __init__(self, storage_dir: str = "conversation_data"):
        """
        Initialize conversation memory
        
        Args:
            storage_dir: Directory to store conversation data
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
    
    def _get_conversation_file_path(self, user_id: str) -> Path:
        """Get the file path for a user's conversation history"""
        return self.storage_dir / f"conversation_{user_id}.json"
    
    def add_message(self, user_id: str, role: str, content: str) -> bool:
        """
        Add a message to conversation history
        
        Args:
            user_id: Unique identifier for the user
            role: Message role ('user' or 'assistant')
            content: Message content
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_conversation_file_path(user_id)
            
            # Load existing conversation
            conversation = []
            if file_path.exists():
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
            
            # Add new message
            conversation.append({
                'role': role,
                'content': content,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 100 messages to manage storage
            if len(conversation) > 100:
                conversation = conversation[-100:]
            
            # Save updated conversation
            with open(file_path, 'w') as f:
                json.dump(conversation, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error adding message to conversation: {e}")
            return False
    
    def get_conversation_history(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get conversation history for a user
        
        Args:
            user_id: Unique identifier for the user
            limit: Maximum number of messages to return
            
        Returns:
            List of conversation messages
        """
        try:
            file_path = self._get_conversation_file_path(user_id)
            if file_path.exists():
                with open(file_path, 'r') as f:
                    conversation = json.load(f)
                return conversation[-limit:] if len(conversation) > limit else conversation
            return []
        except Exception as e:
            print(f"Error getting conversation history: {e}")
            return []
    
    def clear_conversation(self, user_id: str) -> bool:
        """
        Clear conversation history for a user
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self._get_conversation_file_path(user_id)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error clearing conversation: {e}")
            return False
