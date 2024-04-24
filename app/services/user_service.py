from app.utils.unitofwork import IUnitOfWork
from app.api.schemas.user import UserSignUp, UserReturn, UserLogin
from fastapi import HTTPException, status

import app.core.security.cryptography as crypt
import app.core.security.auth as auth

class UserService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def add_user(self, new_user: UserSignUp) -> UserReturn:
        new_user_data: dict = new_user.model_dump()

        async with self.uow:
            user_repo = self.uow.repositories[0]
            filter = {"username": new_user.username} 
            user_in_db = await user_repo.get_one(**filter)
            if user_in_db is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="Пользователь с таким именем уже существует!")
            else:
                hashed_password = crypt.hash_password(new_user.password)
                new_user_data['password'] = hashed_password

                added_user = await user_repo.add_one(new_user_data)
                user_to_return = UserReturn.model_validate(added_user)
                await self.uow.commit()
                return user_to_return
        
    
    async def authorize_user(self, logging_user: UserLogin):

        async with self.uow:
            user_repo = self.uow.repositories[0]
            user_in_db = await user_repo.get_one(username=logging_user.username)
            if user_in_db is None:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Такого пользователя не существует")
            try:
                db_user = UserReturn.model_validate(user_in_db)
                authenticated_user_token = auth.authenticate_user(logging_user, db_user)
                return {"access_token" : authenticated_user_token,
                        "token_type": "bearer"}
            except ValueError as e:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=e)
            