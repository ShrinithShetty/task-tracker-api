from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate, TaskResponse
from app.db.database import Base, engine, get_db
from app.models.task import Task


Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get('/')

def home():
    return {"message": "task_trackers is working"}

@app.get('/health')

def health():
    return {"status" : "ok"}

@app.post("/tasks", response_model = TaskResponse)
def create_task(task : TaskCreate, db: Session = Depends(get_db)):
    new_task = Task(
        title = task.title,
        description = task.description,
        completed = task.completed
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task

@app.get("/tasks", response_model = list[TaskResponse])
def get_task(db : Session = Depends(get_db)):
    tasks = db.query(Task).all()
    return tasks