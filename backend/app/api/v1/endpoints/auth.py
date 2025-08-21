from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlmodel import Session, select
from app.models.user import User
from app.database import get_session
from app.schemas import UserCreate, GoogleUser, UserLogin
from app.security import hash_password, create_access_token, verify_password, create_refresh_token

router = APIRouter()

@router.post("/register")
def register_user(user: UserCreate, session: Session = Depends(get_session)):
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already registered")

    hashed_pw = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_pw)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

@router.post("/google")
def google_login(user: GoogleUser, session: Session = Depends(get_session)):
    try:
        existing_user = session.exec(
            select(User).where(User.email == user.email)
        ).first()

        if not existing_user:
            new_user = User(email=user.email, provider="google", sub=user.sub)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            user_to_return = new_user
        else:
            if existing_user.sub != user.sub:
                existing_user.sub = user.sub
                session.commit()
                session.refresh(existing_user)
            user_to_return = existing_user

        access_token = create_access_token({"sub": str(user_to_return.id)})
        refresh_token = create_refresh_token({"sub": str(user_to_return.id)})

        return {
            "id": user_to_return.id,
            "email": user_to_return.email,
            "role": user_to_return.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    except IntegrityError as e:
        session.rollback()
        u = session.exec(select(User).where(User.email == user.email)).first()
        if not u:
            raise HTTPException(status_code=500, detail="User upsert failed")
        access_token = create_access_token({"sub": str(u.id)})
        refresh_token = create_refresh_token({"sub": str(u.id)})
        return {
            "id": u.id,
            "email": u.email,
            "role": u.role,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    except OperationalError as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"db connection error: {str(e)}")
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"rollback error: {str(e)}")



@router.post("/login")
def login(user: UserLogin, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == user.email)).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {
        "id": db_user.id,
        "email": db_user.email,
        "role": db_user.role,
        "access_token": access_token,
        "refresh_token": refresh_token,
    }