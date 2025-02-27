// Helper function to safely extract coordinates from club data
// This function handles both geolocation object and direct lat/lng properties
export function extractCoordinates(clubData) {
  if (!clubData) return null;
  
  if (clubData.geolocation && clubData.geolocation.coordinates) {
    return { lat: clubData.geolocation.coordinates[1], lng: clubData.geolocation.coordinates[0] };
  } else if (clubData.latitude && clubData.longitude) {
    return { lat: parseFloat(clubData.latitude), lng: parseFloat(clubData.longitude) };
    console.log("Extracted coordinates from lat/lng:", { lat: parseFloat(clubData.latitude), lng: parseFloat(clubData.longitude) });
  }
  return null;
}

// Open Google Maps with the given coordinates
export function openMaps(coordinates) {
  if (!coordinates) return;
  const url = `https://www.google.com/maps/search/?api=1&query=${coordinates.lat},${coordinates.lng}`;
  window.open(url, '_blank');
}


export function openSocialLink(url) {
  if (url) {
    window.open(url, "_blank");
  }
}

export function openWhatsApp(number) {
  if (number) {
    const whatsappUrl = `https://wa.me/${number}`;
    window.open(whatsappUrl, "_blank");
  }
}
