from app.use_cases.user.create_user import create_user_use_case
from app.use_cases.user.login_user import login_user_use_case
from app.use_cases.user.get_user_by_id import get_user_by_id_use_case
from app.use_cases.user.list_users import list_users_use_case
from app.use_cases.user.update_user import update_user_use_case
from app.use_cases.user.delete_user import delete_user_use_case
from app.interfaces.schemas.user_request import (
    UserCreateRequest,
    UserLoginRequest,
    UserUpdateRequest,
    UserQueryRequest
)

class UserController:
    def __init__(self):
        self.create_user_use_case = create_user_use_case
        self.login_user_use_case = login_user_use_case
        self.get_user_by_id_use_case = get_user_by_id_use_case
        self.list_users_use_case = list_users_use_case
        self.update_user_use_case = update_user_use_case
        self.delete_user_use_case = delete_user_use_case

    async def create_user(self, request: UserCreateRequest):
        user = await self.create_user_use_case.execute(request.email, request.password)
        return {"user": user, "message": "Usuario creado exitosamente"}

    async def login_user(self, request: UserLoginRequest):
        token, user = await self.login_user_use_case.execute(request.email, request.password)
        from app.core.security import create_token_response_data
        return create_token_response_data(token, user) | {"user": user}

    async def get_user_by_id(self, user_id: str, current_user):
        return await self.get_user_by_id_use_case.execute(user_id, current_user.id)

    async def list_users(self, query: UserQueryRequest, current_user):
        users, total = await self.list_users_use_case.execute(
            requesting_user_id=current_user.id,
            skip=query.skip,
            limit=query.limit
        )
        from app.interfaces.schemas.user_response import users_to_list_response
        return users_to_list_response(users, total, query.skip, query.limit)

    async def update_user(self, user_id: str, request: UserUpdateRequest, current_user):
        user = await self.update_user_use_case.execute(
            user_id=user_id,
            requesting_user_id=current_user.id,
            new_email=request.email,
            new_password=request.password
        )
        return {"user": user, "message": "Usuario actualizado exitosamente"}

    async def delete_user_soft(self, user_id: str, current_user):
        user = await self.delete_user_use_case.execute_soft_delete(user_id, current_user.id)
        return {"message": "Usuario desactivado exitosamente", "deleted_id": user.id}

    async def delete_user_hard(self, user_id: str, current_user):
        deleted_id = await self.delete_user_use_case.execute_hard_delete(user_id, current_user.id)
        return {"message": "Usuario eliminado permanentemente", "deleted_id": deleted_id}

    async def reactivate_user(self, user_id: str, current_user):
        user = await self.delete_user_use_case.reactivate_user(user_id, current_user.id)
        return {"user": user, "message": "Usuario reactivado exitosamente"}

# Instancia global
user_controller = UserController()
