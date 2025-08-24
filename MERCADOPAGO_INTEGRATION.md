# MercadoPago Checkout API Integration

This document describes how to use the new MercadoPago Checkout API integration that replaces the previous Bricks implementation.

## Backend API

### Create Preference Endpoint

**POST** `/payments/create_preference`

Creates a MercadoPago payment preference and returns the checkout URL.

#### Request Body:
```json
{
  "cart_items": [
    {
      "id": "item_1",
      "title": "Reserva de Cancha",
      "quantity": 1,
      "unit_price": 5000.00
    }
  ],
  "user_info": {
    "email": "user@example.com",
    "name": "Juan Pérez"
  },
  "external_reference": "reservation_123", // Optional
  "metadata": { // Optional
    "reservation_id": "123",
    "club_id": "456"
  }
}
```

#### Response:
```json
{
  "init_point": "https://www.mercadopago.com.ar/checkout/v1/redirect?pref_id=...",
  "preference_id": "123456789-abcd-1234-5678-123456789012"
}
```

## Frontend Integration

### Option 1: Using the MercadoPayment Component

Navigate users to the MercadoPayment page with payment data:

```javascript
import { initiateMercadoPagoPayment } from 'src/helpers/mercadoPagoUtils';

// Prepare payment data
const paymentData = {
  cartItems: [
    {
      id: 'reservation_1',
      title: 'Reserva de Cancha - Club ABC',
      quantity: 1,
      unit_price: 5000.00
    }
  ],
  userInfo: {
    email: 'user@example.com',
    name: 'Juan Pérez'
  },
  externalReference: 'reservation_123',
  metadata: {
    reservation_id: '123',
    club_id: '456'
  }
};

// Redirect to payment page
initiateMercadoPagoPayment(paymentData);
```

### Option 2: Direct API Integration

For more control, call the API directly:

```javascript
import { processMercadoPagoPayment } from 'src/helpers/mercadoPagoUtils';

const cartItems = [
  {
    id: 'item_1',
    name: 'Reserva de Cancha',
    quantity: 1,
    price: 5000.00
  }
];

const userInfo = {
  email: 'user@example.com',
  full_name: 'Juan Pérez'
};

try {
  // This will create preference and redirect to MercadoPago
  const preference = await processMercadoPagoPayment(
    cartItems,
    userInfo,
    'reservation_123',
    { reservation_id: '123' }
  );
} catch (error) {
  console.error('Payment failed:', error);
  // Handle error
}
```

### Option 3: Using the API Service Directly

```javascript
import api from 'src/services/api';

const createPayment = async () => {
  try {
    const response = await api.post('/payments/create_preference', {
      cart_items: [
        {
          id: 'item_1',
          title: 'Reserva de Cancha',
          quantity: 1,
          unit_price: 5000.00
        }
      ],
      user_info: {
        email: 'user@example.com',
        name: 'Juan Pérez'
      },
      external_reference: 'reservation_123'
    });

    // Redirect to MercadoPago
    if (response.data.init_point) {
      window.location.href = response.data.init_point;
    }
  } catch (error) {
    console.error('Error creating payment:', error);
  }
};
```

## Payment Flow

1. **User initiates payment** - Component collects cart items and user info
2. **Create preference** - Frontend calls `/payments/create_preference`
3. **Redirect to MercadoPago** - User is redirected to `init_point` URL
4. **User completes payment** - On MercadoPago's hosted checkout page
5. **Return to app** - User returns to success/failure/pending pages
6. **Webhook processing** - Backend receives payment notifications automatically

## Return URLs

After payment, users will be redirected to:
- Success: `/payment-success` 
- Failure: `/payment-failure`
- Pending: `/payment-pending`

## Environment Configuration

Make sure to set these environment variables in your backend:

```bash
MERCADOPAGO_ACCESS_TOKEN=your_mercadopago_access_token
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## Webhook Handling

The webhook endpoint `/payments/mercadopago-webhook` automatically:
- Receives payment notifications
- Updates payment_orders table
- Creates split_payments records
- Handles payment status changes

No additional configuration needed - webhooks are automatically configured when creating preferences.