from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate
from app.auth import get_current_user
import bcrypt
from jose import jwt
from datetime import datetime,timedelta
from app.config import settings
from app.schemas import UserLogin,TokenResponse,UserResponse


router = APIRouter(prefix="/api/auth",tags = ["认证"])

@router.post("/register")
def register(user_data:UserCreate,db:Session = Depends(get_db)):
    existing_user = db.query(User).filter((User.username == user_data.username) | (User.email == user_data.email)).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="用户名或邮箱已存在")
    hashed = bcrypt.hashpw(user_data.password.encode("utf-8"), bcrypt.gensalt()).decode()
    new_user = User(username=user_data.username,email=user_data.email,hashed_password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login",response_model=TokenResponse)
def login(login_data:UserLogin,db:Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not bcrypt.checkpw(login_data.password.encode("utf-8"),user.hashed_password.encode("utf-8")):
        raise HTTPException(status_code=401,detail="用户名或密码错误")
    payload = {"sub":str(user.id),"exp":datetime.utcnow() + timedelta(hours = 24)}
    token = jwt.encode(payload,settings.SECRET_KEY,algorithm="HS256")
    return TokenResponse(access_token = token)

@router.get("/me",response_model=UserResponse)
def me(current_user:User = Depends(get_current_user)):
    return current_user


