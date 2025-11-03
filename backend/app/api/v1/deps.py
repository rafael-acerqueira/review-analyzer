from __future__ import annotations
from fastapi import Depends
from sqlmodel import Session
from functools import lru_cache

from app.domain.rag.use_cases import SearchRag
from app.domain.reviews.use_cases import SaveApprovedReview
from app.infra.db.admin_repository import SqlModelAdminRepository
from app.infra.db.rag_repository import SqlModelRagRepository
from app.infra.db.repositories import SqlModelUserRepository
from app.infra.db.reviews_repository import SqlModelReviewRepository
from app.infra.tokens.token_provider import SecurityTokenProvider

from app.infra.embeddings.local_sentence_transformer import LocalSentenceTransformerEmbedder

from app.domain.auth.use_cases import (
    RegisterUser,
    LoginUser,
    GoogleLogin,
    TokenExchange,
    RefreshTokens,
)

from app.domain.admin.use_cases import (
    ListReviews as AdminListReviews,
    DeleteReview as AdminDeleteReview,
    GetStats as AdminGetStats

)
from app.services.suggestion_service import SuggestionService


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

def get_query_embedder() -> LocalSentenceTransformerEmbedder:
    return _query_embedder_singleton()

def get_rag_repo(db: Session = Depends(get_db)) -> SqlModelRagRepository:
    return SqlModelRagRepository(db)

def get_rag_uc(
    embedder: LocalSentenceTransformerEmbedder = Depends(get_query_embedder),  # usa "query: " (E5)
    repo: SqlModelRagRepository = Depends(get_rag_repo),
) -> SearchRag:
    return SearchRag(embedder=embedder, repo=repo)

def get_suggestion_engine(
    rag_uc: SearchRag = Depends(get_rag_uc),
    qembed: LocalSentenceTransformerEmbedder = Depends(get_query_embedder),
) -> SuggestionService:
    def _retriever(query_text: str, k: int, min_score: float | None):
        res = rag_uc.execute(text=query_text, k=k, min_score=min_score)
        return [{"id": h.id, "text": h.text, "score": h.score} for h in res.hits]

    return SuggestionService(retriever=_retriever, query_embedder=qembed)

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
def _query_embedder_singleton() -> LocalSentenceTransformerEmbedder:
    return LocalSentenceTransformerEmbedder(query_prefix="query: ")

@lru_cache(maxsize=1)
def _doc_embedder_singleton() -> LocalSentenceTransformerEmbedder:
    return LocalSentenceTransformerEmbedder(query_prefix="passage: ")


def get_doc_embedder() -> LocalSentenceTransformerEmbedder:
    return _doc_embedder_singleton()

def get_save_approved_uc(
    repo: SqlModelReviewRepository = Depends(get_review_repo),
    doc_embedder: LocalSentenceTransformerEmbedder = Depends(get_doc_embedder),
) -> SaveApprovedReview:
    return SaveApprovedReview(repo=repo, embedder=doc_embedder)


def get_admin_repo(db: Session = Depends(get_db)) -> SqlModelAdminRepository:
    return SqlModelAdminRepository(db)

def get_admin_list_uc(repo: SqlModelAdminRepository = Depends(get_admin_repo)) -> AdminListReviews:
    return AdminListReviews(repo=repo)

def get_admin_delete_uc(repo: SqlModelAdminRepository = Depends(get_admin_repo)) -> AdminDeleteReview:
    return AdminDeleteReview(repo=repo)

def get_admin_stats_uc(repo: SqlModelAdminRepository = Depends(get_admin_repo)) -> AdminGetStats:
    return AdminGetStats(repo=repo)