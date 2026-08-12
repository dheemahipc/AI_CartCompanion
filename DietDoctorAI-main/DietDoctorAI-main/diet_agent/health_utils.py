"""
Health and fitness calculation utilities for the Diet Expert AI system
Provides functions for BMI, BMR, TDEE, macro calculations, and more
"""

from typing import Dict, Any, Tuple
from datetime import datetime, timedelta


def calculate_bmi(weight_kg: float, height_cm: float) -> Tuple[float, str]:
    """
    Calculate Body Mass Index (BMI) and category
    
    Args:
        weight_kg: Weight in kilograms
        height_cm: Height in centimeters
        
    Returns:
        Tuple of (BMI value, BMI category)
    """
    height_m = height_cm / 100
    bmi = weight_kg / (height_m ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
    elif 25 <= bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return round(bmi, 2), category


def calculate_bmr(age: int, gender: str, height_cm: float, weight_kg: float) -> float:
    """
    Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
    
    Args:
        age: Age in years
        gender: Gender ('male', 'female', or other variations)
        height_cm: Height in centimeters
        weight_kg: Weight in kilograms
        
    Returns:
        BMR in calories per day
    """
    if gender.lower() in ['male', 'm', 'man', 'boy']:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
    else:  # female or other
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
    
    return round(bmr, 2)


def calculate_tdee(bmr: float, activity_level: str) -> float:
    """
    Calculate Total Daily Energy Expenditure (TDEE)
    
    Args:
        bmr: Basal Metabolic Rate
        activity_level: Activity level description
        
    Returns:
        TDEE in calories per day
    """
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly active': 1.375,
        'lightly_active': 1.375,
        'moderately active': 1.55,
        'moderately_active': 1.55,
        'very active': 1.725,
        'very_active': 1.725,
        'extremely active': 1.9,
        'extremely_active': 1.9,
        'athlete': 1.9,
    }
    
    # Normalize activity level string
    activity_key = activity_level.lower().strip()
    multiplier = activity_multipliers.get(activity_key, 1.55)  # Default to moderately active
    
    tdee = bmr * multiplier
    return round(tdee, 2)


def calculate_target_calories(tdee: float, goal: str, aggressive: bool = False) -> Dict[str, float]:
    """
    Calculate target calorie intake based on goal
    
    Args:
        tdee: Total Daily Energy Expenditure
        goal: Fitness goal ('weight_loss', 'weight_gain', 'maintenance', 'muscle_building')
        aggressive: Whether to use aggressive calorie deficit/surplus
        
    Returns:
        Dictionary with target calories and weekly weight change estimate
    """
    goal_lower = goal.lower()
    
    if 'loss' in goal_lower or 'lose' in goal_lower or 'cut' in goal_lower:
        deficit = 750 if aggressive else 500
        target = tdee - deficit
        weekly_change = -0.5 if not aggressive else -0.75
        goal_type = "Weight Loss"
        
    elif 'gain' in goal_lower or 'bulk' in goal_lower or 'muscle' in goal_lower:
        surplus = 500 if aggressive else 350
        target = tdee + surplus
        weekly_change = 0.5 if aggressive else 0.35
        goal_type = "Weight Gain / Muscle Building"
        
    else:  # maintenance
        target = tdee
        weekly_change = 0
        goal_type = "Maintenance"
    
    return {
        'target_calories': round(target, 2),
        'weekly_weight_change_kg': round(weekly_change, 2),
        'goal_type': goal_type,
        'daily_deficit_surplus': round(target - tdee, 2)
    }


def calculate_macros(target_calories: float, weight_kg: float, goal: str) -> Dict[str, Any]:
    """
    Calculate macronutrient targets (protein, carbs, fats)
    
    Args:
        target_calories: Target daily calorie intake
        weight_kg: Body weight in kilograms
        goal: Fitness goal
        
    Returns:
        Dictionary with macro targets in grams and percentages
    """
    goal_lower = goal.lower()
    
    # Protein targets based on goal
    if 'loss' in goal_lower or 'cut' in goal_lower:
        protein_g_per_kg = 2.2  # Higher protein for muscle preservation
    elif 'gain' in goal_lower or 'muscle' in goal_lower or 'bulk' in goal_lower:
        protein_g_per_kg = 2.0  # High protein for muscle building
    else:
        protein_g_per_kg = 1.8  # Moderate protein for maintenance
    
    # Calculate protein
    protein_g = weight_kg * protein_g_per_kg
    protein_cal = protein_g * 4
    
    # Fat targets (generally 0.8-1g per kg body weight)
    fat_g_per_kg = 1.0 if 'gain' in goal_lower else 0.9
    fat_g = weight_kg * fat_g_per_kg
    fat_cal = fat_g * 9
    
    # Remaining calories from carbohydrates
    carb_cal = target_calories - protein_cal - fat_cal
    carb_g = carb_cal / 4
    
    # Calculate percentages
    protein_pct = (protein_cal / target_calories) * 100
    fat_pct = (fat_cal / target_calories) * 100
    carb_pct = (carb_cal / target_calories) * 100
    
    return {
        'protein': {
            'grams': round(protein_g, 1),
            'calories': round(protein_cal, 1),
            'percentage': round(protein_pct, 1)
        },
        'carbohydrates': {
            'grams': round(max(carb_g, 0), 1),  # Ensure non-negative
            'calories': round(max(carb_cal, 0), 1),
            'percentage': round(carb_pct, 1)
        },
        'fats': {
            'grams': round(fat_g, 1),
            'calories': round(fat_cal, 1),
            'percentage': round(fat_pct, 1)
        },
        'total_calories': round(target_calories, 1)
    }


def calculate_water_intake(weight_kg: float, activity_level: str) -> Dict[str, float]:
    """
    Calculate recommended daily water intake
    
    Args:
        weight_kg: Body weight in kilograms
        activity_level: Activity level
        
    Returns:
        Dictionary with water intake in liters and glasses
    """
    # Base calculation: 30-35ml per kg body weight
    base_ml = weight_kg * 35
    
    # Adjust for activity level
    if 'very' in activity_level.lower() or 'extremely' in activity_level.lower():
        base_ml += 500  # Add 500ml for high activity
    elif 'moderately' in activity_level.lower():
        base_ml += 250  # Add 250ml for moderate activity
    
    liters = base_ml / 1000
    glasses = base_ml / 250  # Assuming 250ml per glass
    
    return {
        'liters': round(liters, 1),
        'glasses': round(glasses, 0),
        'ml': round(base_ml, 0)
    }


def estimate_goal_timeline(current_weight: float, target_weight: float, 
                          weekly_change: float) -> Dict[str, Any]:
    """
    Estimate timeline to reach weight goal
    
    Args:
        current_weight: Current weight in kg
        target_weight: Target weight in kg
        weekly_change: Expected weekly weight change in kg (negative for loss)
        
    Returns:
        Dictionary with timeline estimates
    """
    if weekly_change == 0:
        return {
            'weeks': 0,
            'months': 0,
            'days': 0,
            'message': "Maintenance mode - no weight change goal"
        }
    
    weight_diff = abs(target_weight - current_weight)
    weeks = weight_diff / abs(weekly_change)
    months = weeks / 4.33
    days = weeks * 7
    
    target_date = datetime.now() + timedelta(days=days)
    
    return {
        'weeks': round(weeks, 1),
        'months': round(months, 1),
        'days': round(days, 0),
        'target_date': target_date.strftime('%B %d, %Y'),
        'weight_to_change_kg': round(weight_diff, 1),
        'is_realistic': weeks >= 4  # At least 4 weeks recommended
    }


def calculate_ideal_weight_range(height_cm: float, gender: str) -> Dict[str, float]:
    """
    Calculate ideal weight range based on BMI 18.5-24.9
    
    Args:
        height_cm: Height in centimeters
        gender: Gender
        
    Returns:
        Dictionary with weight range
    """
    height_m = height_cm / 100
    
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    mid_weight = (min_weight + max_weight) / 2
    
    return {
        'minimum_kg': round(min_weight, 1),
        'maximum_kg': round(max_weight, 1),
        'ideal_kg': round(mid_weight, 1)
    }


def calculate_body_fat_percentage_estimate(bmi: float, age: int, gender: str) -> Dict[str, Any]:
    """
    Estimate body fat percentage from BMI (rough estimation)
    Note: This is an estimate. DEXA scan or other methods are more accurate.
    
    Args:
        bmi: Body Mass Index
        age: Age in years
        gender: Gender
        
    Returns:
        Dictionary with body fat estimate and category
    """
    # Using Deurenberg formula (rough estimate)
    if gender.lower() in ['male', 'm', 'man']:
        bf_pct = (1.20 * bmi) + (0.23 * age) - 16.2
        categories = {
            'Essential fat': (2, 5),
            'Athletes': (6, 13),
            'Fitness': (14, 17),
            'Average': (18, 24),
            'Obese': (25, 100)
        }
    else:
        bf_pct = (1.20 * bmi) + (0.23 * age) - 5.4
        categories = {
            'Essential fat': (10, 13),
            'Athletes': (14, 20),
            'Fitness': (21, 24),
            'Average': (25, 31),
            'Obese': (32, 100)
        }
    
    # Determine category
    category = 'Unknown'
    for cat_name, (low, high) in categories.items():
        if low <= bf_pct <= high:
            category = cat_name
            break
    
    return {
        'body_fat_percentage': round(bf_pct, 1),
        'category': category,
        'note': 'This is an estimate. For accurate measurements, consider DEXA scan or body composition analysis.'
    }


def calculate_complete_health_profile(age: int, gender: str, height_cm: float, 
                                     weight_kg: float, target_weight: float,
                                     activity_level: str, goal: str) -> Dict[str, Any]:
    """
    Calculate complete health profile with all metrics
    
    Args:
        age: Age in years
        gender: Gender
        height_cm: Height in centimeters
        weight_kg: Current weight in kilograms
        target_weight: Target weight in kilograms
        activity_level: Activity level
        goal: Fitness goal
        
    Returns:
        Comprehensive dictionary with all health metrics
    """
    bmi, bmi_category = calculate_bmi(weight_kg, height_cm)
    bmr = calculate_bmr(age, gender, height_cm, weight_kg)
    tdee = calculate_tdee(bmr, activity_level)
    calorie_targets = calculate_target_calories(tdee, goal)
    macros = calculate_macros(calorie_targets['target_calories'], weight_kg, goal)
    water = calculate_water_intake(weight_kg, activity_level)
    timeline = estimate_goal_timeline(weight_kg, target_weight, 
                                     calorie_targets['weekly_weight_change_kg'])
    ideal_weight = calculate_ideal_weight_range(height_cm, gender)
    body_fat = calculate_body_fat_percentage_estimate(bmi, age, gender)
    
    return {
        'basic_metrics': {
            'age': age,
            'gender': gender,
            'height_cm': height_cm,
            'current_weight_kg': weight_kg,
            'target_weight_kg': target_weight,
        },
        'bmi': {
            'value': bmi,
            'category': bmi_category
        },
        'bmr': bmr,
        'tdee': tdee,
        'calorie_plan': calorie_targets,
        'macronutrients': macros,
        'water_intake': water,
        'timeline': timeline,
        'ideal_weight_range': ideal_weight,
        'body_composition': body_fat,
        'activity_level': activity_level
    }
