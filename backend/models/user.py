from sqlalchemy import Column, Integer, String
from backend.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    github_url = Column(String)
    github_token = Column(String)
    linkedin_id = Column(String, nullable=True)
    leetcode_id = Column(String, nullable=True)
    gmail = Column(String, nullable=True)
    mobile_number = Column(String, nullable=True)
