from app.database.connection_config import base
from sqlalchemy import Column , ForeignKey , Boolean , Integer , String , DateTime
from datetime import datetime

class Users(base):
    __tablename__ = 'users'

    id = Column(Integer , primary_key=True , index=True)
    telegram_id = Column(String , nullable=False , unique=True)
    created_at = Column(DateTime , nullable=False , default=datetime.utcnow)


class Remainder(base):
    __tablename__ = 'remainders'

    id = Column(Integer , primary_key=True , index=True)
    user_id = Column(Integer , ForeignKey('users.id'), nullable=False)
    message = Column(String , nullable=False)
    scheduled_time = Column(DateTime , nullable=False)
    created_at = Column(DateTime , default=datetime.utcnow)
    is_sent = Column(Boolean , default=False)
    sent_at = Column(DateTime , nullable=True)