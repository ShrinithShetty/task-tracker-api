from fastapi import FastAPI, Depends, HTTPException
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
def get_task(completed : bool | None = None, db : Session = Depends(get_db)):
    query = db.query(Task)

    if completed is not None:
        query = query.filter(Task.completed == completed)
    tasks = query.all()
    return tasks

@app.get("/tasks/{task_id}", response_model = TaskResponse)
def get_task_id(task_id : int, db : Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code = 404, detail = "Task Not Found")
    
    return task

@app.put("/tasks/{task_id}",response_model = TaskResponse)
def update_task(task_id : int, updated_task : TaskCreate, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code = 404, detail = "Task Not Found" )
    
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed

    db.commit()
    db.refresh(task)

    return task

@app.delete("/tasks/{task_id}", status_code = 204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()

    if task is None:
        raise HTTPException(status_code = 404, detail = "Task Not Found")
    
    db.delete(task)
    db.commit()

    return None

 
    
