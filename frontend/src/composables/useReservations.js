import { ref, computed } from "vue";
import { fetchAvailableTimes, fetchAvailableCourts } from "../services/api/reservations";
import { generateDays } from "../helpers/dateUtils";
import { getCourtPrice } from "../helpers/reservationsUtils";

export function useReservations(clubId) {
  const currentDate = ref(new Date());
  const days = ref(generateDays(currentDate.value));
  const selectedDay = ref(days.value[0]?.date || "");
  const consolidatedTimes = ref([]);
  const selectedTime = ref("");
  const availableCourts = ref([]);
  const loadingTimes = ref(false);
  const loadingCourts = ref(false);
  const selectedCourt = ref(null);
  const selectedDuration = ref(null);
  
  const timeOptions = ref([
    { label: "60 minutos", duration: 60 },
    { label: "90 minutos", duration: 90 },
    { label: "120 minutos", duration: 120 },
  ]);

  const previousWeek = () => {
    const today = new Date();
    const firstVisibleDay = new Date(currentDate.value);

    // Asegurarse de que no se retroceda más allá del día actual
    if (
      firstVisibleDay.getFullYear() === today.getFullYear() &&
      firstVisibleDay.getMonth() === today.getMonth() &&
      firstVisibleDay.getDate() === today.getDate()
    ) {
      console.log("No se pueden seleccionar días anteriores al día actual.");
      return;
    }
    currentDate.value.setDate(currentDate.value.getDate() - 7);
    days.value = generateDays(currentDate.value);
    fetchTimes();
  };

  const nextWeek = () => {
    currentDate.value.setDate(currentDate.value.getDate() + 7);
    days.value = generateDays(currentDate.value);
    fetchTimes();
  };

  const selectDay = (day) => {
    selectedDay.value = day;
    fetchTimes();
  };

  const selectTime = (time) => {
    selectedTime.value = time || "";
    fetchCourts();
    selectedCourt.value = null; // Reset selected court when selecting a new time
  };

  const fetchTimes = async () => {
    loadingTimes.value = true;
    try {
      consolidatedTimes.value = await fetchAvailableTimes(clubId, selectedDay.value);
      selectedTime.value = ""; // Reset selected time when fetching new times
    } catch (error) {
      console.error("Error fetching available times:", error);
    } finally {
      loadingTimes.value = false;
    }
  };

  const fetchCourts = async () => {
    loadingCourts.value = true;
    try {
      availableCourts.value = await fetchAvailableCourts(clubId, selectedDay.value, selectedTime.value);
      selectedCourt.value = null; // Reset selected court when fetching new courts
    } catch (error) {
      console.error("Error fetching available courts:", error);
    } finally {
      loadingCourts.value = false;
    }
  };

  return {
    days,
    selectedDay,
    consolidatedTimes,
    selectedTime,
    availableCourts,
    loadingTimes,
    loadingCourts,
    timeOptions,
    selectedCourt: selectedCourt.value,
    selectedDuration: selectedDuration.value,
    previousWeek,
    nextWeek,
    selectDay,
    selectTime,
    fetchTimes,
    fetchCourts,
    getCourtPrice,
  };
}
