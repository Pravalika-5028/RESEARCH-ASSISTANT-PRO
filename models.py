from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    title = Column(String)
    url = Column(String)
    snippet = Column(Text)
    score = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow) 
    