from fastapi import APIRouter, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from app.api.schemas.access_token import Token
import app.api.schemas.user as u_sch
from app.utils.unitofwork import IUnitOfWork
from app.utils.main_uow import MainUOW 
from app.services.user_service import UserService

auth = APIRouter(prefix="/auth")

async def get_user_service(uow: IUnitOfWork = Depends(MainUOW)) -> UserService:
    return UserService(uow) 

@auth.post("/signup")
async def signup(new_user: u_sch.UserSignUp,
                 user_service: UserService = Depends(get_user_service)):
    return await user_service.add_user(new_user)




@auth.post("/login", response_model=Token)
async def login(logging_user: OAuth2PasswordRequestForm = Depends(),
                user_service: UserService = Depends(get_user_service)):

    user = u_sch.UserLogin(username=logging_user.username,
                           password=logging_user.password)
    return await user_service.authorize_user(user)

