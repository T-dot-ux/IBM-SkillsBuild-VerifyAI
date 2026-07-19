from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from utils.config import settings

# If the URL is standard postgres, we might need asyncpg or just use standard psycopg2. 
# We'll use standard synchronous for simplicity, but FastAPI works well with async databases too.
# For SQLite fallback, we need connect_args={"check_same_thread": False}.

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL, connect_args=connect_args
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
