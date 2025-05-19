from sqlalchemy import Column, Integer, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Questionnaire(Base):
    __tablename__ = "questionnaires"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)
    ans1 = Column(JSON, nullable=False)
    ans2 = Column(JSON, nullable=False)
    ans3 = Column(JSON, nullable=False)
    ans4 = Column(JSON, nullable=False)
    monthly_report = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())