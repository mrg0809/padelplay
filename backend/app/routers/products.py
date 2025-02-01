from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from app.core.security import get_current_user
from app.db.connection import supabase
from app.utils.supabase_utils import handle_supabase_response

router = APIRouter()

class ProductCreate(BaseModel):
    name: str
    brand: Optional[str] = None
    category: str
    price: float
    modality: str = Field(..., pattern="^(sale|rental)$")

@router.post("/")
async def create_product(
    product: ProductCreate,
    current_user: dict = Depends(get_current_user)
):
    try:
        # Verificar que el usuario tenga un club_id
        if not current_user or not current_user.get("club_id"):
            raise HTTPException(status_code=400, detail="Usuario no tiene un club asociado.")

        # Insertar el producto en la tabla club_products
        response = supabase.table("club_products").insert({
            "club_id": current_user["club_id"],
            "name": product.name,
            "brand": product.brand,
            "category": product.category,
            "price": product.price,
            "modality": product.modality,
        }).execute()
        handle_supabase_response(response)

        return {
            "message": "Producto creado exitosamente.",
            "status": "success",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al crear el producto: {str(e)}")