from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")

async def hashing(password: str):
    return pwd_context.hash(password)

async def verify(current_password, hashed_password):
    return pwd_context.verify(current_password, hashed_password)