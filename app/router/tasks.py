from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import schemas, models, oath2
from typing import List

router = APIRouter()

@router.get("/tasks", response_model=List[schemas.AllTask])
def gettask(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: str = ""):
    task_query = db.query(models.Task).filter(models.Task.status.contains(search)).limit(limit).offset(skip).all()
    return task_query


@router.post("/createtasks", status_code=status.HTTP_200_OK)
def create_task(task: schemas.Task, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_normal_user)):
    new_tasks = models.Task(creator_id=current_user.id, **task.model_dump())
    db.add(new_tasks)
    db.commit()
    db.refresh(new_tasks)
    return {"data": new_tasks}


@router.put("/updatetask/{task_id}", status_code=status.HTTP_200_OK)
def updatetasks(task_id: int, task_section: schemas.Task, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_normal_user)):
    task_db = db.query(models.Task).filter(models.Task.task_id == task_id)
    task = task_db.first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id {task_id} not found")
    
    if task.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You don't have permission to update this task")
    
    task_db.update(task_section.model_dump(), synchronize_session=False)
    db.commit()
    return {"data": task_db.first()}


@router.put("/tasks/{task_id}/assign", status_code=status.HTTP_200_OK)
def assigntask(task_id: int, assign_id: schemas.Assign, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_admin_user)):
    task_db = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not task_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id {task_id} not found")
    
    if not assign_id.assigned_to_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id {assign_id} not found")


    # if task_db.creator_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
    #                         detail="You don't have permission to update this task")

    task_db.assigned_to_id = assign_id.assigned_to_id
    db.commit()

    return {"message": f"Task assigned to user {assign_id} successfully"}


@router.delete("/task/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletetask(task_id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_normal_user)):
    tasks = db.query(models.Task).filter(models.Task.task_id == task_id).first()
    if not tasks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id {task_id} not found")
    

    if tasks.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="You don't have permission to update this task")
    
    db.delete(tasks)
    db.commit()
    # my_posts.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)