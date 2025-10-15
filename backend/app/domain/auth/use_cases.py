from dataclasses import dataclass

from app.domain.auth.interfaces import UserRepository, TokenProvider
from app.domain.auth.exceptions import (
    InvalidCredentials, UserAlreadyExists, UserNotFound,
    TokenInvalid, TokenExpired
)
from app.domain.auth.entities import UserEntity
from app.security import verify_password, hash_password

@dataclass(frozen=True)
class AuthResult:
    id: int
    email: str
    role: str
    access_token: str
    refresh_token: str


@dataclass(frozen=True)
class TokensResult:
    access_token: str
    refresh_token: str


class RegisterUser:
    def __init__(self, users: UserRepository):
        self.users = users

    def execute(self, *, email: str, password: str) -> UserEntity:
        if self.users.exists_email(email):
            raise UserAlreadyExists()
        user = self.users.create_local(
            email=email,
            hashed_password=hash_password(password),
        )
        return user


class LoginUser:
    def __init__(self, users: UserRepository, tokens: TokenProvider):
        self.users = users
        self.tokens = tokens

    def execute(self, *, email: str, password: str) -> AuthResult:
        user = self.users.get_by_email(email)
        if not user or not user.hashed_password:
            raise InvalidCredentials()
        if not verify_password(password, user.hashed_password):
            raise InvalidCredentials()

        access = self.tokens.create_access_token(user.id)
        refresh = self.tokens.create_refresh_token(user.id)

        return AuthResult(
            id=user.id,
            email=user.email,
            role=user.role or "user",
            access_token=access,
            refresh_token=refresh,
        )


class GoogleLogin:
    def __init__(self, users: UserRepository, tokens: TokenProvider):
        self.users = users
        self.tokens = tokens

    def execute(self, *, email: str, sub: str) -> AuthResult:
        user = self.users.upsert_google_user(email=email, sub=sub)

        access = self.tokens.create_access_token(user.id)
        refresh = self.tokens.create_refresh_token(user.id)

        return AuthResult(
            id=user.id,
            email=user.email,
            role=user.role or "user",
            access_token=access,
            refresh_token=refresh,
        )


class TokenExchange:
    def __init__(self, users: UserRepository, tokens: TokenProvider):
        self.users = users
        self.tokens = tokens

    def execute(self, *, email: str, sub: str) -> TokensResult:
        user = self.users.upsert_google_user(email=email, sub=sub)

        access = self.tokens.create_access_token(user.id)
        refresh = self.tokens.create_refresh_token(user.id)

        return TokensResult(access_token=access, refresh_token=refresh)


class RefreshTokens:
    def __init__(self, users: UserRepository, tokens: TokenProvider):
        self.users = users
        self.tokens = tokens

    def execute(self, *, refresh_token: str) -> TokensResult:
        if not refresh_token:
             raise TokenInvalid()

        try:
            payload = self.tokens.decode_refresh_token(refresh_token)
        except TokenExpired:
           raise
        except TokenInvalid:
            raise

        sub = payload.get("sub")
        if not sub:
            raise TokenInvalid()

        user = self.users.get_by_id(int(sub))
        if not user:
            raise UserNotFound()

        access = self.tokens.create_access_token(user.id)
        refresh = self.tokens.create_refresh_token(user.id)

        return TokensResult(access_token=access, refresh_token=refresh)