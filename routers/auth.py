from datetime import timedelta , datetime
from fastapi import APIRouter, Depends ,HTTPException ,status
from database import Sessionlocal
from pydantic.typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel ,Field
from models import Users
from passlib.context import CryptContext
from jose import jwt , JWTError
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer




def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session,Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'],deprecated = 'auto') 
router = APIRouter(prefix='/auth',tags=['auth'])
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

#for JWT
SECRET_KEY = '948d7866cc6e14b8a100c849a69d35ab656a14dcfa3fbaf0969903df36cbe07b'
ALGORITHM = 'HS256'

# auth user
def auth_user(username:str , password:str , db:db_dependency):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password):
        return False
    return user


def create_access_token(username:str , user_id:int , role:str , expire_time:timedelta):
    encode = {
        'sub' : username , 'id' : user_id , 'role' : role
    }
    expires = datetime.utcnow() + expire_time
    encode.update({'exp':expires})
    return jwt.encode(encode , SECRET_KEY , algorithm=ALGORITHM)

#

async def get_current_user(token:Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token , SECRET_KEY , algorithms=[ALGORITHM])
        username :str = payload.get('sub')
        user_id : int = payload.get('id')
        role : str =payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credintals  ")
        return { 'username' : username , 'id' : user_id , 'role' : role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credintals  ")    



# 
class user_request(BaseModel):
    username :str = Field(min_length=3)
    password:str = Field(min_length=5)
    role : str 


class Token(BaseModel):
    access_token : str
    token_type: str


# create a new user
@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db:db_dependency , new_user:user_request):
    user = Users(
        username = new_user.username,
        hashed_password = bcrypt_context.hash(new_user.password),
        role = new_user.role
    )
    db.add(user)
    db.commit()


@router.get('/user')
async def get_users(db:db_dependency):
    return db.query(Users).all()


@router.post('/token')
async def login_for_token(formdata : Annotated[OAuth2PasswordRequestForm,Depends()], db:db_dependency):
    user =  auth_user(formdata.username, formdata.password,db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate credintals هنا")
    token = create_access_token(user.username , user.id , user.role, timedelta(minutes=20))

    return {'access_token' : token ,'token_type' : 'bearer' }




