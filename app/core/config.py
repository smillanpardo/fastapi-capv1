from pydantic_settings import BaseSettings

class Setting(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"

setting = Setting()

# from pydantic_settings import BaseSettings
# from pathlib import Path
# import os

# # ✅ Ruta absoluta al directorio del proyecto
# BASE_DIR = Path(__file__).resolve().parent.parent.parent

# class Setting(BaseSettings):
#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     DATABASE_URL: str
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

#     class Config:
#         env_file = str(BASE_DIR / ".env")  # ✅ Ruta completa
#         env_file_encoding = 'utf-8'
#         case_sensitive = False
#         extra = 'ignore'  # ✅ Ignora campos extra

# setting = Setting()