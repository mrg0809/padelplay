export function openMaps(coordinates) {
  if (!coordinates) return;
  const mapsUrl = `https://www.google.com/maps?q=${coordinates.lat},${coordinates.lng}`;
  window.open(mapsUrl, "_blank");
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
