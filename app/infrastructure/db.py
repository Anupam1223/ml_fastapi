from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = "postgresql://postgres:anupam@localhost:5432/ml_fastapi"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

try:
    with engine.connect() as conn:
        print("Database exists!")
except Exception as e:
    print("Database does not exist!", e)
    
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
Base = declarative_base()
