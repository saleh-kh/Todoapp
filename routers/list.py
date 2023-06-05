from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from pydantic.typing import Annotated
from sqlalchemy import ARRAY, String, text
from sqlalchemy.orm import Session

from database import Sessionlocal
from models import Lists, Todos

from .auth import get_current_user

router = APIRouter(prefix="/list", tags=["list"])


def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class list_request(BaseModel):
    listname: str = Field()
    shared_with: List[str]


# get all lists
@router.get("/read", status_code=status.HTTP_200_OK)
async def get_lists(db: db_dependency, user: user_dependency):
    lists = db.query(Lists).filter(Lists.list_owner == user.get("id")).all()
    if not lists:
        raise HTTPException(status_code=404, detail="there's no list")
    return lists


# create a new list
@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_list(db: db_dependency, user: user_dependency, new_list: list_request):
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="auth failed"
        )
    list_model = Lists(**new_list.dict(), list_owner=user.get("id"))
    db.add(list_model)
    db.commit()


# delete a list
@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_list(db: db_dependency, user: user_dependency, list_name: str):
    list = (
        db.query(Lists)
        .filter(Lists.list_owner == user.get("id"), Lists.listname == list_name)
        .first()
    )
    if not list:
        raise HTTPException(
            status_code=404, detail=f"there' no list called {list_name}"
        )
    db.query(Todos).filter(Todos.owner_list == list.id).delete()
    db.delete(list)
    db.commit()


# update the list
@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
async def update_list(
    db: db_dependency, user: user_dependency, list_name: str, updated_list: list_request
):
    list = (
        db.query(Lists)
        .filter(Lists.list_owner == user.get("id"), Lists.listname == list_name)
        .first()
    )
    if not list:
        raise HTTPException(
            status_code=404, detail=f"there' no list called {list_name}"
        )
    list.listname = updated_list.listname
    exsiting_shared_with = (
        list.shared_with or []
    )  # exsisitng shared list or empty list if none
    new_shared_with = exsiting_shared_with + updated_list.shared_with
    list.shared_with = new_shared_with

    db.add(list)
    db.commit()


# get lists shared with the user
@router.get("/shared_with_me")
async def get_shared_with_me(db: db_dependency, user: user_dependency):
    shared_lists = (
        db.query(Lists)
        .filter(
            text(":username = ANY(shared_with)").params(username=user.get("username"))
        )
        .all()
    )

    list_names = [shared_list.listname for shared_list in shared_lists]
    return list_names
