from abc import ABC, abstractmethod
from ..models.role import Role

class PermissionController(ABC):
    @abstractmethod
    def can_create_user(self) -> bool:
        pass

    @abstractmethod
    def can_read_user(self) -> bool:
        pass

    @abstractmethod
    def can_update_user(self) -> bool:
        pass

    @abstractmethod
    def can_delete_user(self) -> bool:
        pass

    @abstractmethod
    def can_change_role(self) -> bool:
        pass

    @abstractmethod
    def can_create_questionnaire(self) -> bool:
        pass

    @abstractmethod
    def can_read_questionnaire(self) -> bool:
        pass

    @abstractmethod
    def can_update_questionnaire(self) -> bool:
        pass

    @abstractmethod
    def can_delete_questionnaire(self) -> bool:
        pass

    @abstractmethod
    def can_manage_verification_codes(self) -> bool:
        pass

    @abstractmethod
    def can_create_transaction(self) -> bool:
        pass

class AdminPermissions(PermissionController):
    def can_create_user(self) -> bool:
        return True

    def can_read_user(self) -> bool:
        return True

    def can_update_user(self) -> bool:
        return True

    def can_delete_user(self) -> bool:
        return True

    def can_change_role(self) -> bool:
        return True

    def can_create_questionnaire(self) -> bool:
        return True

    def can_read_questionnaire(self) -> bool:
        return True

    def can_update_questionnaire(self) -> bool:
        return True

    def can_delete_questionnaire(self) -> bool:
        return True

    def can_manage_verification_codes(self) -> bool:
        return True

    def can_create_transaction(self) -> bool:
        return True

class ClientPermissions(PermissionController):
    def can_create_user(self) -> bool:
        return True

    def can_read_user(self) -> bool:
        return False  # Solo puede leer su propio usuario

    def can_update_user(self) -> bool:
        return False  # Solo puede actualizar su propio usuario

    def can_delete_user(self) -> bool:
        return False

    def can_change_role(self) -> bool:
        return False

    def can_create_questionnaire(self) -> bool:
        return True

    def can_read_questionnaire(self) -> bool:
        return False  # Solo puede leer sus propios cuestionarios

    def can_update_questionnaire(self) -> bool:
        return False  # Solo puede actualizar sus propios cuestionarios

    def can_delete_questionnaire(self) -> bool:
        return False  # Solo puede eliminar sus propios cuestionarios

    def can_manage_verification_codes(self) -> bool:
        return False

    def can_create_transaction(self) -> bool:
        return True

class EditorPermissions(PermissionController):
    def can_create_user(self) -> bool:
        return False

    def can_read_user(self) -> bool:
        return False

    def can_update_user(self) -> bool:
        return False

    def can_delete_user(self) -> bool:
        return False

    def can_change_role(self) -> bool:
        return False

    def can_create_questionnaire(self) -> bool:
        return True

    def can_read_questionnaire(self) -> bool:
        return True

    def can_update_questionnaire(self) -> bool:
        return True

    def can_delete_questionnaire(self) -> bool:
        return True

    def can_manage_verification_codes(self) -> bool:
        return False

    def can_create_transaction(self) -> bool:
        return True

def get_permissions(role: Role) -> PermissionController:
    if role == Role.admin:
        return AdminPermissions()
    elif role == Role.editor:
        return EditorPermissions()
    return ClientPermissions()