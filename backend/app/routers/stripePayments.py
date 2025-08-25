from fastapi import APIRouter, HTTPException, Depends, Body, Path, Response, status
from pydantic import BaseModel
from typing import Optional
from app.db.connection import supabase
import stripe
import json
from app.core.config import settings
from app.core.security import get_current_user
from app.utils.stripe_utils import get_or_create_stripe_customer, get_stripe_customer_id


router = APIRouter()

stripe.api_key = settings.STRIPE_SECRET_KEY

class User(BaseModel):
    id: str
    email: str

class PaymentIntentRequest(BaseModel):
    amount: int
    payment_order_id: str
    customer: Optional[str] = None 
    metadata: Optional[dict] = None


@router.post("/create-payment-intent")
async def create_payment_intent(request_data: PaymentIntentRequest = Body(...)):
    try:
        payment_intent_params = {
            "amount": request_data.amount,
            "currency": "mxn",
            "metadata": {"payment_order_id": request_data.payment_order_id},
        }
        
        if request_data.customer:
            payment_intent_params["customer"] = request_data.customer
            
        payment_intent = stripe.PaymentIntent.create(**payment_intent_params)
        return {"clientSecret": payment_intent.client_secret}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/payment_order_and_split_payment")
def create_payment_order_and_split_payment(data: dict, current_user: dict = Depends(get_current_user)):
    try:
        # Debug: Log received data and current user
        print(f"Received data: {data}")
        print(f"Current user: {current_user}")
        
        # Check if current_user has required fields
        if not current_user or not current_user.get("id"):
            print(f"Invalid current_user: {current_user}")
            raise HTTPException(status_code=401, detail="Invalid user authentication")
        
        player_id = current_user["id"]
        
        # Validate required fields in data
        required_fields = ["total_price", "pay_total", "item_type", "participants"]
        for field in required_fields:
            if field not in data:
                print(f"Missing required field: {field}")
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Validate data types
        try:
            total_price = float(data["total_price"])
        except (ValueError, TypeError):
            print(f"Invalid total_price: {data.get('total_price')}")
            raise HTTPException(status_code=400, detail="Invalid total_price: must be a number")
            
        try:
            is_full_payment = bool(data["pay_total"])
        except (ValueError, TypeError):
            print(f"Invalid pay_total: {data.get('pay_total')}")
            raise HTTPException(status_code=400, detail="Invalid pay_total: must be boolean")
            
        try:
            num_players = int(data["participants"])
        except (ValueError, TypeError):
            print(f"Invalid participants: {data.get('participants')}")
            raise HTTPException(status_code=400, detail="Invalid participants: must be a number")
        
        event_type = str(data["item_type"])
        recipient_id = data.get("recipient_id")  # Use .get() since this can be None
        
        # Additional validation for tournament-specific fields
        if event_type == "tournament":
            if not data.get("item_id"):
                print("Missing tournament ID for tournament registration")
                raise HTTPException(status_code=400, detail="Tournament ID is required for tournament registrations")
            if not data.get("player2_email"):
                print("Missing player2_email for tournament registration")
                raise HTTPException(status_code=400, detail="Player 2 email is required for tournament registrations")

        # Prepare additional metadata for tournament registrations
        metadata = {}
        if event_type == "tournament" and data.get("item_id"):
            metadata = {
                "tournament_id": data.get("item_id"),
                "player1_id": player_id,
                "player2_email": data.get("player2_email"),  # This should be passed from frontend
                "tournament_name": data.get("tournament_name")
            }
        
        # Crear payment_order
        payment_order_data = {
            "user_id": player_id,
            "total_amount": total_price,
            "payment_status": "pending",
            "event_type": event_type,
            "is_full_payment": is_full_payment,
            "recipient_id": recipient_id,
        }
        
        # Add metadata if available
        if metadata:
            payment_order_data["metadata"] = json.dumps(metadata)
        
        print(f"Inserting payment_order_data: {payment_order_data}")
        
        # Check if Supabase client is available
        if supabase is None:
            print("Supabase client is not available - check database configuration")
            raise HTTPException(
                status_code=503, 
                detail="Database service unavailable. Please check Supabase configuration (SUPABASE_URL and SUPABASE_KEY environment variables)."
            )
        
        # Add try-catch for database operations specifically
        try:
            payment_order_response = supabase.from_("payment_orders").insert(payment_order_data).execute()
        except Exception as db_error:
            print(f"Database error during payment order insertion: {str(db_error)}")
            print(f"Database error type: {type(db_error)}")
            # Check if it's a Supabase connection issue
            if "supabase" in str(db_error).lower() or "connection" in str(db_error).lower():
                raise HTTPException(status_code=503, detail="Database connection error. Please check Supabase configuration.")
            else:
                raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        print(f"Supabase response: {payment_order_response}")

        if not payment_order_response or not payment_order_response.data:
            print(f"Failed to create payment order. Response: {payment_order_response}")
            raise HTTPException(status_code=500, detail="Error al crear la orden de pago.")

        payment_order_id = payment_order_response.data[0]["id"]
        print(f"Created payment order with ID: {payment_order_id}")

        # Crear split_payments si es necesario
        if not is_full_payment:
            amount = total_price / num_players
            print(f"Creating split payment: amount={amount}, player_id={player_id}")

            split_payment_data = {
                "payment_order_id": payment_order_id,
                "user_id": player_id,
                "amount": amount,
                "payment_status": "pending",
                "is_paid": False
            }
            print(f"Inserting split_payment_data: {split_payment_data}")
            
            try:
                split_payment_response = supabase.from_("split_payments").insert(split_payment_data).execute()
            except Exception as db_error:
                print(f"Database error during split payment insertion: {str(db_error)}")
                print(f"Database error type: {type(db_error)}")
                if "supabase" in str(db_error).lower() or "connection" in str(db_error).lower():
                    raise HTTPException(status_code=503, detail="Database connection error during split payment creation.")
                else:
                    raise HTTPException(status_code=500, detail=f"Database error during split payment: {str(db_error)}")
            
            print(f"Split payment response: {split_payment_response}")

            if not split_payment_response or not split_payment_response.data:
                print(f"Failed to create split payment. Response: {split_payment_response}")
                raise HTTPException(status_code=500, detail="Error al crear el pago dividido.")

        return {
            "message": "Orden de pago y pagos divididos creados exitosamente.",
            "payment_order_id": payment_order_id,
        }

    except HTTPException as http_exc:
        # Re-raise HTTP exceptions with their original status codes
        raise http_exc
    except Exception as e:
        print(f"Unexpected error in create_payment_order_and_split_payment: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    

@router.post("/process-stripe-payment")
def process_stripe_payment(data: dict):
    payment_order_id = data["payment_order_id"]
    payment_method = data["payment_method"]
    payment_status = data["payment_status"]
    transaction_id = data["transaction_id"]
    is_full_payment = data.get("is_full_payment") # Opcional

    try:
        # Actualizar payment_orders
        result_po = supabase.from_("payment_orders").update({
            "payment_method": payment_method,
            "payment_status": payment_status,
            "transaction_id": transaction_id,
            "is_full_payment": is_full_payment
        }).eq("id", payment_order_id).execute()

        # Actualizar split_payments
        result_sp = supabase.from_("split_payments").update({
            "payment_status": payment_status,
            "transaction_id": transaction_id
        }).eq("payment_order_id", payment_order_id).execute()

        if result_po.count == 0:
            raise HTTPException(status_code=404, detail="Payment order not found")
        if result_sp.count == 0:
            raise HTTPException(status_code=404, detail="Split payments not found")

        response = {"success": True, "message": "Pago procesado y registros actualizados exitosamente."}
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el pago: {str(e)}")


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
                "customer": pm.customer,
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