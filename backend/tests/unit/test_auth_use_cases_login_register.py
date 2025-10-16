import pytest

from app.domain.auth.use_cases import RegisterUser, LoginUser, AuthResult
from app.domain.auth.entities import UserEntity
from app.domain.auth.exceptions import UserAlreadyExists, InvalidCredentials
from app.domain.auth.interfaces import UserRepository, TokenProvider
from app.security import hash_password


class FakeUserRepo(UserRepository):
    def __init__(self):
        self._by_email = {}
        self._by_id = {}
        self._seq = 1

    def _add_entity(self, e: UserEntity):
        self._by_email[e.email] = e
        self._by_id[e.id] = e

    def get_by_email(self, email: str):
        return self._by_email.get(email)

    def get_by_id(self, user_id: int):
        return self._by_id.get(user_id)

    def exists_email(self, email: str) -> bool:
        return email in self._by_email

    def create_local(self, *, email: str, hashed_password: str) -> UserEntity:
        if email in self._by_email:
            raise AssertionError("Should not be called if exists_email True")
        e = UserEntity(id=self._seq, email=email, hashed_password=hashed_password, role="user")
        self._seq += 1
        self._add_entity(e)
        return e

    def upsert_google_user(self, *, email: str, sub: str) -> UserEntity:
        raise NotImplementedError

    def update_google_sub_if_needed(self, *, user_id: int, sub: str):
        raise NotImplementedError


class FakeTokens(TokenProvider):
    def create_access_token(self, user_id: int) -> str:
        return f"access.{user_id}"

    def create_refresh_token(self, user_id: int) -> str:
        return f"refresh.{user_id}"

    def decode_refresh_token(self, token: str) -> dict:
        return {"sub": token.split(".")[1]} if "." in token else {}




def test_register_user_ok():
    repo = FakeUserRepo()
    uc = RegisterUser(users=repo)

    user = uc.execute(email="a@a.com", password="12345678")

    assert isinstance(user, UserEntity)
    assert user.id == 1
    assert user.email == "a@a.com"
    assert user.hashed_password and user.hashed_password != "12345678"


def test_register_user_existing_email_raises():
    repo = FakeUserRepo()
    # seed
    repo.create_local(email="a@a.com", hashed_password=hash_password("x"))
    uc = RegisterUser(users=repo)

    with pytest.raises(UserAlreadyExists):
        uc.execute(email="a@a.com", password="12345678")


def test_login_ok():
    repo = FakeUserRepo()
    tokens = FakeTokens()
    pw_hash = hash_password("12345678")
    repo.create_local(email="a@a.com", hashed_password=pw_hash)

    uc = LoginUser(users=repo, tokens=tokens)
    result = uc.execute(email="a@a.com", password="12345678")

    assert isinstance(result, AuthResult)
    assert result.email == "a@a.com"
    assert result.access_token == "access.1"
    assert result.refresh_token == "refresh.1"


def test_login_invalid_email_or_password_raises():
    repo = FakeUserRepo()
    tokens = FakeTokens()
    repo.create_local(email="a@a.com", hashed_password=hash_password("another_password"))

    uc = LoginUser(users=repo, tokens=tokens)

    with pytest.raises(InvalidCredentials):
        uc.execute(email="a@a.com", password="12345678")

    with pytest.raises(InvalidCredentials):
        uc.execute(email="fakeuserhere@a.com", password="anything")
