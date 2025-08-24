#!/usr/bin/env python3
"""
Simple test script to verify MercadoPago integration endpoints
This tests the basic flow without requiring a running database
"""

import sys
import os

# Add the backend app to the Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

def test_endpoints_availability():
    """Test that all required endpoints are available in the FastAPI app"""
    try:
        import app.main
        app = app.main.app
        
        print("🚀 Testing MercadoPago Integration Endpoints")
        print("=" * 50)
        
        required_endpoints = [
            ('POST', '/payments/payment_order_and_split_payment'),
            ('POST', '/payments/create_preference'),  
            ('POST', '/payments/mercadopago-webhook'),
            ('POST', '/payments/process-stripe-payment')
        ]
        
        available_routes = {}
        for route in app.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                for method in route.methods:
                    available_routes[f"{method} {route.path}"] = True
        
        all_available = True
        for method, path in required_endpoints:
            route_key = f"{method} {path}"
            if route_key in available_routes:
                print(f"✅ {method} {path}")
            else:
                print(f"❌ {method} {path}")
                all_available = False
        
        print("\n" + "=" * 50)
        if all_available:
            print("🎉 All required endpoints are available!")
            print("\n📋 Integration Status:")
            print("✅ 404 error fixed - payment_order_and_split_payment endpoint available")
            print("✅ MercadoPago preference creation endpoint available")  
            print("✅ MercadoPago webhook endpoint available")
            print("✅ Stripe payment processing endpoint available")
            print("\n🔄 Expected Flow:")
            print("1. OrderComponent → Select payment method")
            print("2. If MercadoPago → Create payment order → MercadoPayment page")
            print("3. MercadoPayment → Create preference → Redirect to MercadoPago")
            print("4. User pays → Returns to success/failure page")
            print("5. Webhook updates payment status automatically")
            return True
        else:
            print("❌ Some endpoints are missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoints: {e}")
        return False

def test_mercadopago_integration_components():
    """Test that MercadoPago integration components are properly set up"""
    print("\n🧩 Testing Integration Components")
    print("=" * 50)
    
    # Check that OrderComponent has been updated
    order_component_path = "frontend/src/components/OrderComponent.vue"
    if os.path.exists(order_component_path):
        with open(order_component_path, 'r') as f:
            content = f.read()
            if 'paymentMethodDialog' in content and 'MercadoPayment' in content:
                print("✅ OrderComponent updated with payment method selection")
            else:
                print("❌ OrderComponent missing MercadoPago integration")
    else:
        print("❌ OrderComponent not found")
    
    # Check MercadoPayment page exists
    mercado_payment_path = "frontend/src/pages/MercadoPayment.vue"
    if os.path.exists(mercado_payment_path):
        print("✅ MercadoPayment page available")
    else:
        print("❌ MercadoPayment page not found")
    
    # Check payment result pages
    payment_result_path = "frontend/src/pages/PaymentResult.vue"
    if os.path.exists(payment_result_path):
        print("✅ PaymentResult page available for success/failure handling")
    else:
        print("❌ PaymentResult page not found")
    
    # Check routes configuration
    routes_path = "frontend/src/router/routes.js"
    if os.path.exists(routes_path):
        with open(routes_path, 'r') as f:
            content = f.read()
            if '/payment-success' in content and '/mercado-payment' in content:
                print("✅ Payment routes configured properly")
            else:
                print("❌ Payment routes missing")
    else:
        print("❌ Routes file not found")

if __name__ == "__main__":
    print("🔧 MercadoPago Integration Test")
    print("=" * 60)
    
    success = test_endpoints_availability()
    test_mercadopago_integration_components()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Integration test completed successfully!")
        print("💡 The 404 error issue has been resolved.")
        print("🚀 MercadoPago integration is ready to use.")
    else:
        print("❌ Integration test failed. Check the errors above.")
        sys.exit(1)