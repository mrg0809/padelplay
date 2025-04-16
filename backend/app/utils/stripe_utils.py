from app.db.connection import supabase
from fastapi import HTTPException
import stripe

async def get_or_create_stripe_customer(user_id: str, user_email: str | None) -> str:
    # Buscar si existe el stripe_customer_id
    response = supabase.table('profiles').select('stripe_customer_id').eq('id', user_id).maybe_single().execute()

    if response.data and response.data.get('stripe_customer_id'):
        return response.data['stripe_customer_id']

    # Si no existe, crearlo en Stripe
    try:
        customer = stripe.Customer.create(
            email=user_email,
            metadata={'app_user_id': user_id} # ¡Importante enlazar!
        )
        stripe_customer_id = customer.id

        # Guardar el nuevo ID
        update_response = supabase.table('profiles').update({'stripe_customer_id': stripe_customer_id}).eq('id', user_id).execute()

        if not update_response.data: 
             print(f"WARN: Could not update profile for user {user_id} with stripe_customer_id")

        return stripe_customer_id
    except stripe.error.StripeError as e:
        print(f"Stripe error creating customer: {e}")
        raise HTTPException(status_code=500, detail="Error al crear perfil de pago.")
    except Exception as e:
        print(f"Database or other error: {e}")
        raise HTTPException(status_code=500, detail="Error interno al configurar pagos.")


async def get_stripe_customer_id(user_id: str) -> str | None:
     response = supabase.table('profiles').select('stripe_customer_id').eq('id', user_id).maybe_single().execute()
     if response.data and response.data.get('stripe_customer_id'):
         return response.data['stripe_customer_id']
     return None