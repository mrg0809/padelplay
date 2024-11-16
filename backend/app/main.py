from fastapi import FastAPI
from app.routers import auth

app = FastAPI()

# Registrar routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Padel API"}
