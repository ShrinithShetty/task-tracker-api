from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.user import UserCreate, UserResponse
from app.schemas.login import LoginCreate, LoginResponse
from app.db.database import Base, engine, get_db
from app.utils.security import hash_password, verify_password
from app.models.task import Task
from app.models.user import User



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
    user = db.query(User).filter(User.id == task.user_id).first()

    if user is None:
        raise HTTPException(status_code = 404, detail= "User Not Found")
    
    new_task = Task(
        title = task.title,
        description = task.description,
        completed = task.completed,
        user_id = task.user_id
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
    
    user = db.query(User).filter(User.id == updated_task.user_id).first()
    if user is None:
        raise HTTPException(404, detail="User Not Found")
    
    task.title = updated_task.title
    task.description = updated_task.description
    task.completed = updated_task.completed
    task.user_id = updated_task.user_id

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


@app.post("/users/", response_model = UserResponse)
def create_user(user : UserCreate, db : Session = Depends(get_db)):
    exisiting = db.query(User).filter(User.email == user.email).first()

    if exisiting is not None:
        raise HTTPException(status_code = 400, detail = "Email is Already Registered")
    
    new_user = User(
        email = user.email,
        fullname = user.fullname,
        password = hash_password(user.password)

    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/users/", response_model = list[UserResponse] )
def get_user(db : Session = Depends(get_db)):
    users = db.query(User).all()

    return users
 
@app.get('/users/{user_id}/tasks', response_model= list[TaskResponse])
def get_user_tasks(user_id : int, db : Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise HTTPException(status_code = 404, detail="User Not Found")
    
    tasks = db.query(Task).filter(Task.user_id == user_id).all()
    return tasks

@app.post("/login", response_model= LoginResponse)
def create_login(user_data : LoginCreate, db : Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if user is None:
        raise HTTPException(status_code= 401, detail= "Invalid email or password")
    
    if not verify_password(user_data.password, user.password):
        raise HTTPException(status_code= 401, detail="Invalid email or password")
    
    return {"message" : "Login Successfull"}
    
