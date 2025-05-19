# models/roles.py
from enum import Enum as PyEnum

class Role(PyEnum):
    client = "client"
    editor = "editor"
    admin = "admin"