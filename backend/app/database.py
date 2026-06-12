from sqlmodel import create_engine, Session

from app.core.settings import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, echo=settings.sql_echo)

def get_session():
    with Session(engine) as session:
        yield session
