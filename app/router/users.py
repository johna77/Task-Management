from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, utils, models, oath2
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from typing import List

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRegis)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        valid_scopes = {"admin", "normal"}
        if user.role_name not in valid_scopes:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid scope")
        new_user = models.User(username=user.username, password = user.password, role_name = user.role_name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    except IntegrityError as e:
        print(f"Error in database operation: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists. Please choose a different username.")
    except HTTPException as e:
        print(f"Error in HTTP operation: {e}")
        raise
    except Exception as e:
        print(f"Error in database operation: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends() ,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    access_token = oath2.create_access_token(data={"user_id": user.id, "scopes": user_credentials.scopes})

    db_token = models.Tokens(user_id = user.id, token=access_token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=schemas.UserRegis)
def userdetails(user_id: int, db: Session = Depends(get_db), current_user: schemas.UserRegis = Depends(oath2.get_current_admin_user)):
    #print (oath2.get_current_active_user)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"user with id {user_id} doesn't exist")
    return user

@router.get("/users", status_code=status.HTTP_200_OK, response_model=List[schemas.UserRegis])
def userdetails(db: Session = Depends(get_db), current_user: schemas.UserRegis = Depends(oath2.get_current_user)):
    #print (oath2.get_current_active_user)
    alluser = db.query(models.User).all()
    return alluser