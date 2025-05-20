# main.py
from .routes import questionnaire_routes
from fastapi import FastAPI
from .database import get_db
from .routes.user_routes import router as user_router
from .routes.verification_routes import router as verification_router
from .routes.transaction_routes import router as transaction_router
from .routes.budget_routes import router as budget_router

app = FastAPI(title="Gestor de Finanzas Personales")

# Inyectar dependencia de la base de datos
def get_db_dependency():
    return get_db

app.include_router(user_router)
app.include_router(verification_router)
app.include_router(questionnaire_routes.router)
app.include_router(budget_router)
app.include_router(transaction_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)