# utils/permissions.py
from abc import ABC, abstractmethod
from ..models.role import Role

class PermissionController(ABC):
    @abstractmethod
    def can_create_transaction(self) -> bool:
        pass

    @abstractmethod
    def can_delete_user(self) -> bool:
        pass

class AdminPermissions(PermissionController):
    def can_create_transaction(self) -> bool:
        return True

    def can_delete_user(self) -> bool:
        return True

class ClientPermissions(PermissionController):
    def can_create_transaction(self) -> bool:
        return True

    def can_delete_user(self) -> bool:
        return False

class EditorPermissions(PermissionController):
    def can_create_transaction(self) -> bool:
        return True

    def can_delete_user(self) -> bool:
        return False

def get_permissions(role: Role) -> PermissionController:
    if role == Role.admin:
        return AdminPermissions()
    elif role == Role.editor:
        return EditorPermissions()
    return ClientPermissions()