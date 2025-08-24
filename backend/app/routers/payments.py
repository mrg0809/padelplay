from fastapi import APIRouter, HTTPException, Depends, Body, Path, Response, status
from pydantic import BaseModel
from typing import Optional, List
from app.db.connection import supabase
from app.core.config import settings
from app.core.security import get_current_user

import mercadopago
import json

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

@router.post("/create_preference")
async def create_preference(request_data: CreatePreferenceRequest = Body(...), current_user: dict = Depends(get_current_user)):
    """
    Create a MercadoPago payment preference using cart items and user info.
    Returns init_point and preference_id for frontend redirection.
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