from fastapi import APIRouter
from fastapi import APIRouter, Depends ,HTTPException ,status
from database import Sessionlocal
from pydantic.typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel ,Field 
from .auth import get_current_user
from typing import List
from models import Lists



router = APIRouter()


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]
user_dependency = Annotated[dict ,Depends(get_current_user)]


class list_request(BaseModel):
    listname :str = Field()
    shared_with: List[str]



#create a new list
@router.post('/',status_code=status.HTTP_201_CREATED)
async def create_list(db:db_dependency, user : user_dependency,new_list:list_request ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='auth failed')
    list_model = Lists(**new_list.dict(),list_owner = user.get('id'))
    db.add(list_model)
    db.commit()
