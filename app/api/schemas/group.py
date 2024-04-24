from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Iterable, List, Optional, Union

from app.api.schemas.user import UserReturn, UserSafeReturn

class GroupInput(BaseModel):
    name: str = Field(default='')
    description: str = Field(default='')


class GroupReturn(GroupInput):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserGroupScheme(BaseModel):
    name: str = Field(default='')
    members: List[str] = Field(default=[''])

    model_config = ConfigDict(from_attributes=True)

    # @field_validator("members")
    # @classmethod
    # def correct_members_typing(cls, members):
    #     if members:
    #         # print(type(members[0]), "<-------------------------------------------")
    #         if type(members[0]) in (str, UserReturn):
    #             return members
    #         else:
    #             raise ValueError("Некорректные данные в поле members")
    #     else:
    #         return members
        

class UserGroupSchemeReturn(BaseModel):
    name: str
    members: List[UserSafeReturn]

    model_config = ConfigDict(from_attributes=True)
