from fastapi import Depends
from sqlmodel import Session

from app.infra.db.repositories import SqlModelUserRepository
from app.infra.tokens.token_provider import SecurityTokenProvider

from app.domain.auth.use_cases import (
    RegisterUser,
    LoginUser,
    GoogleLogin,
    TokenExchange,
    RefreshTokens,
)

def _get_session_dep():
    from app.database import get_session  # lazy import
    return get_session()


def get_db(session: Session = Depends(_get_session_dep)) -> Session:
    return session

def get_user_repo(db: Session = Depends(get_db)) -> SqlModelUserRepository:
    return SqlModelUserRepository(db)

def get_token_provider() -> SecurityTokenProvider:
    return SecurityTokenProvider()


def get_register_use_case(
    repo = Depends(get_user_repo),
) -> RegisterUser:
    return RegisterUser(users=repo)

def get_login_use_case(
    repo = Depends(get_user_repo),
    tokens = Depends(get_token_provider),
) -> LoginUser:
    return LoginUser(users=repo, tokens=tokens)

def get_google_login_use_case(
    repo = Depends(get_user_repo),
    tokens = Depends(get_token_provider),
) -> GoogleLogin:
    return GoogleLogin(users=repo, tokens=tokens)

def get_token_exchange_use_case(
    repo = Depends(get_user_repo),
    tokens = Depends(get_token_provider),
) -> TokenExchange:
    return TokenExchange(users=repo, tokens=tokens)

def get_refresh_tokens_use_case(
    repo = Depends(get_user_repo),
    tokens = Depends(get_token_provider),
) -> RefreshTokens:
    return RefreshTokens(users=repo, tokens=tokens)