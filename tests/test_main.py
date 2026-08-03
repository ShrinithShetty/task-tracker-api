from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import get_db, Base

DATABASE_URL = "sqlite:///./test_task_tracker.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind= engine)

def override_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

app.dependency_overrides[get_db] = override_db

client = TestClient(app)

def get_token(email:str, password:str):
    response = client.post("/login", 
            data = {
                "username" : email,
                "password" : password
            })
    return response.json()["access_token"]


def test_create_user():
    response1 = client.post(
        "/users/",
        json = {
            "email" : "user1@example.com",
            "fullname" : "User One",
            "password" : "user123"
        }
    )
    assert response1.status_code == 200

    response2 = client.post(
        "/users/",
        json={
            "email" : "user2@example.com",
            "fullname" : "User Two",
            "password" : "user123"
        }
    )
    assert response2.status_code == 200

def test_login():
    response = client.post(
        "/login",
        data = {
            "username" : "user1@example.com",
            "password" : "user123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_create_task_with_token():
    token = get_token("user1@example.com", "user123")

    response = client.post(
        "/tasks",
        json={
            'title' : 'Learn FastAPI',
            'description' : 'Authorization And CRUD',
            "completed" : False,
            "user_id" : 1
        },
        headers={"Authorization" : f"Bearer {token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data['title'] == 'Learn FastAPI'
    assert data['user_id'] == 1

def test_create_task_for_another_user_forbidden():
    token = get_token("user1@example.com", "user123")

    response = client.post(
        "/tasks",
        json={
            'title' : "wrong task",
            "description" : "checking the wrong task",
            'completed' : False,
            'user_id' : 2
        },
        headers={"Authorization" : f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_update_task_by_owner():
    token = get_token("user1@example.com","user123")

    response = client.put(
        "/tasks/1",
        json={
            'title' : 'Updated task',
            'description' : 'Updated by the owner',
            'completed' : True,
            'user_id' : 1
        },
        headers={"Authorization" : f"bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Updated task'
    assert data['completed'] is True

def test_update_task_by_another_user_forbidden():
    token = get_token("user2@example.com", 'user123')

    response = client.put(
        "/tasks/1",
        json={
            'title' : 'forbidden task update',
            'description' : 'not allowed',
            'completed' : True,
            'user_id' : 2
        },
        headers={"Authorization" : f'bearer {token}'}
    )
    assert response.status_code == 403

def test_delete_task_as_owner():
    token = get_token('user1@example.com', 'user123')

    response = client.delete(
        "/tasks/1",
        headers={"Authorization" : f'bearer {token}'}
    )
    assert response.status_code == 204
