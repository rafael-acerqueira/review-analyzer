from __future__ import annotations
from fastapi import Depends
from sqlmodel import Session
from functools import lru_cache

from app.domain.reviews.use_cases import SaveApprovedReview
from app.infra.db.repositories import SqlModelUserRepository
from app.infra.tokens.token_provider import SecurityTokenProvider

from app.infra.embeddings.local_sentence_transformer import LocalSentenceTransformerEmbedder
from app.infra.db.rag_repository import SqlModelRagRepository
from app.domain.rag.use_cases import SearchRag


from app.domain.auth.use_cases import (
    RegisterUser,
    LoginUser,
    GoogleLogin,
    TokenExchange,
    RefreshTokens,
)

def _get_session_dep():
    from app.database import get_session  # lazy import
    for session in get_session():
        yield session


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




def get_review_repo(db: Session = Depends(get_db)):
    from app.infra.db.reviews_repository import SqlModelReviewRepository
    return SqlModelReviewRepository(db)

def get_sentiment_analyzer():
    from app.services.sentiment_analysis_service import SentimentAnalysisService
    return SentimentAnalysisService()

def get_suggestion_engine():
    from app.services.suggestion_service import SuggestionService
    return SuggestionService()

def get_save_approved_uc(repo = Depends(get_review_repo)) -> SaveApprovedReview:
    return SaveApprovedReview(repo)

def get_evaluate_text_uc(
    sentiment = Depends(get_sentiment_analyzer),
    sugg = Depends(get_suggestion_engine),
):
    from app.domain.reviews.use_cases import EvaluateText
    return EvaluateText(sentiment=sentiment, sugg=sugg)

def get_list_my_reviews_uc(
    repo = Depends(get_review_repo),
):
    from app.domain.reviews.use_cases import ListMyReviews
    return ListMyReviews(reviews=repo)


@lru_cache(maxsize=1)
def _embedder_singleton() -> LocalSentenceTransformerEmbedder:
    return LocalSentenceTransformerEmbedder()

def get_embedder() -> LocalSentenceTransformerEmbedder:
    return _embedder_singleton()

def get_rag_repo(db: Session = Depends(_get_session_dep)) -> SqlModelRagRepository:
    repo = SqlModelRagRepository(db)
    return repo


def get_rag_uc(
    embedder: LocalSentenceTransformerEmbedder = Depends(get_embedder),
    repo: SqlModelRagRepository = Depends(get_rag_repo),
) -> SearchRag:
    return SearchRag(embedder=embedder, repo=repo)