from pydantic import BaseModel , Field
from pydantic.typing import Annotated
from fastapi import APIRouter,Depends ,HTTPException ,status
from sqlalchemy.orm import Session
from models import Todos
from database import Sessionlocal




router = APIRouter()


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]


# Validation for creating a new todo
class todo_request(BaseModel):
    title : str = Field(min_length=5 ,max_length=250)
    priority : int = Field(gt=0 ,lt=6) #Between one and five
    complete :bool = Field(default=False)

    class Config:
        schema_extra = {
            "example" : {
                'title' : "Wash the car",
                'priority' : 3,
                'complete' : "false"
            }
        }



# basic CRUD operations

# read all todos
@router.get('/todo')
async def read_todos(db: db_dependency):
    todo = db.query(Todos).all()
    return todo

# read a specific todo
@router.get('/todo/{todo_id}')
async def read_todo_by_id(db:db_dependency , todo_id:int):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo :
        raise  HTTPException(status_code=404, detail="todo not found")
    return todo

# create a todo
@router.post('/todo')
async def create_todo(db:db_dependency,todo_request:todo_request):
    todo_model = Todos(**todo_request.dict())
    db.add(todo_model)
    db.commit()
    

# update a todo 
@router.put('/todo/{todo_id}')
async def update_todo(db:db_dependency, updated_todo:todo_request , todo_id:int):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise  HTTPException(status_code=404, detail="todo not found")
    todo.title = updated_todo.title 
    todo.priority = updated_todo.priority
    todo.complete = updated_todo.complete
    db.add(todo)
    db.commit()


# delete a todo
@router.delete('/todo/{todo_id}')
async def delete_todo(db:db_dependency , todo_id:int):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if not todo:
        raise  HTTPException(status_code=404, detail="todo not found")
    db.delete(todo)
    db.commit()






