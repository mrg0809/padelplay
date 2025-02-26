export function formatDate(date) {
    const [year, month, day] = date.split('-').map(Number);
    const localDate = new Date(year, month - 1, day);
    return localDate.toLocaleDateString("es-MX", {
      weekday: "short",
      day: "numeric",
      month: "short",
    });
}

export function formatDateString(dateString) {
    if (!dateString) return "Fecha no disponible";
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      return "Fecha no disponible";
    }
    return date.toLocaleString();
  };
  
export function formatLongDate(date) {
    if (!date) return "No especificado";
    const options = { year: "numeric", month: "long", day: "numeric" };
    return new Date(date).toLocaleDateString("es-MX", options);
};

export function generateDays(currentDate) {
    let days = [];
    for (let i = 0; i < 7; i++) {
        let date = new Date(currentDate);
        date.setDate(currentDate.getDate() + i);
        days.push({
        date: date.toISOString().split("T")[0],
        label: date.toLocaleDateString("es-ES", { weekday: "short", day: "numeric" }),
        month: date.toLocaleDateString("es-ES", { month: "short" }).toUpperCase(),
        });
    }
    return days;
};

export const generateDaysFrom = (startDate) => {
  return Array.from({ length: 7 }, (_, i) => {
    const day = new Date(startDate);
    day.setDate(day.getDate() + i);
    return {
      label: day.toLocaleDateString("es-ES", { weekday: "short", day: "numeric" }),
      date: day.toISOString().split("T")[0],
    };
  });
};


export const previousWeek = () => {
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
  // Retrocede una semana
  currentDate.value.setDate(currentDate.value.getDate() - 7);
  generateDays();
  fetchAvailableTimes();
};

  
export const nextWeek = () => {
  currentDate.value.setDate(currentDate.value.getDate() + 7);
  generateDays();
  fetchAvailableTimes();
};
