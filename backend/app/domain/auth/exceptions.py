class InvalidCredentials(Exception):
    pass

class UserAlreadyExists(Exception):
    pass

class UserNotFound(Exception):
    pass

class TokenInvalid(Exception):
    pass

class TokenExpired(Exception):
    pass

class DBFailure(Exception):
    pass

__all__ = [
    "InvalidCredentials",
    "UserAlreadyExists",
    "UserNotFound",
    "TokenInvalid",
    "TokenExpired",
    "DBFailure",
]