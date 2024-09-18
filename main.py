from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from auth import get_current_user, create_access_token, authenticate_user
from schemas import UserCreate, User
from database import Base, engine, get_db
from models import Contact, User
from datetime import timedelta

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=dict)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/contacts/", response_model=Contact)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Add logic to only allow the current user to create contacts
    pass
