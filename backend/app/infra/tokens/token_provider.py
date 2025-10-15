from jose import ExpiredSignatureError, JWTError

from app.domain.auth.interfaces import TokenProvider
from app.domain.auth.exceptions import TokenInvalid, TokenExpired
from app.security import create_access_token, create_refresh_token, decode_token


class SecurityTokenProvider(TokenProvider):

    def create_access_token(self, user_id: int) -> str:
        return create_access_token({"sub": str(user_id)})

    def create_refresh_token(self, user_id: int) -> str:
        return create_refresh_token({"sub": str(user_id)})

    def decode_refresh_token(self, token: str) -> dict:
        try:
            return decode_token(token)
        except ExpiredSignatureError:
            raise TokenExpired()
        except (ValueError, TypeError, JWTError):
            raise TokenInvalid()


__all__ = ["SecurityTokenProvider"]