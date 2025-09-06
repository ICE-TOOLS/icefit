import google.generativeai as genai
import json
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from models.meal_models import WeeklyMealPlan, DayMealPlan, MealItem
from datetime import datetime, date, timedelta

load_dotenv()

class GeminiMealPlanService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def create_meal_plan_prompt(self, user_data: Dict[str, Any], preferences: Dict[str, Any]) -> str:
        """
        Create a comprehensive prompt for Gemini AI to generate meal plans
        """
        prompt = f"""
You are a professional nutritionist and meal planning expert. Create a detailed 7-day meal plan for a user with the following profile:

**USER PROFILE:**
- Age: {user_data.get('age', 'N/A')}
- Gender: {user_data.get('gender', 'N/A')}
- Weight: {user_data.get('weight_kg', 'N/A')} kg
- Height: {user_data.get('height_cm', 'N/A')} cm
- BMI: {user_data.get('bmi', 'N/A')}
- Activity Level: {user_data.get('activity_level', 'N/A')}
- Fitness Goal: {user_data.get('goal', 'N/A')}
- Target Weight: {user_data.get('target_weight_kg', 'N/A')} kg
- Daily Calorie Goal: {user_data.get('recommended_daily_calories', 'N/A')} calories
- BMR: {user_data.get('bmr', 'N/A')} calories
- TDEE: {user_data.get('tdee', 'N/A')} calories
- Gym Type: {user_data.get('gym_type', 'N/A')}

**DIETARY PREFERENCES & RESTRICTIONS:**
- Dietary Restrictions: {user_data.get('dietary_restrictions', [])}
- Medical Conditions: {user_data.get('medical_conditions', [])}
- Allergies: {user_data.get('allergies', [])}
- Cuisine Preferences: {preferences.get('cuisine_preferences', [])}
- Cooking Time Preference: {preferences.get('cooking_time_preference', 'moderate')}
- Budget Level: {preferences.get('budget_level', 'moderate')}

**REQUIREMENTS:**
1. Create a complete 7-day meal plan (Monday to Sunday)
2. Each day should include: breakfast, lunch, dinner, and 1-2 healthy snacks
3. Each meal should include:
   - Name of the dish
   - Estimated calories
   - Protein content (grams)
   - Carbohydrate content (grams)
   - Fat content (grams)
   - Fiber content (grams)
   - Brief description
   - Preparation time (minutes)
   - List of main ingredients
   - Simple cooking instructions

4. Ensure the daily calorie intake aligns with the user's goals
5. Provide variety throughout the week
6. Consider the user's activity level and gym type for pre/post workout meals
7. Respect all dietary restrictions and allergies
8. Include seasonal and accessible ingredients

**OUTPUT FORMAT:**
Please provide the response in valid JSON format with the following structure:

{{
  "monday": {{
    "breakfast": [
      {{
        "name": "Meal Name",
        "calories": 400,
        "protein": 25.0,
        "carbs": 45.0,
        "fat": 12.0,
        "fiber": 8.0,
        "description": "Brief description",
        "preparation_time": 15,
        "ingredients": ["ingredient1", "ingredient2"],
        "instructions": "Step by step instructions"
      }}
    ],
    "lunch": [...],
    "dinner": [...],
    "snacks": [...],
    "total_calories": 2000,
    "total_protein": 120.0,
    "total_carbs": 250.0,
    "total_fat": 65.0
  }},
  "tuesday": {{ ... }},
  "wednesday": {{ ... }},
  "thursday": {{ ... }},
  "friday": {{ ... }},
  "saturday": {{ ... }},
  "sunday": {{ ... }}
}}

Ensure the JSON is valid and complete. Focus on creating nutritious, balanced, and enjoyable meals that support the user's fitness goals.
"""
        return prompt
    
    async def generate_meal_plan(self, user_data: Dict[str, Any], preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a weekly meal plan using Gemini AI
        """
        try:
            prompt = self.create_meal_plan_prompt(user_data, preferences)
            
            response = self.model.generate_content(prompt)
            
            # Extract JSON from response
            response_text = response.text
            
            # Clean the response to extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                raise ValueError("No valid JSON found in response")
            
            # Parse JSON
            meal_plan_data = json.loads(json_text)
            
            return meal_plan_data
            
        except Exception as e:
            raise Exception(f"Failed to generate meal plan: {str(e)}")
    
    def create_weekly_meal_plan_model(self, user_id: str, meal_plan_data: Dict[str, Any]) -> WeeklyMealPlan:
        """
        Convert Gemini response to WeeklyMealPlan model
        """
        try:
            # Get the start of current week (Monday)
            today = date.today()
            days_since_monday = today.weekday()
            week_start = today - timedelta(days=days_since_monday)
            
            # Convert each day's data to DayMealPlan
            days = {}
            for day_name in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
                day_data = meal_plan_data.get(day_name, {})
                
                # Convert meals to MealItem objects
                breakfast = [MealItem(**meal) for meal in day_data.get('breakfast', [])]
                lunch = [MealItem(**meal) for meal in day_data.get('lunch', [])]
                dinner = [MealItem(**meal) for meal in day_data.get('dinner', [])]
                snacks = [MealItem(**meal) for meal in day_data.get('snacks', [])]
                
                days[day_name] = DayMealPlan(
                    breakfast=breakfast,
                    lunch=lunch,
                    dinner=dinner,
                    snacks=snacks,
                    total_calories=day_data.get('total_calories', 0),
                    total_protein=day_data.get('total_protein', 0.0),
                    total_carbs=day_data.get('total_carbs', 0.0),
                    total_fat=day_data.get('total_fat', 0.0)
                )
            
            # Create WeeklyMealPlan
            weekly_plan = WeeklyMealPlan(
                user_id=user_id,
                week_start_date=week_start,
                **days
            )
            
            return weekly_plan
            
        except Exception as e:
            raise Exception(f"Failed to create meal plan model: {str(e)}")