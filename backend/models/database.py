from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings

# Source database (read-only)
source_engine = create_engine(settings.source_database_url)
SourceSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=source_engine)

# Target database (read-write)
target_engine = create_engine(settings.target_database_url)
TargetSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=target_engine)

Base = declarative_base()
metadata = MetaData()

def get_source_db():
    """Get source database session"""
    db = SourceSessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_target_db():
    """Get target database session"""
    db = TargetSessionLocal()
    try:
        yield db
    finally:
        db.close()