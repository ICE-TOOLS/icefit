from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import UserRegisterModel, UserLoginModel, UserModel
from services.user_service import UserService, UserCalculationService
from services.auth_service import AuthService
from middleware.auth_middleware import get_current_user, get_current_user_id
from database import get_database
from datetime import datetime
from typing import Dict, Any

router = APIRouter()

@router.post("/register", response_model=Dict[str, Any])
async def register_user(
    user: UserRegisterModel,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Register a new user with comprehensive health metrics calculation
    
    This endpoint:
    - Validates user input
    - Calculates BMI, BMR, TDEE, and calorie recommendations
    - Stores user data securely in MongoDB
    - Returns user profile with health insights
    """
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        existing_username = await db.users.find_one({"username": user.username})
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Prepare user data for database
        user_doc = UserService.prepare_user_for_db(user)
        
        # Insert user into database
        result = await db.users.insert_one(user_doc)
        
        # Get the created user
        created_user = await db.users.find_one({"_id": result.inserted_id})
        
        # Prepare response
        response_data = UserService.get_user_response(created_user)
        
        # Generate JWT tokens
        tokens = AuthService.create_tokens(str(result.inserted_id), user.email)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "User registered successfully",
                "user": response_data,
                "tokens": tokens,
                "health_insights": {
                    "bmi_interpretation": get_bmi_interpretation(response_data['bmi_status']),
                    "calorie_guidance": get_calorie_guidance(response_data['goal'], response_data['recommended_daily_calories']),
                    "weight_guidance": get_weight_guidance(response_data['goal'], response_data['recommended_weight_change'])
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/login")
async def login_user(
    credentials: UserLoginModel,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Authenticate user login
    """
    try:
        # Find user by email
        user = await db.users.find_one({"email": credentials.email})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not UserService.verify_password(credentials.password, user['password_hash']):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Update last login
        await db.users.update_one(
            {"_id": user['_id']},
            {"$set": {"last_login": datetime.utcnow()}}
        )
        
        # Prepare response
        response_data = UserService.get_user_response(user)
        
        # Generate JWT tokens
        tokens = AuthService.create_tokens(str(user['_id']), user['email'])
        
        return JSONResponse(
            content={
                "message": "Login successful",
                "user": response_data,
                "tokens": tokens
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/profile")
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get authenticated user profile
    """
    try:
        # Prepare response from current authenticated user
        response_data = UserService.get_user_response(current_user)
        
        return JSONResponse(
            content={
                "user": response_data,
                "health_insights": {
                    "bmi_interpretation": get_bmi_interpretation(response_data['bmi_status']),
                    "calorie_guidance": get_calorie_guidance(response_data['goal'], response_data['recommended_daily_calories']),
                    "weight_guidance": get_weight_guidance(response_data['goal'], response_data['recommended_weight_change'])
                }
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.put("/profile")
async def update_user_profile(
    updates: dict,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Update authenticated user profile and recalculate health metrics if needed
    """
    try:
        from bson import ObjectId
        
        user_id = str(current_user['_id'])
        
        # Check if we need to recalculate metrics
        recalculate_metrics = any(key in updates for key in ['weight_kg', 'height_cm', 'age', 'gender', 'activity_level', 'goal'])
        
        if recalculate_metrics:
            # Update user data with new values
            user_data = dict(current_user)
            for key, value in updates.items():
                if key in user_data:
                    user_data[key] = value
            
            # Recalculate metrics
            metrics = UserCalculationService.calculate_all_metrics(user_data)
            updates.update(metrics)
        
        # Add updated timestamp
        updates['updated_at'] = datetime.utcnow()
        
        # Update user in database
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": updates}
        )
        
        # Get updated user
        updated_user = await db.users.find_one({"_id": ObjectId(user_id)})
        response_data = UserService.get_user_response(updated_user)
        
        return JSONResponse(
            content={
                "message": "Profile updated successfully",
                "user": response_data
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Helper functions for health insights
def get_bmi_interpretation(bmi_status: str) -> str:
    """Get BMI interpretation message"""
    interpretations = {
        "underweight": "Your BMI indicates you're underweight. Consider consulting with a healthcare provider about healthy weight gain strategies.",
        "normal": "Great! Your BMI is in the healthy range. Maintain your current lifestyle with regular exercise and balanced nutrition.",
        "overweight": "Your BMI indicates you're overweight. Consider a balanced approach with regular exercise and portion control.",
        "obese": "Your BMI indicates obesity. We recommend consulting with a healthcare provider for a comprehensive weight management plan."
    }
    return interpretations.get(bmi_status, "BMI status unknown")

def get_calorie_guidance(goal: str, recommended_calories: int) -> str:
    """Get calorie guidance message"""
    guidance = {
        "lose_weight": f"To lose weight safely, aim for {recommended_calories} calories per day. This creates a moderate deficit for sustainable weight loss.",
        "gain_weight": f"To gain weight healthily, aim for {recommended_calories} calories per day. Focus on nutrient-dense foods and strength training.",
        "build_muscle": f"To build muscle, aim for {recommended_calories} calories per day with adequate protein (1.6-2.2g per kg body weight).",
        "maintain_weight": f"To maintain your current weight, aim for {recommended_calories} calories per day.",
        "improve_endurance": f"For endurance training, aim for {recommended_calories} calories per day, focusing on carbohydrates for energy."
    }
    return guidance.get(goal, f"Aim for {recommended_calories} calories per day based on your goals.")

def get_weight_guidance(goal: str, recommended_change: float) -> str:
    """Get weight change guidance message"""
    if abs(recommended_change) < 1:
        return "Your current weight is in a healthy range for your height."
    
    if recommended_change > 0:
        return f"For optimal health, consider gaining {abs(recommended_change):.1f} kg through healthy nutrition and strength training."
    else:
        return f"For optimal health, consider losing {abs(recommended_change):.1f} kg through a balanced diet and regular exercise."