from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, date
from bson import ObjectId
from models import PyObjectId

class MealItem(BaseModel):
    name: str
    calories: int
    protein: float  # grams
    carbs: float    # grams
    fat: float      # grams
    fiber: Optional[float] = None
    description: Optional[str] = None
    preparation_time: Optional[int] = None  # minutes
    ingredients: List[str] = []
    instructions: Optional[str] = None

class DayMealPlan(BaseModel):
    breakfast: List[MealItem]
    lunch: List[MealItem]
    dinner: List[MealItem]
    snacks: List[MealItem] = []
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float

class WeeklyMealPlan(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    week_start_date: date
    monday: DayMealPlan
    tuesday: DayMealPlan
    wednesday: DayMealPlan
    thursday: DayMealPlan
    friday: DayMealPlan
    saturday: DayMealPlan
    sunday: DayMealPlan
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MealPlanRequest(BaseModel):
    dietary_preferences: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    cuisine_preferences: Optional[List[str]] = []
    cooking_time_preference: Literal['quick', 'moderate', 'elaborate'] = 'moderate'
    budget_level: Literal['budget', 'moderate', 'premium'] = 'moderate'
    
class DayProgress(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    user_id: PyObjectId
    date: date
    meal_plan_id: PyObjectId
    breakfast_completed: bool = False
    lunch_completed: bool = False
    dinner_completed: bool = False
    snacks_completed: bool = False
    day_fully_completed: bool = False
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class MealCompletionRequest(BaseModel):
    meal_type: Literal['breakfast', 'lunch', 'dinner', 'snacks']
    completed: bool = True