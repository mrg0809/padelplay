# MercadoPago Checkout API Integration

This document describes the new in-app MercadoPago Checkout API integration that provides custom UI and payment tokenization capabilities, replacing the previous redirect-based checkout.

## Features

- ✅ **In-App Payments**: Users stay within the application during the entire payment flow
- ✅ **Custom Payment UI**: Fully customizable payment forms and user interface  
- ✅ **Payment Tokenization**: Secure card tokenization for enhanced security
- ✅ **Saved Payment Methods**: Users can save and reuse payment methods
- ✅ **Multiple Installments**: Support for installment payments
- ✅ **Real-time Validation**: Client-side and server-side payment validation

## Backend API Endpoints

### New Checkout API Endpoints

#### 1. Get Payment Methods
**GET** `/payments/payment_methods`

Returns available MercadoPago payment methods (credit/debit cards).

```json
{
  "payment_methods": [
    {
      "id": "visa",
      "name": "Visa",
      "payment_type_id": "credit_card",
      "thumbnail": "https://...",
      "secure_thumbnail": "https://..."
    }
  ]
}
```

#### 2. Tokenize Card
**POST** `/payments/tokenize_card`

Securely tokenizes card information for payment processing.

```json
{
  "card_number": "4507990000004905",
  "expiration_month": "12", 
  "expiration_year": "2025",
  "security_code": "123",
  "card_holder_name": "JUAN PEREZ"
}
```

Response:
```json
{
  "token": "abc123...",
  "first_six_digits": "450799",
  "last_four_digits": "4905",
  "expiration_month": 12,
  "expiration_year": 2025,
  "card_holder_name": "JUAN PEREZ"
}
```

#### 3. Process Payment  
**POST** `/payments/process_payment`

Processes direct payment using tokenized card information.

```json
{
  "transaction_amount": 5000.00,
  "description": "Reserva de Cancha",
  "payment_method_id": "visa",
  "payer": {
    "email": "user@example.com",
    "first_name": "Juan",
    "last_name": "Pérez"  
  },
  "payment_method": {
    "token": "abc123...",
    "installments": 1,
    "issuer_id": "123"
  },
  "external_reference": "order_123",
  "metadata": {
    "reservation_id": "456"
  }
}
```

Response:
```json
{
  "payment_id": "12345678",
  "status": "approved",
  "status_detail": "accredited", 
  "transaction_amount": 5000.00,
  "currency_id": "ARS",
  "payment_method_id": "visa",
  "installments": 1
}
```

### Saved Payment Methods

#### 4. Save Payment Method
**POST** `/payments/save_payment_method`

Saves payment method metadata to user profile (no sensitive data stored).

```json
{
  "payment_method_id": "visa",
  "last_four_digits": "4905",
  "card_holder_name": "JUAN PEREZ",
  "expiration_month": "12",
  "expiration_year": "2025",
  "issuer_name": "Banco Santander"
}
```

#### 5. Get Saved Payment Methods
**GET** `/payments/saved_payment_methods`

Returns user's saved payment methods.

```json
{
  "saved_payment_methods": [
    {
      "id": "uuid-123",
      "payment_method_id": "visa", 
      "last_four_digits": "4905",
      "card_holder_name": "JUAN PEREZ",
      "expiration_month": "12",
      "expiration_year": "2025",
      "issuer_name": "Banco Santander",
      "created_at": "2023-12-01T10:30:00Z"
    }
  ]
}
```

#### 6. Delete Saved Payment Method
**DELETE** `/payments/saved_payment_methods/{payment_method_id}`

Removes a saved payment method from user's profile.

### Legacy Endpoint (Deprecated)

#### Create Preference (DEPRECATED)
**POST** `/payments/create_preference` 

Still available for backwards compatibility but marked as deprecated. Use `/payments/process_payment` for new implementations.

## Database Schema

### New Table: saved_payment_methods

```sql
CREATE TABLE saved_payment_methods (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    payment_method_id VARCHAR(50) NOT NULL,
    last_four_digits VARCHAR(4) NOT NULL,
    card_holder_name VARCHAR(255) NOT NULL,
    expiration_month VARCHAR(2) NOT NULL,
    expiration_year VARCHAR(4) NOT NULL,
    issuer_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT unique_user_card UNIQUE (user_id, last_four_digits, expiration_month, expiration_year)
);
```

## Frontend Integration

### CheckoutAPI Component

The new `CheckoutAPI.vue` component provides:

- Card form with real-time validation
- Payment method selection
- Saved payment methods management  
- Installment options
- Secure tokenization flow

```vue
<template>
  <CheckoutAPI 
    :cart-items="cartItems"
    :user-info="userInfo"
    :total-amount="totalAmount"
    :external-reference="orderId"
    :metadata="{ reservation_id: '123' }"
    @payment-success="handlePaymentSuccess"
    @payment-error="handlePaymentError"
  />
</template>
```

### Updated MercadoPayment Page

The `MercadoPayment.vue` page now uses the new in-app checkout:

- No more redirects to external MercadoPago pages
- Custom payment UI with order summary  
- Success/error dialogs with proper navigation
- Real-time payment status updates

## Payment Flow

### New In-App Flow

1. **Load Payment Form**: User sees custom payment form within the app
2. **Payment Method Selection**: Choose from available card types (Visa, Mastercard, etc.)
3. **Card Information Entry**: Enter card details with real-time validation
4. **Saved Methods**: Option to use previously saved payment methods
5. **Tokenization**: Card details are securely tokenized via MercadoPago
6. **Payment Processing**: Direct payment using token (no page redirects)
7. **Instant Feedback**: User receives immediate payment confirmation
8. **Save Method**: Optional saving of payment method for future use

### Security Features

- **No Card Storage**: Only metadata stored, never full card numbers
- **Token Expiration**: Payment tokens expire for security
- **CVV Re-entry**: Saved methods require CVV re-entry for payments
- **Encryption**: All sensitive data encrypted during transmission
- **PCI Compliance**: MercadoPago handles PCI compliance requirements

## Environment Configuration

```bash
# Required MercadoPago configuration
MERCADOPAGO_ACCESS_TOKEN=your_mercadopago_access_token
MERCADOPAGO_CURRENCY=ARS  # Optional: ARS, BRL, MXN, CLP, COP, PEN, UYU

# URLs for webhooks and notifications  
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

## Migration Notes

### From Redirect-Based to In-App

**Breaking Changes:**
- `create_preference` endpoint deprecated (still works but not recommended)
- New endpoints require authentication for all operations
- Frontend components completely rewritten for in-app experience
- Database schema includes new `saved_payment_methods` table

**Migration Steps:**
1. Deploy new database table: `saved_payment_methods`
2. Update frontend to use new `CheckoutAPI` component
3. Test payment flow thoroughly in sandbox environment
4. Gradually migrate users from redirect flow to in-app flow
5. Eventually remove deprecated endpoints

## Testing

### Sandbox Testing

Use MercadoPago test cards for integration testing:

```javascript
// Test cards for different scenarios
const testCards = {
  approved: {
    number: '4509953566233704',
    cvv: '123',
    expiry: '12/25'
  },
  pending: {
    number: '4774090000000008', 
    cvv: '123',
    expiry: '12/25'
  },
  rejected: {
    number: '4013540682746260',
    cvv: '123', 
    expiry: '12/25'
  }
};
```

### Integration Testing

The existing webhook system remains unchanged and continues to work with the new direct payment flow:

- Payment status updates via `/payments/mercadopago-webhook`
- Automatic `payment_orders` and `split_payments` table updates
- Real-time payment status synchronization

## Advantages over Redirect Flow

1. **Better UX**: Users never leave the application
2. **Faster Payments**: No page redirects or loading times
3. **Custom Branding**: Full control over payment UI/UX
4. **Saved Methods**: Enhanced user convenience
5. **Mobile Optimized**: Better mobile app integration
6. **Real-time Validation**: Instant feedback on form errors
7. **Analytics**: Better tracking of payment funnel
8. **Security**: Enhanced security with tokenization

This new implementation provides a significantly improved user experience while maintaining all the security and reliability of MercadoPago's payment processing.