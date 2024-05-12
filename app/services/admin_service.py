from typing import List, Optional
from fastapi import HTTPException, status
from app.api.schemas.group import UserGroupSchemeReturn, UserGroupScheme
from app.api.schemas.group import GroupInput, GroupReturn
from app.api.schemas.user import UserFromToken
from app.utils.unitofwork import IUnitOfWork



class AdminService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow


    async def add_users_to_group(self, admin: UserFromToken,
                                addition_scheme: UserGroupScheme) -> UserGroupSchemeReturn:
        if admin.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Вам доступ запрещен.")
        else:
            async with self.uow:
                u_repo = self.uow.repositories[0]
                g_repo = self.uow.repositories[1]

                db_group = await g_repo.get_one(
                    name=addition_scheme.name)
                if db_group is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Такой группы не существует")
                else:
                    for member in addition_scheme.members:
                        db_user = await u_repo.get_one(username=member)
                        if db_user is None:
                            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                                detail=f"Пользователь {member} не найден")
                        else:
                            await g_repo.add_member(db_user, db_group)

                await self.uow.commit()
                await self.uow.refresh(db_group)
                return UserGroupSchemeReturn.model_validate(db_group)
            

    async def delete_users_from_group(self, admin: UserFromToken,
                                     delete_scheme: UserGroupScheme) -> UserGroupSchemeReturn:
        if admin.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Вам доступ запрещен.")
        else:
            async with self.uow:
                g_repo = self.uow.repositories[1]
                
                db_group = await g_repo.get_one(
                    name=delete_scheme.name)
                if db_group is None:
                    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                        detail="Такой группы не существует")
                else:
                    for m in await g_repo.get_members(db_group):
                        self.uow.refresh(m)
                        if m.username in delete_scheme.members:
                            await g_repo.delete_member(m, db_group)
                                
                await self.uow.commit()
                await self.uow.refresh(db_group)

                return UserGroupSchemeReturn.model_validate(db_group)

    
    async def add_group(self, admin: UserFromToken, 
                        group: GroupInput) -> GroupReturn:
        if admin.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Вам доступ запрещен.")
        else:
            async with self.uow:
                g_repo = self.uow.repositories[1]

                new_group = await g_repo.add_one(group.model_dump())
                group_to_return = GroupReturn.model_validate(new_group)
                await self.uow.commit()
                return group_to_return
                
    
    async def get_group_and_users(self, admin: UserFromToken,
                                  group: Optional[str]) -> List[UserGroupSchemeReturn]:
        if admin.role != "admin":
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Вам доступ запрещен.")
        else:
            async with self.uow:
                g_repo = self.uow.repositories[1]
                return_data: List[UserGroupSchemeReturn] = []

                if group is None:
                    db_groups = await g_repo.get_all()
                    for group in db_groups:
                        return_data.append(
                            UserGroupSchemeReturn.model_validate(group)
                        )
                else:
                    db_group = await g_repo.get_one(name=group)
                    return_data.append(db_group)    
            return return_data
                    


 
