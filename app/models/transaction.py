from sqlalchemy import Column, Integer, String, Enum, DateTime, DECIMAL, ForeignKey
from sqlalchemy.sql import func
from ..database import Base
import enum

class TransactionType(enum.Enum):
    income = "income"
    expense = "expense"

class CategoryEnum(enum.Enum):
    food = "food"
    transport = "transport"
    housing = "housing"
    entertainment = "entertainment"
    other = "other"

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    amount = Column(DECIMAL(10, 2))
    category = Column(Enum(CategoryEnum))
    description = Column(String(255))
    transaction_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())