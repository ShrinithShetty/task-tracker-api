from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError


from app.schemas.task import TaskCreate, TaskResponse
from app.schemas.user import UserCreate, UserResponse
from app.schemas.login import LoginCreate, LoginResponse
from app.db.database import Base, engine, get_db
from app.utils.security import hash_password, verify_password
from app.utils.auth import SECRET_KEY, ALGORITHM, create_access_token
from app.models.task import Task
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "login")


Base.metadata.create_all(bind = engine)

app = FastAPI()

@app.get('/')

def home():
    return {"message": "task_trackers is working"}

@app.get('/health')

def health():
    return {"status" : "ok"}


def get_current_user(token: str = Depends(oauth2_scheme), db : Session = Depends(get_db)):
    credential_exception = HTTPException(status_code=401, detail="Could not validate credentials")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms= [ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credential_exception
    except JWTError:
        raise credential_exception
    
    user = db.query(User).filter(User.email == email).first()

    if user is None:
        raise credential_exception
    
    return user


@app.post("/tasks", response_model = TaskResponse, status_code=201)
def create_task(task : TaskCreate, db: Session = Depends(get_db), current_user : User = Depends(get_current_user)):
    if current_user.id != task.user_id:
        raise HTTPException(status_code=403, detail="Not allowed to create task for another user")
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
def create_login(db : Session = Depends(get_db), form_data : OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()

    if user is None:
        raise HTTPException(status_code= 401, detail= "Invalid email or password")
    
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code= 401, detail="Invalid email or password")
    
    
    access_token = create_access_token(data = {"sub": user.email})

    return {"access_token" : access_token, "token_type": "bearer"}
    




