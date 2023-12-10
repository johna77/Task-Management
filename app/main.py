from fastapi import FastAPI
from app import models
from app.database import engine
from app.router import users, tasks

models.Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(users.router)
app.include_router(tasks.router)

@app.get("/")
async def root():
    return {"message": "Hello Its me again with Task Management Project"}

