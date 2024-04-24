import string

from pydantic import BaseModel, ConfigDict, Field, field_validator

class UserLogin(BaseModel):
    username: str = Field(default='')
    password: str = Field(default='')
    

class UserSignUp(UserLogin):
    
    email: str = Field(pattern=r"\w+@[a-z]+\.[a-z]{2, 3}", default='')
    
    @field_validator("password")
    @classmethod
    def validate_password(cls, value):
        if not (
            len(value) >= 8 and
            set(value).intersection(string.ascii_uppercase) and
            set(value).intersection(string.ascii_lowercase) and
            set(value).intersection(string.digits) and
            set(value).intersection(string.punctuation)
        ):
            raise ValueError("Пароль не соответствует следующим критериям:\n"
                             "1. Должен содержать 8 или более символов\n"
                             "2. Должен содержать хотябы одну заглавную букву\n"
                             "3. Должен содержать хотябы одну прописную букву\n"
                             "4. Должен содержать хотябы одну цифру\n"
                             "5. Должен содержать хотябы один символ пунктуации\n")
        else:
            return value

class UserReturn(UserSignUp):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str


class UserSafeReturn(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    role: str

    def __eq__(self, other):
        if isinstance(other, UserSafeReturn):
            return self.id == other.id
        else:
            raise NotImplementedError

    def __hash__(self):
        return hash(self.id)
        

class UserFromToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    username: str
    role: str
