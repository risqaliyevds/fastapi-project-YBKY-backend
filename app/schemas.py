from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from pydantic.types import conint
from pydantic import EmailStr


class TokenData(BaseModel):
    id: Optional[str] = None


class RoomIN(BaseModel):

    name: str
    type: str
    capacity: int

    class Config:
        orm_mode = True

class RoomOUT(BaseModel):

    id: int
    name: str
    type: str
    capacity: int

    class Config:
        orm_mode = True


class Rooms(BaseModel):
    count: int
    results: List[RoomOUT]

    class Config:
        orm_mode = True

class RoomAvailability(BaseModel):
    start: datetime
    end: datetime

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda dt: dt.strftime("%Y-%m-%d %H:%M:%S")
        }

class UserOut(BaseModel):
    email: EmailStr
    first_name: str
    second_name: str

    class Config:
        orm_mode = True


class UserID(UserOut):
    id: int

class UserIn(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    second_name: str

class Token(BaseModel):
    access_token: str
    token_type: str


