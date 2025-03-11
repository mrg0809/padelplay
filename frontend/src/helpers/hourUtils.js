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