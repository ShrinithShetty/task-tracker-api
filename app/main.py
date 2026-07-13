from fastapi import FastAPI

app = FastAPI()

@app.get('/')

def home():
    return {"message": "task_trackers is working"}