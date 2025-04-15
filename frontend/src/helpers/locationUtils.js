export const getUserLocation = () => {
    return new Promise((resolve, reject) => {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            if (latitude && longitude) {
              resolve({ latitude, longitude });
            } else {
              reject(new Error("Invalid geolocation data"));
            }
          },
          (error) => {
            reject(error);
          }
        );
      } else {
        reject(new Error("Geolocation is not supported by your device."));
      }
    });
  };


export const goToMapLocation = (latitude, longitude, $q) => {
  if (latitude && longitude) {
    // URL para abrir en Google Maps
    const mapUrl = `https://www.google.com/maps?q=${latitude},${longitude}`;
    window.open(mapUrl, '_blank');
  } else {
    $q.notify({
      message: 'Ubicación no disponible',
      color: 'negative',
      position: 'top',
    });
  }
};