from fastapi import FastAPI
from app.routes.user import router as user_router

app = FastAPI()

# API 라우터 등록
app.include_router(user_router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend"}
