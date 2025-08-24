/**
 * MercadoPago Payment Utilities
 * Helper functions for integrating with MercadoPago Checkout API
 */

import api from 'src/services/api';

/**
 * Prepare and redirect to MercadoPago payment
 * @param {Object} paymentData - Payment data object
 * @param {Array} paymentData.cartItems - Array of cart items
 * @param {Object} paymentData.userInfo - User information
 * @param {string} paymentData.externalReference - Optional external reference
 * @param {Object} paymentData.metadata - Optional metadata
 */
export const initiateMercadoPagoPayment = (paymentData) => {
  // Validate required data
  if (!paymentData.cartItems || !paymentData.userInfo) {
    throw new Error('Cart items and user info are required');
  }

  // Store payment data in localStorage for the payment page
  localStorage.setItem('mercadoPaymentData', JSON.stringify(paymentData));

  // Navigate to MercadoPago payment page
  window.location.href = '/mercado-payment';
};

/**
 * Create MercadoPago preference via backend API
 * @param {Object} paymentData - Payment data
 * @returns {Promise} - Promise resolving to preference data
 */
export const createMercadoPagoPreference = async (paymentData) => {
  try {
    const response = await api.post('/payments/create_preference', {
      cart_items: paymentData.cartItems,
      user_info: paymentData.userInfo,
      external_reference: paymentData.externalReference,
      metadata: paymentData.metadata
    });

    return response.data;
  } catch (error) {
    console.error('Error creating MercadoPago preference:', error);
    throw error;
  }
};

/**
 * Redirect directly to MercadoPago checkout
 * @param {string} initPoint - MercadoPago init_point URL
 */
export const redirectToMercadoPago = (initPoint) => {
  if (!initPoint) {
    throw new Error('Init point URL is required');
  }
  
  window.location.href = initPoint;
};

/**
 * Format cart items for MercadoPago
 * @param {Array} items - Raw cart items
 * @returns {Array} - Formatted items
 */
export const formatCartItems = (items) => {
  return items.map(item => ({
    id: item.id || String(Math.random()),
    title: item.name || item.title,
    quantity: item.quantity || 1,
    unit_price: parseFloat(item.price || item.unit_price || 0)
  }));
};

/**
 * Create user info object for MercadoPago
 * @param {Object} user - User data
 * @returns {Object} - Formatted user info
 */
export const formatUserInfo = (user) => {
  return {
    email: user.email,
    name: user.full_name || user.name || ''
  };
};

/**
 * Complete MercadoPago payment flow
 * @param {Array} cartItems - Cart items
 * @param {Object} userInfo - User information  
 * @param {string} externalReference - Optional external reference
 * @param {Object} metadata - Optional metadata
 */
export const processMercadoPagoPayment = async (cartItems, userInfo, externalReference = null, metadata = null) => {
  try {
    // Format data
    const formattedItems = formatCartItems(cartItems);
    const formattedUser = formatUserInfo(userInfo);

    // Create preference
    const preference = await createMercadoPagoPreference({
      cartItems: formattedItems,
      userInfo: formattedUser,
      externalReference,
      metadata
    });

    // Redirect to MercadoPago
    if (preference.init_point) {
      redirectToMercadoPago(preference.init_point);
      return preference;
    } else {
      throw new Error('No init_point received from MercadoPago');
    }

  } catch (error) {
    console.error('Error processing MercadoPago payment:', error);
    throw error;
  }
};