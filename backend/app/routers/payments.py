from fastapi import APIRouter, HTTPException, Depends, Body, Path, Response, status
from pydantic import BaseModel
from app.db.connection import supabase
import stripe
from app.core.config import settings
from app.core.security import get_current_user
from app.utils.stripe_utils import get_or_create_stripe_customer, get_stripe_customer_id


router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

class User(BaseModel):
    id: str
    email: str

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


@router.post("/setup-intent")
async def create_setup_intent(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get('id')
    user_email = current_user.get('email')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in authentication data.")
    try:
        stripe_customer_id = await get_or_create_stripe_customer(
            user_id=str(user_id), # Asegúrate que sea string si Stripe lo espera así
            user_email=user_email,
        )

        setup_intent = stripe.SetupIntent.create(
            customer=stripe_customer_id,
            automatic_payment_methods={"enabled": True},
             usage='off_session', # Para guardar fuera de un pago
        )
        return {"clientSecret": setup_intent.client_secret}
    except HTTPException as http_exc: # Re-lanzar excepciones HTTP de los helpers
         raise http_exc
    except Exception as e:
        print(f"Error creating SetupIntent: {e}")
        raise HTTPException(status_code=500, detail="No se pudo iniciar la configuración de pago.")
    

@router.get("/payment-methods")
async def list_payment_methods(current_user: dict = Depends(get_current_user)): 
    user_id = current_user.get('id')
    if not user_id:
         raise HTTPException(status_code=401, detail="User ID not found in authentication data.")
    stripe_customer_id = await get_stripe_customer_id(user_id=str(user_id))
    if not stripe_customer_id:
        return [] # Si no tiene cliente Stripe, no tiene métodos guardados

    try:
        payment_methods = stripe.PaymentMethod.list(
            customer=stripe_customer_id,
            type="card",
        )
        # Formatear para el frontend
        formatted_methods = [
            {
                "id": pm.id,
                "brand": pm.card.brand,
                "last4": pm.card.last4,
                "expMonth": pm.card.exp_month,
                "expYear": pm.card.exp_year,
                # Puedes añadir is_default aquí si lo implementas
            }
            for pm in payment_methods.data
        ]
        return formatted_methods
    except stripe.error.StripeError as e:
         print(f"Stripe error listing payment methods: {e}")
         return [] 
    except Exception as e:
         print(f"Error listing payment methods: {e}")
         raise HTTPException(status_code=500, detail="Error al obtener métodos de pago.")
    

@router.delete("/payment-methods/{pm_id}")
async def detach_payment_method(
    pm_id: str = Path(..., title="Stripe Payment Method ID"),
    current_user: dict = Depends(get_current_user)
):
    user_id = current_user.get('id')
    if not user_id:
         raise HTTPException(status_code=401, detail="User ID not found in authentication data.")
    stripe_customer_id = await get_stripe_customer_id(user_id=str(user_id))
    if not stripe_customer_id:
         raise HTTPException(status_code=404, detail="Perfil de cliente no encontrado.")

    try:
        # **VERIFICACIÓN DE SEGURIDAD (Opcional pero Recomendada)**
        # Recupera el método para asegurar que pertenece al cliente actual
        payment_method = await stripe.PaymentMethod.retrieve(pm_id)
        if payment_method.customer != stripe_customer_id:
             raise HTTPException(status_code=403, detail="Permiso denegado.")

        # Si pertenece, desasócialo
        await stripe.PaymentMethod.detach(pm_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except stripe.error.InvalidRequestError as e:
         # Puede ocurrir si el pm_id no existe o ya está desasociado
         print(f"Stripe InvalidRequestError detaching PM: {e}")
         raise HTTPException(status_code=404, detail="Método de pago no encontrado o inválido.")
    except stripe.error.StripeError as e:
         print(f"Stripe error detaching PM: {e}")
         raise HTTPException(status_code=500, detail="Error al eliminar método de pago.")
    except HTTPException as http_exc: # Re-lanzar 403/404
         raise http_exc
    except Exception as e:
         print(f"Error detaching PM: {e}")
         raise HTTPException(status_code=500, detail="Error interno al eliminar método de pago.")