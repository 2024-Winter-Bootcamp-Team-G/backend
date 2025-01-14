from fastapi import FastAPI
from app.db import Base, engine
from app.routes import board, user, auth, channel, subscriptions, share
from app.init_db import init_db


Base.metadata.create_all(bind=engine)
init_db()

app = FastAPI()

app.include_router(user.router)
app.include_router(board.router)
app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(channel.router)
app.include_router(share.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Backend"}
