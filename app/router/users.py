from fastapi import APIRouter, Depends, HTTPException, status, Cookie
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import schemas, utils, models, oath2
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRegis)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        print(user.username)
        print(user.password)
        print(user.role_id)
        hashed_password = utils.hash(user.password)
        user.password = hashed_password
        #role_id = user.role_id
        #new_user = models.User(**user.model_dump())
        new_user = models.User(username=user.username, password = user.password, role_id = user.role_id)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        print(new_user.id)

        return new_user
    
    except IntegrityError as e:
        print(f"Error in database operation: {e}")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists. Please choose a different username.")
    except Exception as e:
        print(f"Error in database operation: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Internal server Error")

@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends() ,db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == user_credentials.username).first()
    if not user or not utils.verify_password(user_credentials.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid credentials")
    access_token = oath2.create_access_token(data={"user_id": user.id})

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=1800)  # max_age is in seconds, adjust as needed

    db_token = models.Tokens(user_id = user.id, token=access_token)
    db.add(db_token)
    db.commit()
    db.refresh(db_token)

    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout",status_code=status.HTTP_200_OK)
def logout(username: schemas.Userlogout, access_token: str = Cookie(None), db: Session = Depends(get_db)):
    print(username.username)
    user = db.query(models.User).filter(models.User.username == username.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    response = JSONResponse(content={"message": "Logout successful"})
    response.set_cookie(key="access_token", value="", httponly=True, max_age=1)  # set max_age to a low value

    db.query(models.Tokens).filter(models.Tokens.user_id == user.id).update({"is_active": False})
    db.commit()

    return {"message": "Logout successful"}

@router.get("/users/{user_id}", status_code=status.HTTP_200_OK, response_model=schemas.UserRegis)
def userdetails(user_id: int, db: Session = Depends(get_db), current_user: int = Depends(oath2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == user_id, models.User.id == current_user.id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail = f"user with id {user_id} doesn't exist")
    return user

