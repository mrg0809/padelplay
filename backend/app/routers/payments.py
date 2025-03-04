from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

# Configuración de Espiral
ESPIRAL_API_URL = settings.ESPIRAL_API_URL
ESPIRAL_API_KEY = settings.ESPIRAL_API_KEY  


class CardHolder(BaseModel):
    name: str
    email: str
    phone: str

class Address(BaseModel):
    country: str
    state: str
    city: str
    numberExt: str
    numberInt: Optional[str] = None
    zipCode: str
    street: str

class TransactionItem(BaseModel):
    name: str
    price: float
    description: str
    quantity: int

class Transaction(BaseModel):
    items: List[TransactionItem]
    total: float
    currency: str

class LinkDetails(BaseModel):
    name: str
    email: str
    reusable: bool
    enableCard: bool
    enableReference: bool
    securityType3D: bool
    bank: int  # 1 para tarjeta, 2 para transferencia

class Webhook(BaseModel):
    redirectUrl: str
    redirectErrorUrl: str
    backPage: str
    redirectData: dict
    redirectErrorData: dict

class CreatePaymentRequest(BaseModel):
    cardHolder: CardHolder
    address: Address
    transaction: Transaction
    linkDetails: LinkDetails
    webhook: Webhook
    metadata: dict

# Endpoint para generar un token de pago
@router.post("/create-payment")
async def create_payment(request: CreatePaymentRequest, current_user=Depends(get_current_user)):
    try:
        # Datos para enviar a Espiral
        payment_data = {
            "cardHolder": request.cardHolder.model_dump(),
            "address": request.address.model_dump(),
            "transaction": request.transaction.model_dump(),
            "linkDetails": request.linkDetails.model_dump(),
            "webhook": request.webhook.model_dump(),
            "metadata": request.metadata,
        }

        # Llamar a la API de Espiral para generar el token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ESPIRAL_API_URL}?key={ESPIRAL_API_KEY}",
                json=payment_data,
                headers={"Content-Type": "application/json"},
            )

            # Verificar si la respuesta es exitosa
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=response.json().get("detail", "Error al generar el token de pago"),
                )

            return response.json()  # Devuelve la respuesta de Espiral (token y URL de pago)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))