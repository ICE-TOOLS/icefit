# ICEFIT FastAPI Backend

A comprehensive fitness and health tracking API with advanced user management, BMI calculations, and personalized health insights.

## Features

- **User Registration & Authentication**: Secure user registration with password hashing
- **Comprehensive Health Metrics**: BMI, BMR, TDEE calculations
- **Personalized Recommendations**: Calorie goals and weight management guidance
- **Modular Architecture**: Clean, organized codebase with proper separation of concerns
- **MongoDB Integration**: Robust data storage with Motor async driver
- **API Versioning**: RESTful API with proper versioning structure

## Setup

1. Create a virtual environment (already created as `venv`).
2. Install dependencies:
   ```powershell
   .\venv\Scripts\python.exe -m pip install -r requirements.txt
   ```
3. Configure your MongoDB connection in the `.env` file:
   ```
   MONGODB_URL=mongodb://localhost:27017
   DB_NAME=icefit
   ```

## Running the Server

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

The server will start at http://127.0.0.1:8000

## API Documentation

Once the server is running, visit:
- **Interactive API Docs**: http://127.0.0.1:8000/docs
- **Alternative Docs**: http://127.0.0.1:8000/redoc

## API Endpoints

### Health Check
- `GET /` - Main health check
- `GET /api/health` - API health check

### Authentication (v1)
All auth endpoints are prefixed with `/api/v1/auth/`

- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - User login
- `GET /api/v1/auth/profile/{user_id}` - Get user profile
- `PUT /api/v1/auth/profile/{user_id}` - Update user profile

## User Registration

The registration endpoint accepts comprehensive user data including:

### Required Fields
- **Basic Info**: email, username, password, first_name, last_name
- **Personal**: date_of_birth, gender
- **Physical**: height_cm, weight_kg
- **Goals**: goal (lose_weight, gain_weight, maintain_weight, build_muscle, improve_endurance)
- **Activity**: activity_level (sedentary, light, moderate, active, very_active)

### Optional Fields
- **Health**: medical_conditions, allergies, medications
- **Diet**: dietary_restrictions, daily_calorie_goal
- **Goals**: target_weight_kg, target_date

### Calculated Metrics
The system automatically calculates:
- **BMI** and status classification
- **BMR** (Basal Metabolic Rate) using Mifflin-St Jeor equation
- **TDEE** (Total Daily Energy Expenditure)
- **Recommended daily calories** based on goals
- **Weight change recommendations** for optimal health

## Example Registration Request

```json
{
  "email": "user@example.com",
  "username": "fitness_user",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "date_of_birth": "1990-01-15T00:00:00",
  "gender": "male",
  "height_cm": 175,
  "weight_kg": 80,
  "goal": "lose_weight",
  "activity_level": "moderate",
  "target_weight_kg": 75,
  "dietary_restrictions": ["vegetarian"]
}
```
## Health Insights

The API provides personalized health insights including:

- **BMI Interpretation**: Detailed explanation of BMI status
- **Calorie Guidance**: Personalized daily calorie recommendations
- **Weight Guidance**: Safe weight change recommendations
- **Metabolic Information**: BMR and TDEE for better understanding

## Security Features

- Password hashing using bcrypt
- Input validation with Pydantic
- Email validation
- Secure database operations

## Development

The codebase follows modern Python practices:
- Type hints throughout
- Modular architecture
- Separation of concerns
- Comprehensive error handling
- Async/await for database operations
