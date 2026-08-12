"""
Diet Expert AI - Comprehensive Health & Fitness Agentic System

A sophisticated AI-powered dietician and health expert system built with Google's ADK.
Provides personalized nutrition planning, exercise guidance, and ongoing health coaching.
"""

__version__ = "1.0.0"
__author__ = "Diet Expert AI Team"

# Import main agent
from .agent import root_agent, USER_PROFILE_TEMPLATE, calculate_health_metrics

# Import storage classes
from .user_storage import UserStorage, ConversationMemory

# Import health utilities
from .health_utils import (
    calculate_bmi,
    calculate_bmr,
    calculate_tdee,
    calculate_target_calories,
    calculate_macros,
    calculate_water_intake,
    estimate_goal_timeline,
    calculate_ideal_weight_range,
    calculate_body_fat_percentage_estimate,
    calculate_complete_health_profile,
)

__all__ = [
    # Agent
    'root_agent',
    'USER_PROFILE_TEMPLATE',
    'calculate_health_metrics',
    
    # Storage
    'UserStorage',
    'ConversationMemory',
    
    # Health Utilities
    'calculate_bmi',
    'calculate_bmr',
    'calculate_tdee',
    'calculate_target_calories',
    'calculate_macros',
    'calculate_water_intake',
    'estimate_goal_timeline',
    'calculate_ideal_weight_range',
    'calculate_body_fat_percentage_estimate',
    'calculate_complete_health_profile',
]
