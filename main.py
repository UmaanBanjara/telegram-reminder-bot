from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.app_routes import router
from app.redis.redis_config import limiter
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database.connection_config import engine, base


app = FastAPI(title='RemindMe')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.include_router(router, prefix='/api', tags=['API'])


#creating tables on startup
@app.on_event("startup")
async def startup():
    from app.models.app_models import Users, Remainder
    async with engine.begin() as conn:
        await conn.run_sync(base.metadata.create_all)
    print("✅ Tables created successfully")


@app.get('/')
def root():
    return {"message": "Welcome to RemindMe Bot"}