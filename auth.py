import enum
import os
import uuid
import logging
from datetime import datetime, timedelta
from random import randint

from jose import JWTError, jwt
#from pydantic import BaseModel

# Use
# openssl rand -hex 32
# to generate a secret key and then assign it to the environment variable JWT_AUTH_SECRET_KEY
SECRET_KEY = None
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

class OperationType(str, enum.Enum):
    CREATE = "created"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"

class UserType(str, enum.Enum):
    ADMIN = 'admin'
    TENANT = 'tenant'
    USER = 'user'
    METRIC_SENDER = 'instance'

class UserID():
    def __init__(self, user_type: UserType, **kwargs):
        self.type = user_type
        match self.type:
            case UserType.ADMIN:
                self.value = f"admin:{kwargs['username']}"
            case UserType.TENANT:
                self.value = f"tenant:{kwargs['tenant_id']}"
            case UserType.METRIC_SENDER:
                self.value = f"metric:{kwargs['username']}"
            case UserType.USER:
                self.value = f"user:{kwargs['tenant_id']}/{kwargs['user_id']}"
            case _:
                raise ValueError(f"Unknown user type {type}")
    def __str__(self):
        return self.value       
    

# def compose_userid(type: UserType, **kwargs) -> UserID:
#     """Produce a string with userid"""
#     match type:
#         case UserType.ADMIN:
#             return f"admin:{kwargs['username']}"
#         case UserType.TENANT:
#             return f"tenant:{kwargs['tenant_id']}"
#         case UserType.METRIC_SENDER:
#             return f"metric:{kwargs['username']}"
#         case UserType.USER:
#             return f"user:{kwargs['tenant_id']}/{kwargs['user_id']}"
#         case _:
#             raise ValueError(f"Unknown user type {type}")
        
def compose_obj_id(tenant_id: str, user_id: str = None) -> str:
    """Produce a string with object id"""
    if user_id:
        return f"{tenant_id}/{user_id}"
    else:
        return tenant_id
    
def load_secret_key(secret: str = None):
    global SECRET_KEY
    if secret:
        SECRET_KEY = secret
    else:
        # TODO: use GCP secrets for this
        SECRET_KEY = os.environ.get("JWT_AUTH_SECRET_KEY",
                            "18c87eb72c934c0013e0a0b817a410c31169da50db28714faf9e40e77a64aab1")
    
def generate_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return (encoded_jwt, expire)

def extra_token_info(obj: object) -> dict:
    """Generate extra info to be added to the token based on the object.
    Right now only used to add "super tenant" info"""
    
    if hasattr(obj, "is_super_tenant") and obj.is_super_tenant:
        return { "is_super_tenant": True }
    
    return {}

def generate_api_token(userid: UserID,
                       hours_to_live: int = None,
                       object: object = None):
    token_data = {"sub": userid.__str__() }
    token_data.update(extra_token_info(object))

    return generate_token(token_data,
                          timedelta(hours=hours_to_live) if hours_to_live else None)

def extract_jwt_data(token: str) -> dict:
    """Get the current user from the JWT token"""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
            
    except JWTError as je:
        logging.debug(f"Cannot decode JWT token {token} {je}")
        raise je

def generate_password() -> str:
    return str(uuid.uuid4()) + str(randint(100000, 999999))

load_secret_key()

if __name__ == "__main__":
    print(generate_token({"sub": "test"}, timedelta(minutes=100000)))
