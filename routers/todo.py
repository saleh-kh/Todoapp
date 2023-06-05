from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from pydantic.typing import Annotated
from sqlalchemy import text
from sqlalchemy.orm import Session

from database import Sessionlocal
from models import Lists, Todos

from .auth import get_current_user

router = APIRouter()


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


# Validation for creating a new todo
class todo_request(BaseModel):
    title: str = Field(min_length=5, max_length=250)
    priority: int = Field(gt=0, lt=6)  # Between one and five
    complete: bool = Field(default=False)
    list_name: str

    class Config:
        schema_extra = {
            "example": {
                "title": "Wash the car",
                "priority": 3,
                "list_name": "name",
                "complete": "false",
            }
        }


# basic CRUD operations


# read all todos
@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_todos(user: user_dependency, db: db_dependency, listname: str):
    list_model = (
        db.query(Lists)
        .filter(Lists.list_owner == user.get("id"), Lists.listname == listname)
        .first()
    )
    if not list_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"list {listname} not found"
        )
    todos = db.query(Todos).filter(Todos.owner_list == list_model.id).all()
    return todos


# read a specific todo
@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo_by_id(
    db: db_dependency, user: user_dependency, listname: str, todo_id: int
):
    list_model = (
        db.query(Lists)
        .filter(Lists.list_owner == user.get("id"), Lists.listname == listname)
        .first()
        or db.query(Lists)
        .filter(
            text(":username = ANY(shared_with)").params(username=user.get("username")),
            Lists.listname == listname,
        )
        .first()
    )
    if not list_model:
        raise HTTPException(
            status_code=404,
            detail=f"List '{listname}' not found or not shared with the user.",
        )
    todo = (
        db.query(Todos)
        .filter(Todos.owner_list == list_model.id, Todos.id == todo_id)
        .first()
    )
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )
    return todo


# create a todo
@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(
    db: db_dependency, user: user_dependency, todo_request: todo_request
):
    list_name = todo_request.list_name
    list_model = (
        db.query(Lists)
        .filter(Lists.list_owner == user.get("id"), Lists.listname == list_name)
        .first()
        or db.query(Lists)
        .filter(
            text(":username = ANY(shared_with)").params(username=user.get("username")),
            Lists.listname == list_name,
        )
        .first()
    )
    if not list_model:
        raise HTTPException(
            status_code=404,
            detail=f"List '{list_name}' not found or not shared with the user.",
        )
    todo_model = Todos(
        title=todo_request.title,
        priority=todo_request.priority,
        complete=todo_request.complete,
        owner_list=list_model.id,
    )
    db.add(todo_model)
    db.commit()


# update a todo
@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
    db: db_dependency, user: user_dependency, updated_todo: todo_request, todo_id: int
):
    list_name = updated_todo.list_name
    # Check if list exist or shared by the user
    list_model = (
        db.query(Lists)
        .filter(Lists.list_owner == user.get("id"), Lists.listname == list_name)
        .first()
        or db.query(Lists)
        .filter(
            text(":username = ANY(shared_with)").params(username=user.get("username")),
            Lists.listname == list_name,
        )
        .first()
    )
    if not list_model:
        raise HTTPException(
            status_code=404,
            detail=f"List '{list_name}' not found or not shared with the user.",
        )
    todo_model = (
        db.query(Todos)
        .filter(Todos.id == todo_id, Todos.owner_list == list_model.id)
        .first()
    )
    if not todo_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="todo not found"
        )
    todo_model.title = updated_todo.title
    todo_model.priority = updated_todo.priority
    todo_model.complete = updated_todo.complete
    todo_model.owner_list = list_model.id

    db.add(todo_model)
    db.commit()


# delete a todo
@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, user: user_dependency, todo_id: int):
    list = db.query(Lists).filter(Lists.list_owner == user.get("id")).first()
    todo = (
        db.query(Todos).filter(Todos.owner_list == list.id, Todos.id == todo_id).first()
    )
    if not todo:
        raise HTTPException(status_code=404, detail="todo not found")
    db.delete(todo)
    db.commit()


# get todos shared with me
@router.get("/shared_todo", status_code=status.HTTP_200_OK)
async def get_shared_todos(db: db_dependency, user: user_dependency, listname: str):
    list = (
        db.query(Lists)
        .filter(
            text(":username = ANY(shared_with)").params(username=user.get("username")),
            Lists.listname == listname,
        )
        .first()
    )
    if not list:
        raise HTTPException(status_code=404, detail=f"list {listname} not found")
    todos = db.query(Todos).filter(Todos.owner_list == list.id).all()
    return todos
