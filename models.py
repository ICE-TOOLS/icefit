from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, Literal
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

class UserRegisterModel(BaseModel):
    # Basic Information
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    
    # Personal Details
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    date_of_birth: datetime
    gender: Literal['male', 'female', 'other']
    
    # Physical Measurements
    height_cm: float = Field(..., gt=50, lt=300)
    weight_kg: float = Field(..., gt=20, lt=500)
    
    # Fitness Goals
    goal: Literal['lose_weight', 'gain_weight', 'maintain_weight', 'build_muscle', 'improve_endurance']
    target_weight_kg: Optional[float] = None
    target_date: Optional[datetime] = None
    
    # Activity Level
    activity_level: Literal['sedentary', 'light', 'moderate', 'active', 'very_active']
    
    # Gym Information
    gym_type: Literal['without_gym', 'home_garage', 'small_gym', 'medium_gym', 'big_gym']
    
    # Gamification
    day_streak: int = Field(default=0, ge=0)
    
    # Health Information
    medical_conditions: Optional[list[str]] = []
    allergies: Optional[list[str]] = []
    medications: Optional[list[str]] = []
    
    # Dietary Preferences
    dietary_restrictions: Optional[list[Literal['vegetarian', 'vegan', 'gluten_free', 'dairy_free', 'keto', 'paleo', 'halal', 'kosher']]] = []
    daily_calorie_goal: Optional[int] = None
    
    # Calculated Fields (will be set by backend)
    age: Optional[int] = None
    bmi: Optional[float] = None
    bmi_status: Optional[str] = None
    recommended_weight_change: Optional[float] = None
    recommended_daily_calories: Optional[int] = None
    bmr: Optional[float] = None  # Basal Metabolic Rate
    tdee: Optional[float] = None  # Total Daily Energy Expenditure
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @validator('target_weight_kg', always=True)
    def set_target_weight(cls, v, values):
        if v is not None:
            return v
        if 'goal' in values and 'weight_kg' in values:
            if values['goal'] == 'lose_weight':
                return values['weight_kg'] - 10
            elif values['goal'] == 'gain_weight':
                return values['weight_kg'] + 10
            elif values['goal'] == 'build_muscle':
                return values['weight_kg'] + 5
            else:
                return values['weight_kg']
        return None

    @validator('age', always=True)
    def calculate_age(cls, v, values):
        if v is not None:
            return v
        if 'date_of_birth' in values:
            today = datetime.now()
            dob = values['date_of_birth']
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return age
        return None

    @validator('created_at', always=True)
    def set_created_at(cls, v):
        return v or datetime.utcnow()

    @validator('updated_at', always=True)
    def set_updated_at(cls, v):
        return datetime.utcnow()

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    username: str
    password_hash: str
    
    # Personal Details
    first_name: str
    last_name: str
    date_of_birth: datetime
    gender: str
    age: int
    
    # Physical Measurements
    height_cm: float
    weight_kg: float
    
    # Fitness Goals
    goal: str
    target_weight_kg: Optional[float] = None
    target_date: Optional[datetime] = None
    
    # Activity Level
    activity_level: str
    
    # Gym Information
    gym_type: str
    
    # Gamification
    day_streak: int = 0
    
    # Health Information
    medical_conditions: list[str] = []
    allergies: list[str] = []
    medications: list[str] = []
    
    # Dietary Preferences
    dietary_restrictions: list[str] = []
    daily_calorie_goal: Optional[int] = None
    
    # Calculated Fields
    bmi: float
    bmi_status: str
    recommended_weight_change: float
    recommended_daily_calories: int
    bmr: float
    tdee: float
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserLoginModel(BaseModel):
    email: EmailStr
    password: str

class UserUpdateModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    weight_kg: Optional[float] = None
    goal: Optional[str] = None
    target_weight_kg: Optional[float] = None
    target_date: Optional[datetime] = None
    activity_level: Optional[str] = None
    gym_type: Optional[str] = None
    day_streak: Optional[int] = None
    medical_conditions: Optional[list[str]] = None
    allergies: Optional[list[str]] = None
    medications: Optional[list[str]] = None
    dietary_restrictions: Optional[list[str]] = None
    daily_calorie_goal: Optional[int] = None
    
    class Config:
        arbitrary_types_allowed = True
