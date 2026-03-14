from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.app_routes import router  

app = FastAPI(title='RemindMe')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix='/api', tags=['API'])

@app.get('/')
def root():
    return {"message": "Welcome to RemindMe Bot"}