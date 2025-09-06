from datetime import datetime
from typing import Dict, Any
import bcrypt
from models import UserRegisterModel, UserModel

class UserCalculationService:
    """Service for calculating user health metrics"""
    
    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """Calculate Body Mass Index"""
        height_m = height_cm / 100
        return round(weight_kg / (height_m ** 2), 2)
    
    @staticmethod
    def get_bmi_status(bmi: float) -> str:
        """Get BMI status category"""
        if bmi < 18.5:
            return "underweight"
        elif 18.5 <= bmi < 25:
            return "normal"
        elif 25 <= bmi < 30:
            return "overweight"
        else:
            return "obese"
    
    @staticmethod
    def calculate_recommended_weight(height_cm: float, bmi_status: str) -> float:
        """Calculate recommended weight based on healthy BMI range"""
        height_m = height_cm / 100
        
        if bmi_status in ["underweight"]:
            # Target BMI of 20 (middle of healthy range)
            return round(20 * (height_m ** 2), 2)
        elif bmi_status == "normal":
            # Already in healthy range, no change needed
            return 0
        else:  # overweight or obese
            # Target BMI of 24 (upper healthy range)
            return round(24 * (height_m ** 2), 2)
    
    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:  # female or other
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        
        return round(bmr, 2)
    
    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        multiplier = activity_multipliers.get(activity_level, 1.2)
        return round(bmr * multiplier, 2)
    
    @staticmethod
    def calculate_calorie_goal(tdee: float, goal: str, target_weight_kg: float, current_weight_kg: float) -> int:
        """Calculate daily calorie goal based on fitness goal"""
        if goal == 'lose_weight':
            # Create a deficit of 500-750 calories per day for 1-1.5 lbs per week
            weight_to_lose = current_weight_kg - target_weight_kg
            if weight_to_lose > 10:  # More aggressive deficit for larger weight loss
                return int(tdee - 750)
            else:
                return int(tdee - 500)
        elif goal == 'gain_weight' or goal == 'build_muscle':
            # Create a surplus of 300-500 calories per day
            return int(tdee + 400)
        else:  # maintain_weight or improve_endurance
            return int(tdee)
    
    @classmethod
    def calculate_all_metrics(cls, user_data) -> Dict[str, Any]:
        """Calculate all health metrics for a user"""
        # Handle both UserRegisterModel and dict inputs
        if hasattr(user_data, 'weight_kg'):
            weight_kg = user_data.weight_kg
            height_cm = user_data.height_cm
            age = user_data.age
            gender = user_data.gender
            activity_level = user_data.activity_level
            goal = user_data.goal
            target_weight_kg = user_data.target_weight_kg
        else:
            weight_kg = user_data['weight_kg']
            height_cm = user_data['height_cm']
            age = user_data['age']
            gender = user_data['gender']
            activity_level = user_data['activity_level']
            goal = user_data['goal']
            target_weight_kg = user_data.get('target_weight_kg')
        
        # Calculate BMI
        bmi = cls.calculate_bmi(weight_kg, height_cm)
        bmi_status = cls.get_bmi_status(bmi)
        
        # Calculate recommended weight
        recommended_weight = cls.calculate_recommended_weight(height_cm, bmi_status)
        recommended_weight_change = recommended_weight - weight_kg if recommended_weight != 0 else 0
        
        # Calculate BMR and TDEE
        bmr = cls.calculate_bmr(weight_kg, height_cm, age, gender)
        tdee = cls.calculate_tdee(bmr, activity_level)
        
        # Calculate calorie goal
        target_weight = target_weight_kg or weight_kg
        recommended_calories = cls.calculate_calorie_goal(tdee, goal, target_weight, weight_kg)
        
        return {
            'bmi': bmi,
            'bmi_status': bmi_status,
            'recommended_weight_change': round(recommended_weight_change, 2),
            'bmr': bmr,
            'tdee': tdee,
            'recommended_daily_calories': recommended_calories
        }

class UserService:
    """Service for user operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def prepare_user_for_db(user_data: UserRegisterModel) -> Dict[str, Any]:
        """Prepare user data for database insertion"""
        # Calculate all health metrics
        metrics = UserCalculationService.calculate_all_metrics(user_data)
        
        # Hash password
        password_hash = UserService.hash_password(user_data.password)
        
        # Prepare user document
        user_doc = {
            'email': user_data.email,
            'username': user_data.username,
            'password_hash': password_hash,
            'first_name': user_data.first_name,
            'last_name': user_data.last_name,
            'date_of_birth': user_data.date_of_birth,
            'gender': user_data.gender,
            'age': user_data.age,
            'height_cm': user_data.height_cm,
            'weight_kg': user_data.weight_kg,
            'goal': user_data.goal,
            'target_weight_kg': user_data.target_weight_kg,
            'target_date': user_data.target_date,
            'activity_level': user_data.activity_level,
            'medical_conditions': user_data.medical_conditions or [],
            'allergies': user_data.allergies or [],
            'medications': user_data.medications or [],
            'dietary_restrictions': user_data.dietary_restrictions or [],
            'daily_calorie_goal': user_data.daily_calorie_goal,
            'bmi': metrics['bmi'],
            'bmi_status': metrics['bmi_status'],
            'recommended_weight_change': metrics['recommended_weight_change'],
            'recommended_daily_calories': metrics['recommended_daily_calories'],
            'bmr': metrics['bmr'],
            'tdee': metrics['tdee'],
            'created_at': user_data.created_at,
            'updated_at': user_data.updated_at,
            'is_active': True
        }
        
        return user_doc
    
    @staticmethod
    def get_user_response(user_doc: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare user data for API response (exclude sensitive info)"""
        response_data = user_doc.copy()
        # Remove sensitive information
        response_data.pop('password_hash', None)
        response_data.pop('_id', None)
        
        return response_data