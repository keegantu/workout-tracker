from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from auth import *

class SignupData(BaseModel):
    username: str
    email: str
    password: str

class LoginData(BaseModel):
    username: str
    password: str

class SetData(BaseModel):
    workout_id: int
    exercise_id: int
    reps: int
    weight: float

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    username = verify_token(token)
    if username is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username

@app.post("/signup")
def signup_route(data: SignupData):
    sign_up(data.username, data.email, data.password)
    return {"message": "user created"}

@app.post("/login")
def login_user(data: LoginData):
    if log_in(data.username, data.password):
        token = create_token(data.username)
        return {"token": token}
    else:
        return {"error": "Invalid credentials"}

@app.get("/my-workouts")
def workouts_route(username: str = Depends(get_current_user)):
    rows = get_workouts(username)
    return [
        {"workout_id": row[0], "date": row[1].isoformat()}
        for row in rows
    ]

@app.get("/workouts/{workout_id}/sets")
def sets(workout_id: int):
    rows = get_sets(workout_id)
    return [
        {"exercise": row[0], "reps": row[2], "weight": float(row[3])}
        for row in rows
    ]

@app.post("/add-workout")
def add_workout_route(username: str = Depends(get_current_user)):
    workout_id = addWorkout(username)
    return {"workout_id": workout_id}

@app.post("/add-set")
def add_set_route(data: SetData, username: str = Depends(get_current_user)):
    addSet(data.workout_id, data.exercise_id, data.reps, data.weight)
    return {"message": "set added"}

@app.get("/volume")
def volume_route(exercise_id: int, username: str = Depends(get_current_user)):
    rows = volume_over_time(username, exercise_id)
    return [
        {"date": row[0].isoformat(), "volume": float(row[1])}
        for row in rows
    ]

@app.get("/max-weight")
def max_weight_route(exercise_id: int, username: str = Depends(get_current_user)):
    return {"max_weight": maxWeight(username, exercise_id)}

@app.get("/percent-increase")
def percent_increase_route(exercise_id: int, from_date: str, username: str = Depends(get_current_user)):
    rows = percent_increase(username, exercise_id, from_date)
    return [
        {"date": row[0].isoformat(), "volume": float(row[1]), "percent": float(row[2])}
        for row in rows
    ]

@app.get("/exercises")
def exercises_route():
    exercises = get_exercises()
    return exercises

@app.get("/leaderboard")
def leaderboard_route():
    rows = get_total_vol_leaderboard()
    return [
        {"username": row[0], "volume": float(row[1]), "vol_rank": row[2]}
        for row in rows
    ]