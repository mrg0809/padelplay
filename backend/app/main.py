from fastapi import FastAPI
from app.routers import auth, courts
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto al origen de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los encabezados
)
# Registrar routers
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(courts.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Padel API"}
