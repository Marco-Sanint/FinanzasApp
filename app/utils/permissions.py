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

    @abstractmethod
    def can_read_transaction(self) -> bool:
        pass

    @abstractmethod
    def can_edit_transaction(self) -> bool:
        pass

    @abstractmethod
    def can_delete_transaction(self) -> bool:
        pass

    @abstractmethod
    def can_create_budget(self) -> bool:
        pass

    @abstractmethod
    def can_read_budget(self) -> bool:
        pass

    @abstractmethod
    def can_update_budget(self) -> bool:
        pass

    @abstractmethod
    def can_delete_budget(self) -> bool:
        pass

    @abstractmethod
    def can_sync_budget(self) -> bool:
        pass

    @abstractmethod
    def can_generate_report(self) -> bool:
        pass


class AdminPermissions(PermissionController):
    def can_create_user(self) -> bool:
        return True  # Admin puede crear usuarios

    def can_read_user(self) -> bool:
        return True  # Admin puede leer todos los usuarios

    def can_update_user(self) -> bool:
        return True  # Admin puede actualizar todos los usuarios

    def can_delete_user(self) -> bool:
        return True  # Admin puede eliminar usuarios

    def can_change_role(self) -> bool:
        return True  # Admin puede cambiar roles

    def can_create_questionnaire(self) -> bool:
        return True  # Admin puede crear cuestionarios

    def can_read_questionnaire(self) -> bool:
        return True  # Admin puede leer todos los cuestionarios

    def can_update_questionnaire(self) -> bool:
        return True  # Admin puede actualizar todos los cuestionarios

    def can_delete_questionnaire(self) -> bool:
        return True  # Admin puede eliminar todos los cuestionarios

    def can_manage_verification_codes(self) -> bool:
        return True  # Admin puede gestionar códigos de verificación

    def can_create_transaction(self) -> bool:
        return True  # Admin puede crear transacciones

    def can_read_transaction(self) -> bool:
        return True  # Admin puede leer todas las transacciones

    def can_edit_transaction(self) -> bool:
        return True  # Admin puede editar todas las transacciones

    def can_delete_transaction(self) -> bool:
        return True  # Admin puede eliminar transacciones

    def can_create_budget(self) -> bool:
        return True  # Admin puede crear presupuestos

    def can_read_budget(self) -> bool:
        return True  # Admin puede leer todos los presupuestos

    def can_update_budget(self) -> bool:
        return True  # Admin puede actualizar todos los presupuestos

    def can_delete_budget(self) -> bool:
        return True  # Admin puede eliminar presupuestos

    def can_sync_budget(self) -> bool:
        return True  # Admin puede sincronizar presupuestos

    def can_generate_report(self) -> bool:
        return True  # Admin puede generar reportes


class ClientPermissions(PermissionController):
    def can_create_user(self) -> bool:
        return True  # Cliente puede crear su propia cuenta (registro)

    def can_read_user(self) -> bool:
        return False  # Solo puede leer su propio usuario (controlado en rutas)

    def can_update_user(self) -> bool:
        return False  # Solo puede actualizar su propio usuario (controlado en rutas)

    def can_delete_user(self) -> bool:
        return False  # Cliente no puede eliminar usuarios

    def can_change_role(self) -> bool:
        return False  # Cliente no puede cambiar roles

    def can_create_questionnaire(self) -> bool:
        return True  # Cliente puede crear sus propios cuestionarios

    def can_read_questionnaire(self) -> bool:
        return False  # Solo puede leer sus propios cuestionarios (controlado en rutas)

    def can_update_questionnaire(self) -> bool:
        return True  # Solo puede actualizar sus propios cuestionarios (controlado en rutas)

    def can_delete_questionnaire(self) -> bool:
        return False  # Solo puede eliminar sus propios cuestionarios (controlado en rutas)

    def can_manage_verification_codes(self) -> bool:
        return False  # Cliente no puede gestionar códigos de verificación

    def can_create_transaction(self) -> bool:
        return True  # Cliente puede crear sus propias transacciones

    def can_read_transaction(self) -> bool:
        return False  # Solo puede leer sus propias transacciones (controlado en rutas)

    def can_edit_transaction(self) -> bool:
        return False  # Solo puede editar sus propias transacciones (controlado en rutas)

    def can_delete_transaction(self) -> bool:
        return False  # Solo puede eliminar sus propias transacciones (controlado en rutas)

    def can_create_budget(self) -> bool:
        return True  # Cliente puede crear su propio presupuesto

    def can_read_budget(self) -> bool:
        return False  # Solo puede leer sus propios presupuestos (controlado en rutas)

    def can_update_budget(self) -> bool:
        return False  # Solo puede actualizar sus propios presupuestos (controlado en rutas)

    def can_delete_budget(self) -> bool:
        return False  # Solo puede eliminar sus propios presupuestos (controlado en rutas)

    def can_sync_budget(self) -> bool:
        return True  # Cliente puede sincronizar sus propios presupuestos

    def can_generate_report(self) -> bool:
        return True  # Cliente puede generar reportes de sus propios presupuestos


class EditorPermissions(PermissionController):
    def can_create_user(self) -> bool:
        return True  # Editor no puede crear usuarios

    def can_read_user(self) -> bool:
        return False  # Editor no puede leer usuarios

    def can_update_user(self) -> bool:
        return False  # Editor no puede actualizar usuarios

    def can_delete_user(self) -> bool:
        return False  # Editor no puede eliminar usuarios

    def can_change_role(self) -> bool:
        return False  # Editor no puede cambiar roles

    def can_create_questionnaire(self) -> bool:
        return True  # Editor puede crear cuestionarios

    def can_read_questionnaire(self) -> bool:
        return True  # Editor puede leer todos los cuestionarios

    def can_update_questionnaire(self) -> bool:
        return True  # Editor puede actualizar todos los cuestionarios

    def can_delete_questionnaire(self) -> bool:
        return True  # Editor puede eliminar todos los cuestionarios

    def can_manage_verification_codes(self) -> bool:
        return False  # Editor no puede gestionar códigos de verificación

    def can_create_transaction(self) -> bool:
        return True  # Editor puede crear transacciones

    def can_read_transaction(self) -> bool:
        return True  # Editor puede leer todas las transacciones

    def can_edit_transaction(self) -> bool:
        return True  # Editor puede editar todas las transacciones

    def can_delete_transaction(self) -> bool:
        return False  # Editor no puede eliminar transacciones

    def can_create_budget(self) -> bool:
        return False  # Editor no puede crear presupuestos

    def can_read_budget(self) -> bool:
        return False  # Editor no puede leer presupuestos

    def can_update_budget(self) -> bool:
        return False  # Editor no puede actualizar presupuestos

    def can_delete_budget(self) -> bool:
        return False  # Editor no puede eliminar presupuestos

    def can_sync_budget(self) -> bool:
        return False  # Editor no puede sincronizar presupuestos

    def can_generate_report(self) -> bool:
        return False  # Editor no puede generar reportes


def get_permissions(role: Role) -> PermissionController:
    if role == Role.admin:
        return AdminPermissions()
    elif role == Role.editor:
        return EditorPermissions()
    return ClientPermissions()