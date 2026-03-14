from fastapi import FastAPI
from slowapi import Limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
import redis

#connect redis client
redis_client = redis.Redis(host="localhost",port=6379 , db=0)

#create limiter to limit ip
limiter = Limiter(
    key_func=get_remote_address, #determines ip
    storage_uri="redis://localhost:6379/0" #stores data in redis db 0
)

#export limiter and put it in main.py to access teh slow api middleware globally