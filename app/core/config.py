
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_PATH: str
    TEST_DB_PATH: str
    DB_DIALECT: str
    DB_DRIVER: str
    SYNC_DB_DRIVER: str

    JWT_KEY: str
    JWT_ALGORITHM: str
    JWT_EXPIRE_DELTA: int

    @property
    def MAIN_DB(self):
        return self.DB_DIALECT + "+" + self.DB_DRIVER + self.DB_PATH
    
    @property
    def ALEMBIC_URL(self):
        return self.DB_DIALECT + "+" + self.SYNC_DB_DRIVER + self.DB_PATH
    
    
    @property
    def TEST_DB(self):
        return self.DB_DIALECT + "+" + self.SYNC_DB_DRIVER + self.TEST_DB_PATH
    

    class Config:
        env_file = ".env"

settings = Settings()
