from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import schemas, database, models
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

SECRET_KEY = ""
ALGORITHM = ""
ACCESS_TOKEN_EXPIRE_MINUTES = 10

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = str(payload.get("user_id"))
        if id is None:
            raise credentials_exception
        # user = db.query(models.Tokens).filter(models.Tokens.user_id == id).first()
        # if not user or not user.is_active:
        #     raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data
            
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = verify_access_token(token, credentials_exception)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user


def get_user_role(user: schemas.UserRegis = Depends(get_current_user)):
    return user.role_id

def is_admin(user_role: int = Depends(get_user_role)):
    if user_role != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied, admin role required")
