from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, ExpiredSignatureError
from sqlmodel import Session
from app.models.user import User
from app.database import get_session, engine
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    try:
        payload = decode_token(token)
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")

        user = session.get(User, int(sub))
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (ValueError, TypeError):
        raise HTTPException(status_code=401, detail="Invalid token subject")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")