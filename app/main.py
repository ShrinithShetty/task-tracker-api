from fastapi import FastAPI
from app.schemas.task import TaskCreate

app = FastAPI()

@app.get('/')

def home():
    return {"message": "task_trackers is working"}

@app.get('/health')

def health():
    return {"status" : "ok"}

@app.post("/tasks")

def task(task : TaskCreate):
    return {
        "message" : "task has been received successfully",
        "task" : task
    }