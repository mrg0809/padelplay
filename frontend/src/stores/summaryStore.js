import { defineStore } from 'pinia';

export const useSummaryStore = defineStore('summary', {
  // State: Donde guardamos los datos temporalmente
  state: () => ({
    /**
     * Contiene los detalles necesarios para el componente ReservationSummary.
     * Se establece antes de navegar a la página de resumen y se limpia después.
     * Ejemplo: { summaryTitle: '...', itemDetails: [...], baseData: {...}, ... }
     */
    currentSummaryDetails: null,
  }),

  getters: {
    /**
     * Devuelve los detalles actuales del resumen.
     * @param {object} state El estado actual del store.
     * @returns {object | null} Los detalles del resumen o null si no hay ninguno.
     */
    getSummaryDetails: (state) => state.currentSummaryDetails,

    /**
     * Indica si hay detalles de resumen activos en el store.
     * @param {object} state El estado actual del store.
     * @returns {boolean} True si hay detalles, false si no.
     */
    hasActiveSummary: (state) => state.currentSummaryDetails !== null,
  },

  // Actions: Métodos para modificar el estado
  actions: {
    /**
     * Establece los detalles para el próximo resumen a mostrar.
     * @param {object} details El objeto completo con las props para ReservationSummary.
     */
    setSummaryDetails(details) {
      // Copiar el objeto para evitar problemas de reactividad si se modifica el original
      this.currentSummaryDetails = { ...details };
      console.log('Summary details set in store:', this.currentSummaryDetails); // Para depuración
    },

    /**
     * Limpia los detalles del resumen del store.
     * Se debe llamar después de que el resumen ya no sea necesario (ej. al salir de la página).
     */
    clearSummaryDetails() {
      console.log('Clearing summary details from store.'); // Para depuración
      this.currentSummaryDetails = null;
    },
  },
});