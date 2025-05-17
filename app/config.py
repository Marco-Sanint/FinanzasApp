from fastapi import FastAPI
from .database import get_db

app = FastAPI(title="Gestor de Finanzas Personales")

# Inyectar dependencia de la base de datos
def get_db_dependency():
    return get_db