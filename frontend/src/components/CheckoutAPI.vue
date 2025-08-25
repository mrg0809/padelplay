<template>
  <q-card class="text-white">
    <q-card-section>
      <h3 class="text-white">Pagar con MercadoPago</h3>
      <p class="text-caption">Ingresa los datos de tu tarjeta de manera segura</p>
    </q-card-section>

    <q-card-section v-if="loading">
      <div class="text-center">
        <q-spinner color="primary" size="3rem" />
        <p class="q-mt-md">Cargando métodos de pago...</p>
      </div>
    </q-card-section>

    <!-- Saved Payment Methods -->
    <q-card-section v-if="!loading && savedMethods.length > 0">
      <h5 class="q-mb-md">Métodos de pago guardados</h5>
      <div class="row q-col-gutter-sm">
        <div v-for="method in savedMethods" :key="method.id" class="col-12">
          <q-card 
            flat 
            bordered 
            :class="selectedSavedMethod?.id === method.id ? 'bg-primary text-white' : 'bg-grey-8 text-white'"
            clickable
            @click="selectSavedMethod(method)"
          >
            <q-card-section class="row items-center">
              <q-icon 
                :name="getCardIcon(method.payment_method_id)" 
                size="sm" 
                class="q-mr-sm"
              />
              <div class="col">
                <div class="text-body2">**** **** **** {{ method.last_four_digits }}</div>
                <div class="text-caption">{{ method.card_holder_name }}</div>
                <div class="text-caption">{{ method.expiration_month }}/{{ method.expiration_year }}</div>
              </div>
              <q-btn
                flat
                icon="delete"
                size="sm"
                @click.stop="deleteSavedMethod(method)"
                :loading="deletingMethod === method.id"
              />
            </q-card-section>
          </q-card>
        </div>
      </div>
      
      <q-separator class="q-my-md" />
      
      <q-btn
        flat
        :label="showNewCard ? 'Usar método guardado' : 'Usar nueva tarjeta'"
        @click="showNewCard = !showNewCard"
        class="full-width q-mb-md"
      />
    </q-card-section>

    <!-- Loading state for payment methods -->
    <q-card-section v-if="!loading && loadingPaymentMethods">
      <div class="text-center">
        <q-spinner color="primary" size="2rem" />
        <p class="q-mt-md text-white">Cargando métodos de pago...</p>
      </div>
    </q-card-section>

    <!-- No payment methods available -->
    <q-card-section v-if="!loading && !loadingPaymentMethods && cardPaymentMethods.length === 0 && (savedMethods.length === 0 || showNewCard)">
      <div class="text-center text-white">
        <q-icon name="error" size="3rem" color="negative" />
        <p class="q-mt-md">No se pudieron cargar los métodos de pago disponibles.</p>
        <q-btn 
          color="primary" 
          label="Reintentar" 
          @click="loadPaymentMethods" 
          class="q-mt-md" 
        />
      </div>
    </q-card-section>

    <!-- New Card Form -->
    <q-card-section v-if="!loading && !loadingPaymentMethods && cardPaymentMethods.length > 0 && (savedMethods.length === 0 || showNewCard)">
      <q-form @submit.prevent="processPayment">
        <!-- Card Type Display (Auto-detected) -->
        <div class="q-mb-md" v-if="detectedCardType">
          <div class="text-body2 q-mb-sm text-white">Tipo de tarjeta detectado</div>
          <div class="row items-center q-py-md">
            <img 
              :src="`/icons/${detectedCardType}.svg`" 
              :alt="getCardName(detectedCardType)"
              style="height: 32px; width: auto; filter: brightness(1.2);"
              class="q-mr-md"
            />
            <span class="text-white text-h6">{{ getCardName(detectedCardType) }}</span>
          </div>
        </div>

        <!-- Card Number -->
        <q-input
          v-model="cardForm.number"
          label="Número de tarjeta"
          placeholder="1234 5678 9012 3456"
          filled
          dark
          maxlength="19"
          :rules="[val => validateCardNumber(val) || 'Número de tarjeta inválido']"
          @input="formatCardNumber"
          class="q-mb-md"
        >
          <template v-slot:prepend v-if="detectedCardType">
            <img 
              :src="`/icons/${detectedCardType}.svg`" 
              :alt="getCardName(detectedCardType)"
              style="height: 24px; width: auto;"
            />
          </template>
          <template v-slot:prepend v-else>
            <q-icon name="credit_card" color="grey" />
          </template>
        </q-input>

        <!-- Card Holder Name -->
        <q-input
          v-model="cardForm.holderName"
          label="Nombre del titular"
          placeholder="JUAN PÉREZ"
          filled
          dark
          :rules="[val => !!val || 'El nombre es requerido']"
          class="q-mb-md"
        />

        <div class="row q-col-gutter-md">
          <!-- Expiry Date -->
          <div class="col-6">
            <q-input
              v-model="cardForm.expiry"
              label="MM/AA"
              placeholder="12/28"
              filled
              dark
              maxlength="5"
              :rules="[val => validateExpiry(val) || 'Fecha inválida (MM/AA)']"
              @input="formatExpiry"
              @keyup="formatExpiry"
            />
          </div>

          <!-- CVV -->
          <div class="col-6">
            <q-input
              v-model="cardForm.cvv"
              label="CVV"
              placeholder="123"
              filled
              dark
              maxlength="4"
              type="password"
              :rules="[val => validateCVV(val) || 'CVV inválido']"
            />
          </div>
        </div>

        <!-- Save Payment Method -->
        <q-checkbox
          v-model="savePaymentMethod"
          label="Guardar método de pago para futuras compras"
          color="primary"
          dark
          class="q-mb-md"
        />

        <!-- Payment Button -->
        <q-btn
          type="submit"
          :color="isFormValid ? 'positive' : 'primary'"
          size="lg"
          :label="`Pagar $${totalAmount}`"
          class="full-width"
          :loading="processing"
          :disable="!isFormValid"
        />
      </q-form>
    </q-card-section>

    <!-- Selected Saved Method Payment -->
    <q-card-section v-if="!loading && !loadingPaymentMethods && selectedSavedMethod && !showNewCard">
      <div class="text-center">
        <p class="q-mb-md">
          Pagar con: **** **** **** {{ selectedSavedMethod.last_four_digits }}
        </p>
        
        <q-btn
          color="positive"
          size="lg"
          :label="`Pagar $${totalAmount}`"
          class="full-width"
          :loading="processing"
          @click="processPaymentWithSavedMethod"
        />
      </div>
    </q-card-section>
  </q-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'

// Props
const props = defineProps({
  cartItems: {
    type: Array,
    required: true
  },
  userInfo: {
    type: Object,
    required: true
  },
  totalAmount: {
    type: Number,
    required: true
  },
  externalReference: {
    type: String,
    required: true
  },
  metadata: {
    type: Object,
    default: () => ({})
  }
})

// Emits
const emit = defineEmits(['payment-success', 'payment-error'])

// Composables
const $q = useQuasar()

// State
const loading = ref(true)
const processing = ref(false)
const loadingPaymentMethods = ref(false)
const deletingMethod = ref(null)
const showNewCard = ref(false)
const detectedCardType = ref('')

// Payment methods
const cardPaymentMethods = ref([])
const selectedPaymentMethod = ref(null)

// Saved methods
const savedMethods = ref([])
const selectedSavedMethod = ref(null)

// Card form
const cardForm = ref({
  number: '',
  holderName: '',
  expiry: '',
  cvv: ''
})

// Payment options
const selectedInstallments = ref(1)
const savePaymentMethod = ref(false)

// Computed
const installmentOptions = computed(() => [
  { label: '1 pago', value: 1 }
])

const isFormValid = computed(() => {
  if (selectedSavedMethod.value && !showNewCard.value) {
    return true
  }
  
  return (
    // Card type is valid if auto-detected
    (detectedCardType.value && 
     detectedCardType.value !== null && 
     detectedCardType.value !== '') &&
    validateCardNumber(cardForm.value.number) &&
    cardForm.value.holderName &&
    cardForm.value.holderName.trim() !== '' &&
    validateExpiry(cardForm.value.expiry) &&
    validateCVV(cardForm.value.cvv)
  )
})

// Methods
const getCardIcon = (paymentMethodId) => {
  const icons = {
    'visa': 'credit_card',
    'master': 'credit_card',
    'amex': 'credit_card',
    'naranja': 'credit_card',
    'cabal': 'credit_card',
    'default': 'credit_card'
  }
  return icons[paymentMethodId] || icons.default
}

const getCardName = (paymentMethodId) => {
  const names = {
    'visa': 'VISA',
    'master': 'Mastercard',
    'amex': 'American Express',
    'naranja': 'Naranja',
    'cabal': 'Cabal'
  }
  return names[paymentMethodId] || paymentMethodId?.toUpperCase()
}

const validateCardNumber = (value) => {
  if (!value) return false
  const cleanNumber = value.replace(/\s/g, '')
  return cleanNumber.length >= 13 && cleanNumber.length <= 19 && /^\d+$/.test(cleanNumber)
}

const validateExpiry = (value) => {
  if (!value || value.length !== 5) return false
  const [month, year] = value.split('/')
  const monthNum = parseInt(month)
  const yearNum = parseInt('20' + year)
  const now = new Date()
  const currentYear = now.getFullYear()
  const currentMonth = now.getMonth() + 1
  
  return (
    monthNum >= 1 && monthNum <= 12 &&
    yearNum >= currentYear &&
    (yearNum > currentYear || monthNum >= currentMonth)
  )
}

const validateCVV = (value) => {
  if (!value) return false
  return value.length >= 3 && value.length <= 4 && /^\d+$/.test(value)
}

const formatCardNumber = () => {
  let value = cardForm.value.number.replace(/\s/g, '')
  value = value.replace(/(.{4})/g, '$1 ').trim()
  cardForm.value.number = value
  
  // Auto-detect card type
  autoDetectCardType(value.replace(/\s/g, ''))
}

const formatExpiry = () => {
  let value = cardForm.value.expiry.replace(/\D/g, '')
  
  // Automatically insert "/" after 2 digits
  if (value.length >= 2) {
    value = value.substring(0, 2) + '/' + value.substring(2, 4)
  }
  
  cardForm.value.expiry = value
}

const autoDetectCardType = (cardNumber) => {
  if (!cardNumber) {
    detectedCardType.value = ''
    selectedPaymentMethod.value = null
    return
  }
  
  const patterns = {
    visa: /^4/,
    master: /^5[1-5]/,
    amex: /^3[47]/
  }
  
  for (const [type, pattern] of Object.entries(patterns)) {
    if (pattern.test(cardNumber)) {
      const method = cardPaymentMethods.value.find(m => m.id === type)
      if (method) {
        selectedPaymentMethod.value = method.id
        detectedCardType.value = type
        return
      }
    }
  }
  
  // Reset if no match found
  detectedCardType.value = ''
  selectedPaymentMethod.value = null
}

const loadPaymentMethods = async () => {
  try {
    loadingPaymentMethods.value = true
    const response = await api.get('/payments/payment_methods')
    
    if (response.data && response.data.payment_methods) {
      // Filter to only allow visa, mastercard, amex, and transferencia
      const allowedMethods = ['visa', 'master', 'amex', 'pse', 'efecty', 'bancolombia', 'banco_agrario', 'banco_av_villas', 'banco_bogota', 'banco_davivienda', 'banco_falabella', 'banco_gnb_sudameris', 'banco_itau', 'banco_occidente', 'banco_popular', 'banco_santander_colombia', 'bbva_colombia']
      cardPaymentMethods.value = response.data.payment_methods.filter(method => 
        allowedMethods.includes(method.id) || 
        method.payment_type_id === 'credit_card' && ['visa', 'master', 'amex'].includes(method.id) ||
        method.payment_type_id === 'bank_transfer'
      )
      
      // No need to set default payment method - will be set by auto-detection
      selectedPaymentMethod.value = null
    } else {
      throw new Error('Invalid response format')
    }
  } catch (error) {
    console.error('Error loading payment methods:', error)
    cardPaymentMethods.value = []
    selectedPaymentMethod.value = null
    $q.notify({
      type: 'negative',
      message: 'Error al cargar métodos de pago'
    })
  } finally {
    loadingPaymentMethods.value = false
  }
}

const loadSavedMethods = async () => {
  try {
    const response = await api.get('/payments/saved_payment_methods')
    
    if (response.data && response.data.saved_payment_methods) {
      savedMethods.value = response.data.saved_payment_methods
    } else {
      savedMethods.value = []
    }
  } catch (error) {
    console.error('Error loading saved payment methods:', error)
    // Don't show error to user, saved methods are optional
    savedMethods.value = []
  }
}

const selectSavedMethod = (method) => {
  selectedSavedMethod.value = method
  showNewCard.value = false
}

const deleteSavedMethod = async (method) => {
  try {
    deletingMethod.value = method.id
    await api.delete(`/payments/saved_payment_methods/${method.id}`)
    savedMethods.value = savedMethods.value.filter(m => m.id !== method.id)
    
    if (selectedSavedMethod.value?.id === method.id) {
      selectedSavedMethod.value = null
    }
    
    $q.notify({
      type: 'positive',
      message: 'Método de pago eliminado'
    })
  } catch (error) {
    console.error('Error deleting saved method:', error)
    $q.notify({
      type: 'negative',
      message: 'Error al eliminar método de pago'
    })
  } finally {
    deletingMethod.value = null
  }
}

const processPayment = async () => {
  try {
    processing.value = true
    
    // First tokenize the card
    const [month, year] = cardForm.value.expiry.split('/')
    const tokenResponse = await api.post('/payments/tokenize_card', {
      card_number: cardForm.value.number.replace(/\s/g, ''),
      expiration_month: month,
      expiration_year: '20' + year,
      security_code: cardForm.value.cvv,
      card_holder_name: cardForm.value.holderName
    })
    
    const token = tokenResponse.data.token
    
    // Process payment
    const paymentResponse = await api.post('/payments/process_payment', {
      transaction_amount: props.totalAmount,
      description: `Pago por ${props.cartItems.length} items`,
      payment_method_id: selectedPaymentMethod.value,
      payer: {
        email: props.userInfo.email,
        first_name: props.userInfo.name?.split(' ')[0] || '',
        last_name: props.userInfo.name?.split(' ').slice(1).join(' ') || ''
      },
      payment_method: {
        token: token,
        installments: selectedInstallments.value
      },
      external_reference: props.externalReference,
      metadata: props.metadata
    })
    
    const paymentResult = paymentResponse.data
    
    // Save payment method if requested
    if (savePaymentMethod.value && paymentResult.status === 'approved') {
      try {
        await api.post('/payments/save_payment_method', {
          payment_method_id: selectedPaymentMethod.value,
          last_four_digits: tokenResponse.data.last_four_digits,
          card_holder_name: cardForm.value.holderName,
          expiration_month: month,
          expiration_year: '20' + year,
          issuer_name: paymentResult.issuer_name
        })
      } catch (saveError) {
        console.error('Error saving payment method:', saveError)
        // Don't fail the payment if saving fails
      }
    }
    
    emit('payment-success', paymentResult)
    
  } catch (error) {
    console.error('Payment error:', error)
    const errorMessage = error.response?.data?.detail || 'Error al procesar el pago'
    emit('payment-error', errorMessage)
    
    $q.notify({
      type: 'negative',
      message: errorMessage
    })
  } finally {
    processing.value = false
  }
}

const processPaymentWithSavedMethod = async () => {
  try {
    processing.value = true
    
    // For saved methods, we need to re-tokenize as tokens expire
    // This is a security limitation - we can't store tokens long-term
    $q.notify({
      type: 'info',
      message: 'Para métodos guardados, necesitas ingresar el CVV nuevamente'
    })
    
    // Show a dialog to enter CVV for saved method
    $q.dialog({
      title: 'Confirmar pago',
      message: `Ingresa el CVV de tu tarjeta terminada en ${selectedSavedMethod.value.last_four_digits}`,
      prompt: {
        model: '',
        type: 'password',
        placeholder: 'CVV'
      },
      cancel: true,
      persistent: true
    }).onOk(async (cvv) => {
      if (!validateCVV(cvv)) {
        $q.notify({
          type: 'negative',
          message: 'CVV inválido'
        })
        return
      }
      
      try {
        // Re-tokenize with saved method data
        const tokenResponse = await api.post('/payments/tokenize_card', {
          card_number: '*'.repeat(12) + selectedSavedMethod.value.last_four_digits, // This won't work - need different approach
          expiration_month: selectedSavedMethod.value.expiration_month,
          expiration_year: selectedSavedMethod.value.expiration_year,
          security_code: cvv,
          card_holder_name: selectedSavedMethod.value.card_holder_name
        })
        
        // Continue with payment processing...
        // This approach has limitations - saved methods would need customer/card IDs from MercadoPago
        
      } catch (error) {
        console.error('Error with saved method payment:', error)
        $q.notify({
          type: 'negative',
          message: 'Error al procesar pago con método guardado. Por favor usa una nueva tarjeta.'
        })
      }
    })
    
  } catch (error) {
    console.error('Saved method payment error:', error)
    emit('payment-error', 'Error al procesar pago con método guardado')
  } finally {
    processing.value = false
  }
}

// Lifecycle
onMounted(async () => {
  try {
    await Promise.all([
      loadPaymentMethods(),
      loadSavedMethods()
    ])
    
    // If no saved methods, show new card form
    if (savedMethods.value.length === 0) {
      showNewCard.value = true
    }
    
  } catch (error) {
    console.error('Error during component initialization:', error)
    // Show error state
    $q.notify({
      type: 'negative',
      message: 'Error al inicializar el formulario de pago'
    })
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.q-card {
  background-image: url(../assets/texturafondo.png);
  background-size: cover;
  background-position: center center;
  background-color: rgba(0, 0, 0, 0.6); 
  background-blend-mode: overlay;
  color: #fff;
  border-radius: 8px;
  box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.3);
}

.text-white {
  color: white !important;
}

h3, h5 { 
  color: #FFF; 
  margin-bottom: 1rem; 
  font-weight: 500; 
}

p { 
  margin-bottom: 0.5rem; 
  line-height: 1.5; 
}

.q-separator { 
  background: rgba(255, 255, 255, 0.3); 
}
</style>