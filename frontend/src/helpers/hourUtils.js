export const generateHours = (openingTime, closingTime) => {
    const hours = [];
    const [startHour, startMinutes] = openingTime.split(":").map(Number);
    const [endHour, endMinutes] = closingTime.split(":").map(Number);
  
    let currentTime = new Date();
    currentTime.setHours(startHour, startMinutes, 0, 0);
  
    const endTime = new Date();
    endTime.setHours(endHour, endMinutes, 0, 0);
  
    while (currentTime <= endTime) {
      hours.push(
        `${String(currentTime.getHours()).padStart(2, "0")}:${String(
          currentTime.getMinutes()
        ).padStart(2, "0")}`
      );
      currentTime.setMinutes(currentTime.getMinutes() + 30);
    }
  
    return hours;
  };

export const endtime_calculate = ( startTime , duration ) => {
  const startTimeParts = startTime.split(":");
  const startHour = parseInt(startTimeParts[0]);
  const startMinute = parseInt(startTimeParts[1]);
  const durationHours = Math.floor(duration / 60);
  const durationMinutes = duration % 60;

  let endHour = startHour + durationHours;
  let endMinute = startMinute + durationMinutes;

  // Ajustar minutos y horas si es necesario
  if (endMinute >= 60) {
    endHour += Math.floor(endMinute / 60);
    endMinute %= 60;
  }
  // Formatear end_time correctamente
  const formattedEndHour = String(endHour).padStart(2, "0");
  const formattedEndMinute = String(endMinute).padStart(2, "0");
  
  return `${formattedEndHour}:${formattedEndMinute}`;
};