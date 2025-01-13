from fastapi import FastAPI
from app.db import Base, engine
from app.routes.user import router as user_router

# DB 초기화
Base.metadata.create_all(bind=engine)

app = FastAPI()

# API 라우터 등록
app.include_router(user_router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend"}
