from fastapi import FastAPI
from main import calculate_tdee, calculate_plan
from database import insert_user, insert_plan, get_user_by_email,get_plan_by_user_id, get_user_by_id, create_connection


app = FastAPI()

@app.get("/")
def root():
    return {"message": "Git Shred API is running"}

## endpoint creation
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import date
from main import calculate_tdee, calculate_plan
from database import insert_user, insert_plan, get_user_by_email, get_plan_by_user_id

app = FastAPI()

## ── request models ──────────────────────────────────────────────
class UserCreate(BaseModel):
    email: str
    age: int
    sex: int
    height_in: int
    weight: float
    activity_level: int
    goal_weight: float
    weeks_to_goal: int
    checkin_day: int

class LoginRequest(BaseModel):
    email: str

## ── endpoints ───────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "Git Shred API is running"}

@app.post("/create-user")
def create_user(user: UserCreate):
    ## check if user already exists
    existing = get_user_by_email(user.email.strip().lower())
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_data = {
        "email": user.email.strip().lower(),
        "age": user.age,
        "sex": user.sex,
        "height_in": user.height_in,
        "weight": user.weight,
        "activity_level": user.activity_level,
        "goal_weight": user.goal_weight,
        "weeks_to_goal": user.weeks_to_goal,
        "checkin_day": user.checkin_day,
        "start_date": date.today()
    }

    tdee = calculate_tdee(user_data)
    plan_data = calculate_plan(user_data, tdee)
    user_id = insert_user(user_data)
    insert_plan(plan_data, user_id)

    return {
        "message": "Plan created successfully",
        "user_id": user_id,
        "plan": plan_data
    }

@app.post("/login")
def login(request: LoginRequest):
    user = get_user_by_email(request.email.strip().lower())
    if not user:
        raise HTTPException(status_code=404, detail="No account found with that email")
    
    user_id = user[0]
    plan = get_plan_by_user_id(user_id)

    return {
        "user_id": user_id,
        "email": user[1],
        "plan": plan
    }

from checkin import calculate_checkin
from engine import run_engine
from database import insert_checkin, update_plan, get_last_checkin

## ── additional request models ────────────────────────────────────

class CheckinRequest(BaseModel):
    user_id: int
    avg_weight_lbs: float
    days_tracked: int
    avg_step_count: int
    strength_subj: int
    fatigue_subj: int
    days_adherent: int
    calories_over: float | None = None
    off_the_rails: int = 0

## ── endpoints ────────────────────────────────────────────────────

@app.post("/checkin")
def checkin(request: CheckinRequest):
    user = get_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    plan_data = get_plan_by_user_id(request.user_id)
    if not plan_data:
        raise HTTPException(status_code=404, detail="No plan found")

    user_data = {
        "age": user[3],
        "sex": user[4],
        "height_in": user[5],
        "weight": user[6],
        "activity_level": user[7],
        "start_date": user[2],
        "checkin_day": user[8]
    }

    checkin_data = {
        "user_id": request.user_id,
        "check_in_date": date.today(),
        "avg_weight_lbs": request.avg_weight_lbs,
        "days_tracked": request.days_tracked,
        "avg_step_count": request.avg_step_count,
        "strength_subj": request.strength_subj,
        "fatigue_subj": request.fatigue_subj,
        "days_adherent": request.days_adherent,
        "calories_over": request.calories_over,
        "off_the_rails": request.off_the_rails,
        "lbs_to_go": round(request.avg_weight_lbs - plan_data["goal_weight"], 2)
    }

    calculated_data = calculate_checkin(checkin_data, user_data, plan_data)
    insert_checkin(checkin_data, calculated_data)
    messages = run_engine(checkin_data, calculated_data, plan_data, user_data)

    return {
        "calculated": calculated_data,
        "messages": messages
    }

@app.get("/progress/{user_id}")
def get_progress(user_id: int):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT check_in_date, avg_weight_lbs, weekly_rol, 
               cumulative_rol, fatigue_subj, strength_subj,
               days_adherent, calories_over
        FROM check_ins
        WHERE user_id = %s
        ORDER BY check_in_date ASC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    return {
        "history": [
            {
                "date": str(row[0]),
                "weight": row[1],
                "weekly_rol": row[2],
                "cumulative_rol": row[3],
                "fatigue": row[4],
                "strength": row[5],
                "days_adherent": row[6],
                "calories_over": row[7]
            }
            for row in rows
        ]
    }