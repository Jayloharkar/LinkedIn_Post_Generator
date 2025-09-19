from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    linkedin_post = Column(Text)
    source_blog = Column(String)
    keywords_matched = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_posted = Column(Boolean, default=False)
    is_approved = Column(Boolean, default=False)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./blog_posts.db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()