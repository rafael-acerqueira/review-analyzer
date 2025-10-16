from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas import (
    UserCreate,
    GoogleUser,
    UserLogin,
    TokenExchangeIn,
    TokensOut,
    RefreshIn,
)

from app.api.v1.deps import (
    get_register_use_case,
    get_login_use_case,
    get_google_login_use_case,
    get_token_exchange_use_case,
    get_refresh_tokens_use_case,
)

from app.domain.auth.use_cases import (
    RegisterUser,
    LoginUser,
    GoogleLogin,
    TokenExchange,
    RefreshTokens,
)
from app.domain.auth.exceptions import (
    UserAlreadyExists,
    InvalidCredentials,
    UserNotFound,
    TokenInvalid,
    TokenExpired,
)

router = APIRouter()

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    payload: UserCreate,
    use_case: RegisterUser = Depends(get_register_use_case),
):
    try:
        user = use_case.execute(email=payload.email, password=payload.password)
        return {"id": user.id, "email": user.email}
    except UserAlreadyExists:
        raise HTTPException(status_code=400, detail="User already registered")



@router.post("/google")
def google_login(
    payload: GoogleUser,
    use_case: GoogleLogin = Depends(get_google_login_use_case),
):

    result = use_case.execute(email=payload.email, sub=payload.sub)
    return {
        "id": result.id,
        "email": result.email,
        "role": result.role,
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
    }

@router.post("/login")
def login(
    payload: UserLogin,
    use_case: LoginUser = Depends(get_login_use_case),
):
    try:
        result = use_case.execute(email=payload.email, password=payload.password)
        return {
            "id": result.id,
            "email": result.email,
            "role": result.role,
            "access_token": result.access_token,
            "refresh_token": result.refresh_token,
        }
    except InvalidCredentials:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/token/exchange")
def token_exchange(
    payload: TokenExchangeIn,
    use_case: TokenExchange = Depends(get_token_exchange_use_case),
):

    result = use_case.execute(email=payload.email, sub=payload.sub)

    return {
        "access_token": result.access_token,
        "refresh_token": result.refresh_token,
        "token_type": "bearer",
        "expires_in": 60 * 60 * 24 * 7,
    }

@router.post("/refresh", response_model=TokensOut)
def refresh_tokens(
    payload: RefreshIn,
    use_case: RefreshTokens = Depends(get_refresh_tokens_use_case),
):

    try:
        result = use_case.execute(refresh_token=payload.refresh_token)
        return TokensOut(access_token=result.access_token, refresh_token=result.refresh_token)
    except TokenExpired:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except TokenInvalid:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    except UserNotFound:
        raise HTTPException(status_code=401, detail="User not found")