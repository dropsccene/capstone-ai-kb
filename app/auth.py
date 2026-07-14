from fastapi import Depends,HTTPException
from sqlalchemy.orm import Session
from jose import jwt,JWTError
from app.database import get_db
from app.models import User
from app.config import settings
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_current_user(token:str = Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        payload = jwt.decode(token,settings.SECRET_KEY,algorithms=["HS256"])
    except JWTError:
        raise HTTPException(status_code=401,detail="凭据无效")
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401,detail="用户不存在")
    return user
