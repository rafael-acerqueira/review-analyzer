from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.security import hash_password

Base.metadata.create_all(bind=engine)

db = SessionLocal()

user = User(email="user@example.com", hashed_password=hash_password("password123"), role="user")
db.add(user)
db.commit()
db.close()

print("Test user created.")