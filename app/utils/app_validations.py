from pydantic import BaseModel
from datetime import datetime

class CreateUser(BaseModel):
    telegram_id: str

class CreateRemainder(BaseModel):
    telegram_id : str
    message : str
    scheduled_time : datetime

class ListRemainder(BaseModel):
    telegram_id : str

class DeleteRemainder(BaseModel):
    telegram_id : str
    remainder_id : int