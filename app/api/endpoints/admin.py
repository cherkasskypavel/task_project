from typing import Optional
from fastapi import APIRouter, Depends

import app.api.schemas.user as u_sch
import app.api.schemas.group as gr
import app.core.security.auth as auth
from app.services.admin_service import AdminService
from app.utils.main_uow import MainUOW
from app.utils.unitofwork import IUnitOfWork

admin = APIRouter(prefix="/admin")

async def get_admin_service(uow: IUnitOfWork = Depends(MainUOW)) -> AdminService:
    return AdminService(uow)


@admin.post("/add_group")
async def add_group(group: gr.GroupInput, 
                    admin: u_sch.UserFromToken = Depends(auth.get_user_from_token),
                    service: AdminService = Depends(get_admin_service)):
        
    return await service.add_group(admin, group)


@admin.patch("/add_user_to_group")
async def add_user_to_group(add_scheme: gr.UserGroupScheme,
                            admin: u_sch.UserFromToken = Depends(auth.get_user_from_token),
                            service: AdminService = Depends(get_admin_service)):
    result = await service.add_users_to_group(admin, add_scheme)
    return {"msg": {"Успешное добавление пользователей в группу:": result}} 
    


@admin.delete("/delete_user_from_group")
async def delete_user_from_group(delete_scheme: gr.UserGroupScheme,
                                 admin: u_sch.UserFromToken = Depends(auth.get_user_from_token),
                                 service: AdminService = Depends(get_admin_service)):
    result = await service.delete_users_from_group(admin, delete_scheme)
    return {"msg": {"Успешное удаление пользователей из группы:": result}} 



@admin.get("/groups_and_users")
async def get_group_and_users(group: Optional[str] = None,
                               admin: u_sch.UserFromToken = Depends(auth.get_user_from_token),
                               service: AdminService = Depends(get_admin_service)):
    result = await service.get_group_and_users(admin, group)
    return result

