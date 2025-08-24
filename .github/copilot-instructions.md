# PadelPlay - GitHub Copilot Instructions

## Project Overview

PadelPlay is a comprehensive padel court management application designed for both players and clubs. The application enables players to book courts, schedule classes, join tournaments, and view rankings, while clubs can manage their facilities, coaches, schedules, and revenue.

### Architecture

This is a full-stack application with:
- **Frontend**: Vue.js 3 + Quasar Framework (multiplatform with Capacitor)
- **Backend**: FastAPI (Python) REST API
- **Database**: Supabase (PostgreSQL)
- **Authentication**: JWT-based with role-based access (player/club/admin)
- **Payments**: Integrated with Stripe and MercadoPago
- **State Management**: Pinia stores

## Directory Structure

```
├── frontend/              # Vue.js + Quasar application
│   ├── src/
│   │   ├── pages/         # Page components (route-based)
│   │   ├── components/    # Reusable UI components
│   │   ├── helpers/       # Utility JavaScript functions
│   │   ├── composables/   # Vue composables for shared logic
│   │   ├── stores/        # Pinia stores for state management
│   │   └── services/      # API service layers
│   └── ...
├── backend/               # FastAPI Python application
│   └── app/
│       ├── routers/       # API endpoint modules
│       ├── core/          # Core functionality (auth, config)
│       ├── db/            # Database connection and utilities
│       ├── services/      # Business logic services
│       └── utils/         # Helper utilities
└── ...
```

## Key Technologies & Patterns

### Frontend (Vue.js + Quasar)

- **Vue 3 Composition API**: Use `<script setup>` syntax for components
- **Quasar Framework**: Use q-* components for consistent UI
- **Routing**: Vue Router with route-based page components in `src/pages/`
- **State Management**: Pinia stores in `src/stores/`
- **API Communication**: Axios-based API service in `src/services/api.js`

**Component Structure Pattern:**
```vue
<template>
  <!-- Quasar components preferred -->
  <q-page padding>
    <q-card>
      <!-- Component content -->
    </q-card>
  </q-page>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useQuasar } from 'quasar'
// Import composables and stores as needed

// Component logic using Composition API
</script>

<style scoped>
/* Component-specific styles */
</style>
```

### Backend (FastAPI)

- **Python**: Follow PEP 8 conventions, use `black` for formatting
- **FastAPI**: RESTful API with automatic OpenAPI documentation
- **Router Pattern**: Modular endpoints in `app/routers/`
- **Authentication**: JWT tokens with role-based permissions
- **Database**: Supabase client for PostgreSQL operations

**API Endpoint Pattern:**
```python
from fastapi import APIRouter, HTTPException, Depends
from app.core.security import get_current_user
from app.db.connection import supabase

router = APIRouter()

@router.get("/endpoint")
async def get_data(current_user: dict = Depends(get_current_user)):
    # Endpoint implementation
    pass
```

## Development Guidelines

### Code Style

**Python (Backend):**
- Follow PEP 8 standards
- Use type hints for function parameters and return types
- Use `black` for automatic code formatting
- Prefer async/await for database operations

**JavaScript/Vue (Frontend):**
- Use ESLint configuration (`.eslintrc.cjs`)
- Prefer Composition API over Options API
- Use camelCase for JavaScript variables, kebab-case for HTML attributes
- Use Prettier for code formatting

### Authentication Patterns

**JWT Authentication:**
- Include JWT token in Authorization header: `Bearer <token>`
- Backend validates tokens using `get_current_user` dependency
- User roles: `player`, `club`, `admin`

**Frontend Auth Flow:**
```javascript
// Login and store token
const { data } = await api.post('/auth/login', credentials)
localStorage.setItem('token', data.access_token)

// Use token in API calls
api.defaults.headers.common['Authorization'] = `Bearer ${token}`
```

### Payment Integration

**Supported Providers:**
- **Stripe**: Primary payment processor with saved payment methods
- **MercadoPago**: Alternative payment processor for Latin America

**Payment Flow Pattern:**
1. Create payment intent via `/payments/create-payment-intent`
2. Process payment through provider-specific endpoints
3. Update payment status via webhooks or client confirmation
4. Finalize booking/reservation based on payment success

### Database Patterns

**Supabase Integration:**
- Use Supabase client for all database operations
- Prefer `.select()`, `.insert()`, `.update()`, `.delete()` methods
- Handle errors appropriately with try/catch blocks
- Use `.eq()`, `.filter()` for query conditions

**Common Tables:**
- `users` - User accounts and profiles
- `clubs` - Club information and settings
- `courts` - Court details and pricing
- `reservations` - Court bookings
- `matches` - Game records and results
- `tournaments` - Tournament management
- `payment_orders` - Payment tracking

### State Management (Pinia)

**Store Structure:**
```javascript
import { defineStore } from 'pinia'

export const useExampleStore = defineStore('example', {
  state: () => ({
    // State properties
  }),
  
  getters: {
    // Computed properties
  },
  
  actions: {
    // Methods to modify state
  }
})
```

### Common Workflows

**Creating New API Endpoints:**
1. Add route function in appropriate `app/routers/*.py` file
2. Include necessary imports and dependencies
3. Add authentication if required with `Depends(get_current_user)`
4. Implement database operations using Supabase client
5. Return appropriate HTTP responses

**Adding New Frontend Pages:**
1. Create Vue component in `src/pages/`
2. Add route to router configuration
3. Implement using Quasar components and Composition API
4. Add any required stores or composables
5. Connect to backend API endpoints

**Payment Integration:**
1. Create payment intent with required metadata
2. Handle payment processing based on provider (Stripe/MercadoPago)
3. Update payment status in database
4. Complete business logic (reservation, booking, etc.)

## Important Files

### Frontend
- `src/services/api.js` - API client configuration
- `src/stores/` - Pinia state management stores
- `src/helpers/` - Utility functions and helpers
- `src/pages/` - Route-based page components
- `src/composables/` - Reusable Vue composables

### Backend
- `app/main.py` - FastAPI application entry point
- `app/routers/` - API endpoint modules
- `app/core/security.py` - Authentication and JWT handling
- `app/core/config.py` - Application configuration
- `app/db/connection.py` - Database connection setup

## Environment Setup

**Frontend Development:**
```bash
cd frontend
npm install
quasar dev  # Development server
```

**Backend Development:**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload  # Development server
```

**Environment Variables:**
- Backend requires `.env` file with Supabase credentials, JWT secrets, and payment provider keys
- Frontend connects to backend API (typically localhost:8000 in development)

## Testing & Quality

**Frontend:**
- ESLint for code quality: `npm run lint`
- No test framework currently configured

**Backend:**
- Follow FastAPI testing patterns
- Test directory: `app/tests/`
- Use FastAPI TestClient for endpoint testing

Remember to maintain consistent code style, follow authentication patterns, and integrate properly with the payment systems when working on this codebase.