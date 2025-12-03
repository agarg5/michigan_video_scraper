from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from app.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True)
    source = Column(String)
    url = Column(String)
    date = Column(DateTime)
    transcript = Column(Text)
    processed_at = Column(DateTime)

def init_db():
    Base.metadata.create_all(engine)
