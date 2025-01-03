from fastapi import FastAPI
from app.routers import auth, courts, clubs, matches, players, reservations, tournaments
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.DEBUG)
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
app.include_router(clubs.router)
app.include_router(courts.router)
app.include_router(matches.router, prefix="/matches", tags=["Matches"])
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["Tournaments"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Padel API"}
