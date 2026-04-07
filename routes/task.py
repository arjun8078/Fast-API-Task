from fastapi import APIRouter, Depends
from database import SessionLocal
from models import TaskDB
from schemas import Task
from core.security import get_current_user

router = APIRouter()

@router.post("/tasks")
def create_task(task: Task, current_user=Depends(get_current_user)):
    db = SessionLocal()

    db_task = TaskDB(
        title=task.title,
        name=task.name,
        completed=task.completed,
        user_id=current_user.id
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task


@router.get("/tasks")
def get_tasks(current_user=Depends(get_current_user)):
    db = SessionLocal()
    return db.query(TaskDB).filter(TaskDB.user_id == current_user.id).all()


@router.put("/tasks/{task_id}")
def update_task(task_id: int, updated_task: Task, current_user=Depends(get_current_user)):
    db = SessionLocal()

    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.user_id == current_user.id
    ).first()

    if not task:
        return {"error": "No task found"}

    task.title = updated_task.title
    task.name = updated_task.name
    task.completed = updated_task.completed

    db.commit()
    db.refresh(task)

    return task


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user=Depends(get_current_user)):
    db = SessionLocal()

    task = db.query(TaskDB).filter(
        TaskDB.id == task_id,
        TaskDB.user_id == current_user.id
    ).first()

    if not task:
        return {"error": "Task not found"}

    db.delete(task)
    db.commit()

    return {"message": "Task deleted successfully"}