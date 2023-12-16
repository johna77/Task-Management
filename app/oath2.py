from jose import JWTError, jwt
from datetime import datetime, timedelta
from app import schemas, database, models
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi import Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from typing import Annotated

SECRET_KEY = ""
ALGORITHM = ""
ACCESS_TOKEN_EXPIRE_MINUTES = 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scopes={"admin": "Perform all tasks", "normal": "Perform tasks except admin"},
)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

            
def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    print (security_scopes.scopes)
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id = str(payload.get("user_id"))
        if id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = schemas.TokenData(scopes=token_scopes, id=id)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.id == token_data.id).first()
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes or scope != user.role_name:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_admin_user(
    current_user: Annotated[schemas.UserRegis, Security(get_current_user, scopes=["admin"])]
):
    return current_user

async def get_current_normal_user(
    current_user: Annotated[schemas.UserRegis, Security(get_current_user, scopes=["normal"])]
):
    return current_user
