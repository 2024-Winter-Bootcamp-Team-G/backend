from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.db import Base, engine
from app.routes import board, user, auth, subscriptions, share, celery_tasks, profile
from app.init_db import init_db
from prometheus_fastapi_instrumentator import Instrumentator

Base.metadata.create_all(bind=engine)
init_db()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://www.algorify.net", "https://algorify.net"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(board.router)
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(subscriptions.router)
app.include_router(share.router)
app.include_router(celery_tasks.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend"}

Instrumentator().instrument(app).expose(app)