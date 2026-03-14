from fastapi import FastAPI
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import redis
import os
from dotenv import load_dotenv
load_dotenv()


REDIS_URL = os.getenv("REDIS_URL","redis://localhost:6379/0")
#connect redis client
redis_client = redis.Redis.from_url(REDIS_URL)

#create limiter to limit ip
limiter = Limiter(
    key_func=get_remote_address, #determines ip
    storage_uri=REDIS_URL #stores data in redis db 0
)

#export limiter and put it in main.py to access teh slow api middleware globally