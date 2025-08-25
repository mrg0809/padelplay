from fastapi import APIRouter, HTTPException, Depends, Body, Path, Response, status
from pydantic import BaseModel
from typing import Optional, List
from app.db.connection import supabase
from app.core.config import settings
from app.core.security import get_current_user

import mercadopago
import json
import requests

router = APIRouter()

sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

class User(BaseModel):
    id: str
    email: str

class MercadoPagoPaymentNotification(BaseModel):
    id: str
    live_mode: Optional[bool] = None
    type: Optional[str] = None
    date_created: Optional[str] = None
    user_id: Optional[str] = None
    version: Optional[str] = None
    api_version: Optional[str] = None
    action: Optional[str] = None
    data: Optional[dict] = None

class SplitConfig(BaseModel):
    seller_id: str
    amount: float
    fee_bearer: str = "marketplace" # O "primary_account" según tu lógica

class PreferencePayer(BaseModel):
    email: str
    # Puedes agregar más información del pagador si lo deseas

class PreferenceItem(BaseModel):
    id: str
    title: str
    quantity: int
    unit_price: float

class PaymentIntentRequest(BaseModel):
    payment_order_id: str
    items: List[PreferenceItem]
    total_amount: float
    split_config: List[SplitConfig]
    payer: Optional[PreferencePayer] = None
    metadata: Optional[dict] = None

# New models for the simplified /api/create_preference endpoint
class CartItem(BaseModel):
    id: str
    title: str
    quantity: int
    unit_price: float

class UserInfo(BaseModel):
    email: str
    name: Optional[str] = None
    
class CreatePreferenceRequest(BaseModel):
    cart_items: List[CartItem]
    user_info: UserInfo
    external_reference: Optional[str] = None
    metadata: Optional[dict] = None

# New models for Checkout API integration
class PaymentMethodInfo(BaseModel):
    token: str
    issuer_id: Optional[str] = None
    installments: Optional[int] = 1

class PayerInfo(BaseModel):
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class CreatePaymentRequest(BaseModel):
    transaction_amount: float
    description: str
    payment_method_id: str
    payer: PayerInfo
    payment_method: PaymentMethodInfo
    external_reference: Optional[str] = None
    metadata: Optional[dict] = None

class SavedPaymentMethod(BaseModel):
    id: str
    payment_method_id: str
    last_four_digits: str
    card_holder_name: str
    expiration_month: str
    expiration_year: str
    issuer_name: Optional[str] = None

class TokenizeCardRequest(BaseModel):
    card_number: str
    expiration_month: str
    expiration_year: str
    security_code: str
    card_holder_name: str

@router.post("/create-payment-intent")
async def create_payment_intent(request_data: PaymentIntentRequest = Body(...), current_user: dict = Depends(get_current_user)):
    try:
        preference_data = {
            "items": [item.model_dump() for item in request_data.items],
            "total_amount": request_data.total_amount,
            "marketplace": True,
            "marketplace_fee": 0.00, # Puedes calcular tu comisión aquí o en split_config
            "split_config": [split.model_dump() for split in request_data.split_config],
            "external_reference": request_data.payment_order_id,
            "metadata": {"payment_order_id": request_data.payment_order_id, **(request_data.metadata or {})},
            "payer": request_data.payer.model_dump() if request_data.payer else {"email": current_user.get('email')},
            "notification_url": f"{settings.BACKEND_URL}/payments/mercadopago-webhook", # URL para recibir notificaciones
        }

        preference_response = sdk.preference().create(preference_data)
        if preference_response["status"] == 201:
            return {"init_point": preference_response["response"]["init_point"]}
        else:
            raise HTTPException(status_code=500, detail=f"Error al crear la preferencia de Mercado Pago: {preference_response}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el intento de pago: {str(e)}")


def detect_currency_from_token(access_token: str) -> str:
    """
    Detect the appropriate currency based on MercadoPago access token.
    MercadoPago tokens often contain country codes that indicate the currency.
    """
    if not access_token:
        return "ARS"  # Default fallback
    
    # Common currency mappings based on token patterns and countries
    currency_mapping = {
        "AR": "ARS",  # Argentina
        "BR": "BRL",  # Brazil  
        "CL": "CLP",  # Chile
        "CO": "COP",  # Colombia
        "MX": "MXN",  # Mexico
        "PE": "PEN",  # Peru
        "UY": "UYU",  # Uruguay
    }
    
    # Check if token contains country indicators
    token_upper = access_token.upper()
    for country_code, currency in currency_mapping.items():
        if country_code in token_upper:
            return currency
    
    # Default to ARS if no specific country detected
    return "ARS"


async def handle_payment_approval(payment_order_id: str):
    """
    Handle post-payment actions when a payment is approved.
    This function checks the payment order type and performs the appropriate action.
    """
    try:
        # Get the payment order details
        payment_order_response = supabase.from_("payment_orders").select("*").eq("id", payment_order_id).single().execute()
        
        if not payment_order_response.data:
            print(f"Payment order not found: {payment_order_id}")
            return
            
        payment_order = payment_order_response.data
        event_type = payment_order.get("event_type")
        user_id = payment_order.get("user_id")
        
        print(f"Handling payment approval for order {payment_order_id}, event_type: {event_type}")
        
        if event_type == "tournament":
            await handle_tournament_registration(payment_order_id, user_id)
        elif event_type == "reservation":
            # Handle reservation confirmation if needed
            print(f"Reservation payment approved for order {payment_order_id}")
        elif event_type == "lesson":
            # Handle lesson booking confirmation if needed 
            print(f"Lesson payment approved for order {payment_order_id}")
        else:
            print(f"Unknown event type: {event_type} for payment order {payment_order_id}")
            
    except Exception as e:
        print(f"Error handling payment approval for order {payment_order_id}: {str(e)}")


async def handle_tournament_registration(payment_order_id: str, user_id: str):
    """
    Handle tournament team registration after successful payment.
    """
    try:
        # Get the payment order to extract tournament metadata
        payment_order_response = supabase.from_("payment_orders").select("*").eq("id", payment_order_id).single().execute()
        
        if not payment_order_response.data:
            print(f"Payment order not found: {payment_order_id}")
            return
            
        payment_order = payment_order_response.data
        metadata_str = payment_order.get("metadata")
        
        if not metadata_str:
            print(f"No metadata found for tournament payment order {payment_order_id}")
            return
            
        # Parse the metadata
        try:
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError:
            print(f"Invalid metadata JSON for payment order {payment_order_id}: {metadata_str}")
            return
            
        tournament_id = metadata.get("tournament_id")
        player1_id = metadata.get("player1_id") 
        player2_email = metadata.get("player2_email")
        
        if not tournament_id or not player1_id or not player2_email:
            print(f"Missing required tournament data in metadata for payment order {payment_order_id}")
            return
            
        # Find player2 by email
        player2_response = supabase.from_("players").select("user_id").eq("email", player2_email).single().execute()
        
        if not player2_response.data:
            print(f"Player with email {player2_email} not found for tournament registration")
            return
            
        player2_id = player2_response.data["user_id"]
        
        # Check if team is already registered (to avoid duplicates)
        existing_team = supabase.from_("tournament_teams").select("*").eq("tournament_id", tournament_id).eq("player1_id", player1_id).eq("player2_id", player2_id).execute()
        
        if existing_team.data:
            print(f"Team already registered for tournament {tournament_id}")
            return
            
        # Register the tournament team
        team_data = {
            "tournament_id": tournament_id,
            "player1_id": player1_id,
            "player2_id": player2_id,
            "payment_order_id": payment_order_id  # Link to payment
        }
        
        insert_result = supabase.from_("tournament_teams").insert(team_data).execute()
        
        if insert_result.data:
            print(f"Successfully registered tournament team for tournament {tournament_id}, payment {payment_order_id}")
            
            # Create notifications for both players
            from app.utils.notification_utils import create_notification
            
            create_notification(
                player1_id,
                "Inscripción a Torneo Confirmada",
                f"Tu pago fue procesado exitosamente. Ya estás inscrito en el torneo.",
                f"/tournament/{tournament_id}",
            )
            
            create_notification(
                player2_id,
                "Invitación a Torneo",
                f"Has sido invitado como pareja para un torneo. La inscripción fue pagada.",
                f"/tournament/{tournament_id}",
            )
        else:
            print(f"Failed to register tournament team for payment {payment_order_id}")
        
    except Exception as e:
        print(f"Error handling tournament registration for payment order {payment_order_id}: {str(e)}")


# New endpoints for Checkout API integration

@router.post("/tokenize_card")
async def tokenize_card(request_data: TokenizeCardRequest = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Tokenize a credit card using MercadoPago API for secure payments.
    Returns a card token that can be used for payments.
    """
    try:
        # Create card token using MercadoPago SDK
        card_token_data = {
            "card_number": request_data.card_number,
            "expiration_month": int(request_data.expiration_month),
            "expiration_year": int(request_data.expiration_year),
            "security_code": request_data.security_code,
            "card_holder": {
                "name": request_data.card_holder_name
            }
        }
        
        card_token_response = sdk.card_token().create(card_token_data)
        
        if card_token_response["status"] == 201:
            token_data = card_token_response["response"]
            return {
                "token": token_data["id"],
                "first_six_digits": token_data.get("first_six_digits"),
                "last_four_digits": token_data.get("last_four_digits"),
                "expiration_month": token_data.get("expiration_month"),
                "expiration_year": token_data.get("expiration_year"),
                "card_holder_name": token_data.get("cardholder", {}).get("name")
            }
        else:
            print(f"Error tokenizing card: {card_token_response}")
            raise HTTPException(status_code=400, detail=f"Error al tokenizar la tarjeta: {card_token_response.get('response', {}).get('message', 'Error desconocido')}")
            
    except Exception as e:
        print(f"Error tokenizing card: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al tokenizar la tarjeta: {str(e)}")

@router.post("/process_payment")
async def process_payment(request_data: CreatePaymentRequest = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Process a direct payment using MercadoPago Checkout API.
    Uses tokenized payment method for in-app payments.
    """
    try:
        # Detect appropriate currency
        currency_to_use = settings.MERCADOPAGO_CURRENCY or detect_currency_from_token(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        # Get user email from JWT token or database
        user_email = current_user.get("email")
        if not user_email:
            # Fallback: get email from players table  
            try:
                user_id = current_user.get("id") or current_user.get("sub")
                if user_id:
                    player_response = supabase.from_("players").select("email").eq("user_id", user_id).single().execute()
                    if player_response.data and player_response.data.get("email"):
                        user_email = player_response.data["email"]
            except Exception as e:
                print(f"Could not retrieve email from players table: {e}")
        
        # Final fallback to request payer email
        if not user_email:
            user_email = request_data.payer.email
        
        # Create payment using MercadoPago SDK
        payment_data = {
            "transaction_amount": float(request_data.transaction_amount),
            "token": request_data.payment_method.token,
            "description": request_data.description,
            "payment_method_id": request_data.payment_method_id,
            "payer": {
                "email": user_email
            },
            "external_reference": request_data.external_reference,
            "metadata": request_data.metadata or {}
        }
        
        # Only add notification_url for production (non-localhost URLs)
        backend_url = settings.BACKEND_URL or 'http://localhost:8000'
        if not backend_url.startswith('http://localhost') and not backend_url.startswith('http://127.0.0.1'):
            payment_data["notification_url"] = f"{backend_url}/payments/mercadopago-webhook"
        
        # Add installments if specified
        if request_data.payment_method.installments and request_data.payment_method.installments > 1:
            payment_data["installments"] = request_data.payment_method.installments
        
        # Add issuer if specified
        if request_data.payment_method.issuer_id:
            payment_data["issuer_id"] = request_data.payment_method.issuer_id
            
        print(f"Creating MercadoPago payment with data: {payment_data}")
        
        payment_response = sdk.payment().create(payment_data)
        
        if payment_response["status"] == 201:
            payment_info = payment_response["response"]
            return {
                "payment_id": payment_info["id"],
                "status": payment_info["status"],
                "status_detail": payment_info["status_detail"],
                "transaction_amount": payment_info["transaction_amount"],
                "currency_id": payment_info["currency_id"],
                "payment_method_id": payment_info["payment_method_id"],
                "issuer_id": payment_info.get("issuer_id"),
                "installments": payment_info.get("installments", 1)
            }
        else:
            print(f"Error processing payment: {payment_response}")
            error_message = payment_response.get('response', {}).get('message', 'Error desconocido')
            raise HTTPException(status_code=400, detail=f"Error al procesar el pago: {error_message}")
            
    except Exception as e:
        print(f"Error processing payment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al procesar el pago: {str(e)}")

@router.get("/payment_methods")
async def get_payment_methods():
    """
    Get available payment methods from MercadoPago.
    """
    try:
        import requests
        
        # Make direct API call to get payment methods
        url = "https://api.mercadopago.com/v1/payment_methods"
        headers = {
            "Authorization": f"Bearer {settings.MERCADOPAGO_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            payment_methods = response.json()
            
            # Filter only credit and debit cards
            card_methods = [
                {
                    "id": method["id"],
                    "name": method["name"],
                    "payment_type_id": method["payment_type_id"],
                    "thumbnail": method.get("thumbnail"),
                    "secure_thumbnail": method.get("secure_thumbnail")
                }
                for method in payment_methods
                if method["payment_type_id"] in ["credit_card", "debit_card"]
            ]
            
            return {"payment_methods": card_methods}
        else:
            print(f"MercadoPago API error: {response.status_code} - {response.text}")
            raise HTTPException(status_code=500, detail="Error al obtener métodos de pago")
            
    except Exception as e:
        print(f"Error getting payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener métodos de pago: {str(e)}")

@router.post("/create_preference")
async def create_preference(request_data: CreatePreferenceRequest = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Create a MercadoPago payment preference using cart items and user info.
    Returns init_point and preference_id for frontend redirection.
    DEPRECATED: Use /process_payment for in-app payments instead.
    """
    try:
        # Detect appropriate currency
        primary_currency = settings.MERCADOPAGO_CURRENCY
        detected_currency = detect_currency_from_token(settings.MERCADOPAGO_ACCESS_TOKEN)
        
        # Use configured currency, but fallback to detected if needed
        currency_to_use = primary_currency if primary_currency else detected_currency
        
        print(f"Using currency: {currency_to_use} (configured: {primary_currency}, detected: {detected_currency})")
        
        # Convert cart items to MercadoPago items format
        items = []
        for item in request_data.cart_items:
            items.append({
                "id": item.id,
                "title": item.title,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": currency_to_use
            })

        # Create preference data
        preference_data = {
            "items": items,
            "payer": {
                "email": request_data.user_info.email,
                "name": request_data.user_info.name or current_user.get('full_name', '')
            },
            "external_reference": request_data.external_reference,
            "metadata": request_data.metadata or {},
            "notification_url": f"{settings.BACKEND_URL}/payments/mercadopago-webhook"
        }

        # Only add back_urls and auto_return for production (public URLs)
        frontend_url = settings.FRONTEND_URL or 'http://localhost:3000'
        if not frontend_url.startswith('http://localhost') and not frontend_url.startswith('http://127.0.0.1'):
            # Production environment with public URLs
            preference_data["back_urls"] = {
                "success": f"{frontend_url}/payment-success",
                "failure": f"{frontend_url}/payment-failure", 
                "pending": f"{frontend_url}/payment-pending"
            }
            preference_data["auto_return"] = "approved"

        print(f"Creating MercadoPago preference with data: {preference_data}")
        
        # Create preference using MercadoPago SDK with currency fallback
        preference_response = None
        currencies_to_try = [currency_to_use, "ARS", "BRL", "MXN", "CLP", "COP", "PEN", "UYU"]
        
        # Remove duplicates while preserving order
        currencies_to_try = list(dict.fromkeys(currencies_to_try))
        
        for attempt_currency in currencies_to_try:
            try:
                # Update currency in items for this attempt
                preference_data_attempt = preference_data.copy()
                items_with_currency = []
                for item in preference_data_attempt["items"]:
                    item_copy = item.copy()
                    item_copy["currency_id"] = attempt_currency
                    items_with_currency.append(item_copy)
                preference_data_attempt["items"] = items_with_currency
                
                print(f"Attempting MercadoPago preference creation with currency: {attempt_currency}")
                preference_response = sdk.preference().create(preference_data_attempt)
                
                if preference_response["status"] == 201:
                    print(f"Successfully created preference with currency: {attempt_currency}")
                    break
                else:
                    print(f"Failed with currency {attempt_currency}: {preference_response}")
                    
            except Exception as currency_error:
                print(f"Currency {attempt_currency} failed: {str(currency_error)}")
                if attempt_currency == currencies_to_try[-1]:  # Last attempt
                    raise currency_error
                continue
        
        print(f"MercadoPago response: {preference_response}")
        
        if preference_response and preference_response["status"] == 201:
            preference = preference_response["response"]
            return {
                "init_point": preference["init_point"],
                "preference_id": preference["id"]
            }
        else:
            error_detail = preference_response if preference_response else "No response received"
            raise HTTPException(status_code=500, detail=f"Error al crear la preferencia de Mercado Pago: {error_detail}")

    except Exception as e:
        print(f"Error creating MercadoPago preference: {str(e)}")
        # Provide more detailed error information
        if "currency_id invalid" in str(e):
            raise HTTPException(
                status_code=500, 
                detail=f"Currency error: {str(e)}. Try configuring MERCADOPAGO_CURRENCY environment variable with a supported currency (ARS, BRL, MXN, CLP, COP, PEN, UYU)"
            )
        raise HTTPException(status_code=500, detail=f"Error al crear la preferencia: {str(e)}")



@router.post("/mercadopago-webhook")
async def mercadopago_webhook(notification: MercadoPagoPaymentNotification = Body(...)):
    try:
        print(f"Notificación de Mercado Pago recibida: {notification.model_dump()}")
        payment_id = notification.data.get("id") if notification.data else None

        if payment_id and notification.type == "payment":
            payment_info_response = sdk.payment().get(payment_id)
            if payment_info_response["status"] == 200:
                payment_data = payment_info_response["response"]
                status = payment_data.get("status")
                transaction_id = payment_data.get("id")
                payment_method = payment_data.get("payment_type") # Adaptar según la respuesta
                payment_order_id = payment_data.get("external_reference")
                amount = payment_data.get("transaction_amount")
                payer_id = payment_data.get("payer", {}).get("id")

                if payment_order_id:
                    # Actualizar payment_orders
                    payment_order_update = {
                        "payment_method": payment_method,
                        "payment_status": status,
                        "transaction_id": str(transaction_id),
                    }
                    update_po_result = supabase.from_("payment_orders").update(payment_order_update).eq("id", payment_order_id).execute()
                    print(f"Resultado de actualización de payment_orders: {update_po_result}")

                    # Registrar el pago en split_payments (asumiendo un solo pago inicial aquí)
                    split_payment_data = {
                        "payment_order_id": payment_order_id,
                        "user_id": payer_id,
                        "amount": amount,
                        "payment_status": status,
                        "transaction_id": str(transaction_id),
                        "is_paid": status == "approved"
                    }
                    insert_sp_result = supabase.from_("split_payments").insert([split_payment_data]).execute()
                    print(f"Resultado de inserción en split_payments: {insert_sp_result}")

                    # Handle post-payment actions when payment is approved
                    if status == "approved":
                        await handle_payment_approval(payment_order_id)

                    return {"message": "Webhook de Mercado Pago procesado exitosamente."}
                else:
                    print(f"No se encontró payment_order_id en la notificación para el pago {payment_id}")
                    raise HTTPException(status_code=400, detail="payment_order_id no encontrado en la notificación.")
            else:
                print(f"Error al obtener información del pago {payment_id} desde Mercado Pago: {payment_info_response}")
                raise HTTPException(status_code=500, detail="Error al obtener información del pago desde Mercado Pago.")
        elif notification.type == "refund":
            print(f"Notificación de reembolso recibida: {notification.model_dump()}")
            # Aquí podrías implementar la lógica para manejar reembolsos
            return {"message": "Notificación de reembolso de Mercado Pago recibida."}
        else:
            print(f"Notificación de Mercado Pago recibida sin tipo de pago claro: {notification.model_dump()}")
            return {"message": "Notificación de Mercado Pago recibida."}

    except Exception as e:
        print(f"Error al procesar webhook de Mercado Pago: {e}")
        raise HTTPException(status_code=500, detail=f"Error al procesar webhook de Mercado Pago: {str(e)}")


# Saved Payment Methods endpoints

@router.post("/save_payment_method")
async def save_payment_method(
    payment_method_id: str = Body(...),
    last_four_digits: str = Body(...),
    card_holder_name: str = Body(...),
    expiration_month: str = Body(...),
    expiration_year: str = Body(...),
    issuer_name: str = Body(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Save a payment method to user's profile for future use.
    This stores the payment method metadata (not sensitive card data).
    """
    try:
        user_id = current_user.get("sub") or current_user.get("id")
        
        # Check if payment method already exists for this user
        existing_check = supabase.from_("saved_payment_methods").select("*").eq("user_id", user_id).eq("last_four_digits", last_four_digits).execute()
        
        if existing_check.data:
            raise HTTPException(status_code=400, detail="Este método de pago ya está guardado")
        
        # Save payment method
        payment_method_data = {
            "user_id": user_id,
            "payment_method_id": payment_method_id,
            "last_four_digits": last_four_digits,
            "card_holder_name": card_holder_name,
            "expiration_month": expiration_month,
            "expiration_year": expiration_year,
            "issuer_name": issuer_name,
            "created_at": "now()",
            "is_active": True
        }
        
        result = supabase.from_("saved_payment_methods").insert([payment_method_data]).execute()
        
        if result.data:
            return {"message": "Método de pago guardado exitosamente", "id": result.data[0]["id"]}
        else:
            raise HTTPException(status_code=500, detail="Error al guardar el método de pago")
            
    except Exception as e:
        print(f"Error saving payment method: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al guardar método de pago: {str(e)}")

@router.get("/saved_payment_methods")
async def get_saved_payment_methods(current_user: dict = Depends(get_current_user)):
    """
    Get user's saved payment methods.
    """
    try:
        user_id = current_user.get("sub") or current_user.get("id")
        
        result = supabase.from_("saved_payment_methods").select("*").eq("user_id", user_id).eq("is_active", True).order("created_at", desc=True).execute()
        
        saved_methods = []
        for method in result.data:
            saved_methods.append({
                "id": method["id"],
                "payment_method_id": method["payment_method_id"],
                "last_four_digits": method["last_four_digits"],
                "card_holder_name": method["card_holder_name"],
                "expiration_month": method["expiration_month"],
                "expiration_year": method["expiration_year"],
                "issuer_name": method["issuer_name"],
                "created_at": method["created_at"]
            })
        
        return {"saved_payment_methods": saved_methods}
        
    except Exception as e:
        print(f"Error getting saved payment methods: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al obtener métodos de pago guardados: {str(e)}")

@router.delete("/saved_payment_methods/{payment_method_id}")
async def delete_saved_payment_method(payment_method_id: str, current_user: dict = Depends(get_current_user)):
    """
    Delete a saved payment method.
    """
    try:
        user_id = current_user.get("sub") or current_user.get("id")
        
        # Soft delete by setting is_active to False
        result = supabase.from_("saved_payment_methods").update({"is_active": False}).eq("id", payment_method_id).eq("user_id", user_id).execute()
        
        if result.data:
            return {"message": "Método de pago eliminado exitosamente"}
        else:
            raise HTTPException(status_code=404, detail="Método de pago no encontrado")
            
    except Exception as e:
        print(f"Error deleting saved payment method: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error al eliminar método de pago: {str(e)}")