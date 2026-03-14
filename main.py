from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.app_routes import router 
from app.redis.redis_config import limiter
from slowapi.middleware import SlowAPIMiddleware



app = FastAPI(title='RemindMe')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#attach limiter here
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.include_router(router, prefix='/api', tags=['API'])

@app.get('/')
def root():
    return {"message": "Welcome to RemindMe Bot"}