from app.database import engine, SessionLocal
from app.models.user import User
from app.security import hash_password
from sqlmodel import SQLModel

SQLModel.metadata.create_all(engine)

db = SessionLocal()
user = User(
    email="user@example.com",
    hashed_password=hash_password("password123"),
    provider="credentials",
    role="user"
)
db.add(user)
db.commit()
db.close()
print("Test user created.")