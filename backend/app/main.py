from fastapi import FastAPI
from app.routers import auth, blocks, community, courts, clubs, discounts, lessons, matches, notifications, players, products, reservations, tournaments
from fastapi.middleware.cors import CORSMiddleware
import logging

#logging.basicConfig(level=logging.DEBUG)
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
app.include_router(blocks.router, prefix="/block", tags=["Blocks"])
app.include_router(clubs.router, prefix="/clubs", tags=["Clubs"])
app.include_router(courts.router, prefix="/courts", tags=["Courts"])
app.include_router(community.router, prefix="/community", tags=["Community"])
app.include_router(discounts.router, prefix="/promo", tags=["Discounts"])
app.include_router(lessons.router, prefix="/lessons", tags=["Lessons"])
app.include_router(matches.router, prefix="/matches", tags=["Matches"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(players.router, prefix="/players", tags=["Players"])
app.include_router(products.router, prefix="/products", tags=["Products"])
app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])
app.include_router(tournaments.router, prefix="/tournaments", tags=["Tournaments"])


@app.get("/")
async def root():
    return {"message": "Welcome to the Padelplay API"}
