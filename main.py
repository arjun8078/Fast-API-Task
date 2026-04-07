from fastapi import FastAPI
from routes import user, task
from database import Base, engine





app = FastAPI()

# app.include_router(auth_router)



Base.metadata.create_all(bind=engine)

app.include_router(user.router)
app.include_router(task.router)


@app.get("/")
def home():
    return {"message": "FastAPI running 🚀","docs": "/docs",
        "status": "running"}