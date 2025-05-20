from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.user import User
from fastapi import HTTPException
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TransactionService:
    def __init__(self, db: Session):
        self.db = db

    def create_transaction(self, transaction: dict, user_id: int) -> Transaction:
        db_transaction = Transaction(**transaction, user_id=user_id)
        self.db.add(db_transaction)
        self.db.commit()
        self.db.refresh(db_transaction)
        logger.info(f"Transacción creada con id: {db_transaction.id} por usuario: {user_id}")
        return db_transaction

    def get_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        if not transaction:
            logger.error(f"Transacción con id {transaction_id} no encontrada para usuario {user_id}")
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        return transaction

    def get_all_transactions(self, user_id: int) -> list[Transaction]:
        return self.db.query(Transaction).filter(Transaction.user_id == user_id).all()

    def update_transaction(self, transaction_id: int, transaction_update: dict, user_id: int) -> Transaction:
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transacción no encontrada")
        for key, value in transaction_update.items():
            if value is not None:  # Solo actualizar campos no nulos
                setattr(transaction, key, value)
        self.db.commit()
        self.db.refresh(transaction)
        return transaction

    def delete_transaction(self, transaction_id: int, user_id: int) -> dict:
        transaction = self.db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        if not transaction:
            logger.error(f"Transacción con id {transaction_id} no encontrada para usuario {user_id}")
            raise HTTPException(status_code=404, detail="Transacción no encontrada")

        self.db.delete(transaction)
        self.db.commit()
        logger.info(f"Transacción con id {transaction_id} eliminada por usuario {user_id}")
        return {"message": "Transacción eliminada exitosamente"}