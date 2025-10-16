import pytest

from app.domain.auth.use_cases import GoogleLogin, TokenExchange, RefreshTokens, TokensResult, AuthResult
from app.domain.auth.entities import UserEntity
from app.domain.auth.exceptions import TokenInvalid, TokenExpired, UserNotFound
from app.domain.auth.interfaces import UserRepository, TokenProvider



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
        e = UserEntity(id=self._seq, email=email, hashed_password=hashed_password, role="user")
        self._seq += 1
        self._add_entity(e)
        return e

    def upsert_google_user(self, *, email: str, sub: str) -> UserEntity:
        u = self._by_email.get(email)
        if not u:
            u = UserEntity(id=self._seq, email=email, role="user", provider="google", sub=sub)
            self._seq += 1
            self._add_entity(u)
            return u

        if u.sub != sub:
            u = UserEntity(id=u.id, email=u.email, role=u.role, provider="google", sub=sub, hashed_password=u.hashed_password)
            self._add_entity(u)
        return u

    def update_google_sub_if_needed(self, *, user_id: int, sub: str):
        u = self._by_id.get(user_id)
        if not u:
            return None
        if u.sub != sub:
            u = UserEntity(id=u.id, email=u.email, role=u.role, provider="google", sub=sub, hashed_password=u.hashed_password)
            self._add_entity(u)
        return u


class FakeTokens(TokenProvider):
    def __init__(self, mode="ok"):
        self.mode = mode

    def create_access_token(self, user_id: int) -> str:
        return f"access.{user_id}"

    def create_refresh_token(self, user_id: int) -> str:
        return f"refresh.{user_id}"

    def decode_refresh_token(self, token: str) -> dict:
        if self.mode == "expired":
            from app.domain.auth.exceptions import TokenExpired
            raise TokenExpired()
        if self.mode == "invalid":
            from app.domain.auth.exceptions import TokenInvalid
            raise TokenInvalid()

        try:
            _, id_str = token.split(".", 1)
            return {"sub": id_str}
        except Exception:
            return {}




def test_google_login_creates_or_updates_user_and_returns_tokens():
    repo = FakeUserRepo()
    tokens = FakeTokens()
    uc = GoogleLogin(users=repo, tokens=tokens)

    result1 = uc.execute(email="g@a.com", sub="sub-1")
    assert isinstance(result1, AuthResult)
    assert result1.access_token == "access.1"
    assert result1.refresh_token == "refresh.1"

    result2 = uc.execute(email="g@a.com", sub="sub-2")
    assert result2.id == result1.id
    assert result2.access_token == "access.1"
    assert result2.refresh_token == "refresh.1"


def test_token_exchange_returns_tokens():
    repo = FakeUserRepo()
    tokens = FakeTokens()
    uc = TokenExchange(users=repo, tokens=tokens)

    res = uc.execute(email="g@a.com", sub="sub-1")
    assert isinstance(res, TokensResult)
    assert res.access_token == "access.1"
    assert res.refresh_token == "refresh.1"


def test_refresh_tokens_ok():
    repo = FakeUserRepo()
    u = repo.create_local(email="a@a.com", hashed_password="hash")
    assert u.id == 1

    tokens = FakeTokens(mode="ok")
    uc = RefreshTokens(users=repo, tokens=tokens)

    res = uc.execute(refresh_token="refresh.1")
    assert isinstance(res, TokensResult)
    assert res.access_token == "access.1"
    assert res.refresh_token == "refresh.1"


def test_refresh_tokens_expired_and_invalid():
    repo = FakeUserRepo()
    repo.create_local(email="a@a.com", hashed_password="hash")  # id=1

    tokens_exp = FakeTokens(mode="expired")
    uc_exp = RefreshTokens(users=repo, tokens=tokens_exp)
    with pytest.raises(TokenExpired):
        uc_exp.execute(refresh_token="refresh.1")

    tokens_inv = FakeTokens(mode="invalid")
    uc_inv = RefreshTokens(users=repo, tokens=tokens_inv)
    with pytest.raises(TokenInvalid):
        uc_inv.execute(refresh_token="refresh.1")


def test_refresh_tokens_user_not_found():
    repo = FakeUserRepo()
    tokens = FakeTokens(mode="ok")
    uc = RefreshTokens(users=repo, tokens=tokens)

    with pytest.raises(UserNotFound):
        uc.execute(refresh_token="refresh.123")
