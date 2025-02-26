export function getCourtPrice(court, duration) {
  if (!court) return 0;
  const prices = {
    60: court.price_per_hour || 0,
    90: court.price_per_hour_and_half || 0,
    120: court.price_per_two_hour || 0,
  };
  return prices[duration] || 0;
}
