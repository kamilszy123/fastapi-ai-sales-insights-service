from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

DATABASE_URL = (
    f"postgresql://"
    f"{settings.postgres_password}"
    f"@db:5432/"
    f"{settings.postgres_db}"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
