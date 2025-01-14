from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from app.db.connection import supabase
from app.core.security import get_current_user
from app.utils.supabase_utils import handle_supabase_response

router = APIRouter()

class Discount(BaseModel):
    club_id: str
    type: str
    name: str
    discount_percentage: float = None
    fixed_price: float = None
    applicable_days: List[int] = None
    start_time: str = None
    end_time: str = None
    start_date: str = None
    end_date: str = None
    description: str = None


@router.get("/")
async def get_discounts(current_user: dict = Depends(get_current_user)):
    club_id = current_user.get("club_id")
    if not club_id:
        raise HTTPException(status_code=403, detail="User is not associated with a club")
    try:
        response = supabase.table("discounts").select("*").execute()
        return handle_supabase_response(response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/")
async def create_discount(discount: Discount, current_user: dict = Depends(get_current_user)):
    club_id = current_user.get("club_id")
    if not club_id:
        raise HTTPException(status_code=403, detail="User is not associated with a club")
    try:
        data = discount.dict()
        data["club_id"] = club_id
        response = supabase.table("discounts").insert(data).execute()

        data = handle_supabase_response(response)

        if not data:
            raise HTTPException(status_code=400, detail=str("No data"))

        return {"message": "Descuento creado exitosamente", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
