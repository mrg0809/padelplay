from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from app.db.connection import supabase
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
    

@router.post("/payment_order_and_split_payment")
def create_payment_order_and_split_payment(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        player_id = current_user["id"]
        total_price = data["total_price"]
        pay_total = data["pay_total"]

        # Crear payment_order
        payment_order_response = supabase.from_("payment_orders").insert({
            "user_id": player_id,
            "total_amount": total_price, 
            "payment_status": "pending",
            "event_type": "reservation",
        }).execute()

        if not payment_order_response or not payment_order_response.data:
            raise HTTPException(status_code=500, detail="Error al crear la orden de pago.")

        payment_order_id = payment_order_response.data[0]["id"]

        # Crear split_payment
        if pay_total:
            amount = total_price
        else:
            amount = total_price / 4

        split_payment_response = supabase.from_("split_payments").insert({
            "payment_order_id": payment_order_id,
            "user_id": player_id,
            "amount": amount,
            "payment_status": "pending",
        }).execute()

        if not split_payment_response or not split_payment_response.data:
            raise HTTPException(status_code=500, detail="Error al crear el pago dividido.")

        return {
            "message": "Orden de pago y pago dividido creados exitosamente.",
            "payment_order_id": payment_order_id,
            "split_payment_id": split_payment_response.data[0]["id"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@router.post("/process-stripe-payment")
def process_stripe_payment(data: dict):
    payment_order_id = data["payment_order_id"]
    payment_method = data["payment_method"]
    payment_status = data["payment_status"]
    transaction_id = data["transaction_id"]
    is_full_payment = data["is_full_payment"] # Opcional

    # Actualizar payment_orders
    supabase.from_("payment_orders").update({
        "payment_method": payment_method,
        "payment_status": payment_status,
        "transaction_id": transaction_id,
        "is_full_payment": is_full_payment # Opcional
    }).eq("id", payment_order_id).execute()

    # Actualizar split_payments
    supabase.from_("split_payments").update({
        "payment_status": payment_status,
        "transaction_id": transaction_id
    }).eq("payment_order_id", payment_order_id).execute()

    return {"message": "Pago procesado y registros actualizados exitosamente."}