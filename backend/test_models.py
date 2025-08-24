#!/usr/bin/env python3
"""
Simple validation test for MercadoPago models without database dependencies.
"""

from pydantic import BaseModel, ValidationError
from typing import Optional, List
import json

# Replicate the models from payments.py
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

def test_models():
    print("🧪 Testing MercadoPago models...")
    
    # Valid data
    valid_data = {
        "cart_items": [
            {
                "id": "item_1",
                "title": "Reserva de Cancha",
                "quantity": 1,
                "unit_price": 5000.00
            }
        ],
        "user_info": {
            "email": "test@example.com",
            "name": "Juan Pérez"
        },
        "external_reference": "test_123"
    }
    
    try:
        request = CreatePreferenceRequest(**valid_data)
        print("✅ Models validation passed")
        print(f"✅ JSON output: {json.dumps(request.model_dump(), indent=2)}")
        return True
    except ValidationError as e:
        print(f"❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    success = test_models()
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}")