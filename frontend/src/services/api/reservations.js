import api from "../api"

export const fetchAvailableTimes = async (clubId, selectedDay) => {
  if (!clubId || !selectedDay) return []; // Return empty array if no club or day selected

  try {
    const response = await api.get(`/reservations/available-times`, {
      params: {
        club_id: clubId,
        date: selectedDay,
      },
    });

    const rawAvailableTimes = response.data.available_times;

    // Consolidate unique times regardless of court
    let allTimes = Object.values(rawAvailableTimes).flat();

    // Round all times to the nearest 30-minute interval
    const roundToNearest30 = (time) => {
      const [hour, minute] = time.split(":").map(Number);
      const roundedMinute = minute < 15 ? 0 : minute < 45 ? 30 : 0;
      const roundedHour = minute >= 45 ? hour + 1 : hour;
      return `${String(roundedHour).padStart(2, "0")}:${String(roundedMinute).padStart(2, "0")}`;
    };

    allTimes = allTimes.map(roundToNearest30);

    // Remove duplicates and sort
    allTimes = [...new Set(allTimes)].sort();

    // Filter past times if the selected day is today
    const now = new Date();
    const selectedDate = new Date(`${selectedDay}T00:00:00`); // Force local timezone

    if (
      selectedDate.getFullYear() === now.getFullYear() &&
      selectedDate.getMonth() === now.getMonth() &&
      selectedDate.getDate() === now.getDate()
    ) {
      const currentMinutes = now.getMinutes();
      const currentHour = now.getHours();

      // Round up to the next 30-minute interval
      let roundedHour = currentHour;
      let roundedMinutes = currentMinutes < 30 ? 30 : 0;

      if (currentMinutes >= 30) {
        roundedHour += 1;
      }

      const currentTimeRounded = `${String(roundedHour).padStart(2, "0")}:${String(roundedMinutes).padStart(2, "0")}`;

      allTimes = allTimes.filter((time) => time >= currentTimeRounded);
    }

    console.log("Fetched times:", allTimes);
    return allTimes;
  } catch (error) {
    console.error("Error fetching available times:", error.message);
    throw error;
  }
};


export const fetchAvailableCourts = async (clubId, selectedDay, selectedTime) => {
  if (!clubId || !selectedDay || !selectedTime) return []; // Return empty array if any required param is missing

  try {
    const response = await api.get(`/reservations/available-courts`, {
      params: {
        club_id: clubId,
        date: selectedDay,
        time: selectedTime,
      },
    });
    console.log("Fetched courts:", response.data.available_courts);
    return response.data.available_courts;
  } catch (error) {
    console.error("Error fetching available courts:", error.message);
    throw error;
  }
};
