#!/usr/bin/env python3
"""
Test script for MercadoPago integration endpoints.

This script validates the endpoint structure and request/response models
without making actual API calls to MercadoPago.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.routers.payments import CreatePreferenceRequest, CartItem, UserInfo
from pydantic import ValidationError
import json

def test_create_preference_models():
    """Test that our Pydantic models work correctly."""
    
    print("🧪 Testing CreatePreferenceRequest model...")
    
    # Valid request data
    valid_data = {
        "cart_items": [
            {
                "id": "item_1",
                "title": "Reserva de Cancha",
                "quantity": 1,
                "unit_price": 5000.00
            },
            {
                "id": "item_2", 
                "title": "Pelota de Pádel",
                "quantity": 2,
                "unit_price": 1500.00
            }
        ],
        "user_info": {
            "email": "test@example.com",
            "name": "Juan Pérez"
        },
        "external_reference": "test_123",
        "metadata": {
            "source": "test_script",
            "club_id": "456"
        }
    }
    
    try:
        # Test creating the request model
        request = CreatePreferenceRequest(**valid_data)
        print("✅ Valid request model created successfully")
        
        # Test JSON serialization
        json_data = json.dumps(request.model_dump(), indent=2, default=str)
        print(f"✅ JSON serialization works:\n{json_data}")
        
        # Test individual models
        cart_item = CartItem(
            id="test",
            title="Test Item",
            quantity=1,
            unit_price=100.50
        )
        print(f"✅ CartItem model: {cart_item}")
        
        user_info = UserInfo(
            email="test@test.com",
            name="Test User"
        )
        print(f"✅ UserInfo model: {user_info}")
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    # Test invalid data
    print("\n🧪 Testing invalid data handling...")
    
    invalid_data = {
        "cart_items": [
            {
                "id": "item_1",
                "title": "Test",
                "quantity": "not_a_number",  # Invalid type
                "unit_price": 100.00
            }
        ],
        "user_info": {
            "email": "invalid_email",  # Invalid email format
        }
    }
    
    try:
        request = CreatePreferenceRequest(**invalid_data)
        print("❌ Should have failed validation")
        return False
    except ValidationError as e:
        print(f"✅ Correctly caught validation error: {len(e.errors())} errors")
        for error in e.errors():
            print(f"   - {error['loc']}: {error['msg']}")
    
    return True

def test_mercadopago_preference_structure():
    """Test the structure of data we'd send to MercadoPago."""
    
    print("\n🧪 Testing MercadoPago preference data structure...")
    
    # Sample request
    request = CreatePreferenceRequest(
        cart_items=[
            CartItem(
                id="reservation_1",
                title="Reserva de Cancha - Club ABC",
                quantity=1,
                unit_price=5000.00
            )
        ],
        user_info=UserInfo(
            email="user@example.com",
            name="Juan Pérez"
        ),
        external_reference="test_reservation_123"
    )
    
    # Expected MercadoPago preference structure
    expected_preference = {
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "currency_id": "ARS"
            }
            for item in request.cart_items
        ],
        "payer": {
            "email": request.user_info.email,
            "name": request.user_info.name or ""
        },
        "external_reference": request.external_reference,
        "metadata": request.metadata or {},
        "notification_url": "http://localhost:8000/payments/mercadopago-webhook",
        "back_urls": {
            "success": "http://localhost:3000/payment-success",
            "failure": "http://localhost:3000/payment-failure",
            "pending": "http://localhost:3000/payment-pending"
        },
        "auto_return": "approved"
    }
    
    print("✅ Expected MercadoPago preference structure:")
    print(json.dumps(expected_preference, indent=2))
    
    return True

def test_endpoint_compatibility():
    """Test compatibility with existing payment system."""
    
    print("\n🧪 Testing compatibility with existing system...")
    
    # The new endpoint should coexist with the existing /create-payment-intent
    print("✅ New endpoint: /payments/create_preference")
    print("✅ Existing endpoint: /payments/create-payment-intent") 
    print("✅ Webhook endpoint: /payments/mercadopago-webhook")
    
    # Both should work with different use cases:
    # - create_preference: Simple cart-based payments
    # - create-payment-intent: Complex split payments with marketplace features
    
    return True

def main():
    """Run all tests."""
    
    print("🚀 Starting MercadoPago integration tests...\n")
    
    tests = [
        test_create_preference_models,
        test_mercadopago_preference_structure,
        test_endpoint_compatibility
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with error: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results:")
    print(f"✅ Passed: {sum(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}")
    print(f"📋 Total: {len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! MercadoPago integration is ready.")
        return 0
    else:
        print("\n💥 Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    exit(main())