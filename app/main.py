from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, rooms, admin, users
from app import models
from app.database import engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(users.router)
app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(rooms.router)


@app.get("/")
async def hello_message():
    return {"message": 'Server is successfully running!!!'}
