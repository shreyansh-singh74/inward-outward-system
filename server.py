from fastapi import FastAPI
from auth.routes import authRouter
from config import engine
from sqlmodel import SQLModel

app = FastAPI()


app.include_router(authRouter, prefix="/api/auth")


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
