from fastapi import FastAPI
from auth.routes import authRouter
from config import engine
from db.models import Base

app = FastAPI()


app.include_router(authRouter, prefix="/api/auth")


@app.get("/")
async def root():
    return {"message": "Hello World"}
