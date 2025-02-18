from sqlalchemy import Column, String, Float, JSON, Text
from sqlalchemy.dialects.postgresql import ARRAY

from ..base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    url = Column(String, nullable=False)
    title = Column(String)
    status = Column(String, nullable=False)  # pending, processing, completed, error
    error = Column(String)
    progress = Column(Float, default=0.0)
    steps_completed = Column(ARRAY(String))
    
    # Results
    transcript = Column(Text)
    embeddings = Column(JSON)
    summary = Column(JSON) 