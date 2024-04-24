from datetime import datetime, timedelta

from fastapi import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
import jwt


from app.api.schemas.user import UserLogin, UserReturn, UserFromToken
from app.api.schemas.access_token import Token
from app.core.security.cryptography import verify_password
from app.core.config import settings

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def generate_jwt(payload: dict):
    expire_time = datetime.now() + timedelta(minutes=settings.JWT_EXPIRE_DELTA)
    algorithm = settings.JWT_ALGORITHM
    secret_key = settings.JWT_KEY

    payload.update({"exp": expire_time})

    return jwt.encode(payload=payload, algorithm=algorithm, key=secret_key) 


def authenticate_user(logging_user: UserLogin,
                      db_user: UserReturn) -> Token:
    if not verify_password(logging_user.password,
                       db_user.password):
        raise ValueError("Ошибка аутентификации")
    else:
        token_payload = {
            "username": db_user.username,
            "role": db_user.role
        }

    return generate_jwt(token_payload)


def get_user_from_token(token: str = Depends(oauth2scheme)):
    user = jwt.decode(token,
                      key=settings.JWT_KEY, 
                      algorithms=[settings.JWT_ALGORITHM])
    
    return UserFromToken.model_validate(user)
