from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
import stripe
from app.core.config import settings
from app.core.security import get_current_user

router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

class PaymentIntentRequest(BaseModel):
    payment_order_id: str
    amount: int


@router.post("/create-payment-intent")
async def create_payment_intent(request_data: PaymentIntentRequest = Body(...)):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=request_data.amount,
            currency="mxn",
            metadata={"payment_order_id": request_data.payment_order_id},
        )
        return {"clientSecret": payment_intent.client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
