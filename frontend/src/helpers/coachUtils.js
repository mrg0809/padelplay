export const processAvailability = (availabilityData) => {
    const processedAvailability = {};
    for (const schedule of availabilityData) {
      const day = schedule.day;
      const startTime = schedule.start_time;
      const endTime = schedule.end_time;
  
      processedAvailability[day] = []; // Inicializar array para el día
  
      if (startTime && endTime) {
        const [startHour, startMinute] = startTime.split(":").map(Number);
        const [endHour, endMinute] = endTime.split(":").map(Number);
  
        let currentHour = startHour;
        let currentMinute = startMinute;
  
        while (currentHour < endHour || (currentHour === endHour && currentMinute < endMinute)) {
          const formattedTime = `${String(currentHour).padStart(2, "0")}:${String(currentMinute).padStart(2, "0")}`;
          processedAvailability[day].push(formattedTime);
  
          currentMinute += 60;
          if (currentMinute >= 60) {
            currentHour++;
            currentMinute -= 60;
          }
        }
      }
    }
    return processedAvailability;
  };