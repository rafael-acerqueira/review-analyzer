import time
import uuid
from typing import Dict
from jose import jwt
import os
from dotenv import load_dotenv

load_dotenv()

DRAFT_SECRET = os.getenv("DRAFT_SECRET")
DRAFT_ALG = "HS256"
DRAFT_TTL_SECONDS = 60 * 30

class JwtDraftProvider:
    def __init__(self, secret: str = DRAFT_SECRET, alg: str = DRAFT_ALG, ttl: int = DRAFT_TTL_SECONDS):
        self.secret = secret
        self.alg = alg
        self.ttl = ttl

    def create(self, *, user_id: int, text: str, group_id: str) -> str:
        now = int(time.time())
        payload = {
            "sub": str(user_id),
            "text": text,
            "group_id": group_id,
            "iat": now,
            "exp": now + self.ttl,
            "typ": "review_draft",
        }
        return jwt.encode(payload, self.secret, algorithm=self.alg)

    def decode(self, token: str) -> Dict:
        return jwt.decode(token, self.secret, algorithms=[self.alg])
