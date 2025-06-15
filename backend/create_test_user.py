from app.database import engine
from app.models.user import User
from app.security import hash_password
from sqlmodel import SQLModel, Session

SQLModel.metadata.create_all(engine)

with Session(engine) as session:
    user = User(
        email="user@example.com",
        hashed_password=hash_password("password123"),
        provider="credentials",
        role="user"
    )
    session.add(user)
    session.commit()
    print("Test user created.")