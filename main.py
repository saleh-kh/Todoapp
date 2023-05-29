from fastapi import FastAPI
from pydantic.typing import Annotated
import models
from database import engine 
from routers import todo , auth , list


app = FastAPI()
models.Base.metadata.create_all(bind = engine)
app.include_router(todo.router)
app.include_router(auth.router)
app.include_router(list.router)

