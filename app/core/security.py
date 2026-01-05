from jose import JWTError, jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from core.config import setting

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def crear_token(sub: str, role: str):
    expire = datetime.utcnow() + timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    data = {
        "sub": sub,
        "exp": expire,
        "role": role
    }
    token = jwt.encode(data, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return token

def verificar_token(token:str):
    try:
        payload= jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        return payload
    except JWTError:
        return None



def hash_password(password:str):
    return pwd_context.hash(password)

def verify_password(password:str, hashed:str):
    return pwd_context.verify(password, hashed)