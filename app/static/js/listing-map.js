// Shows the listing location on an OpenStreetMap map (Leaflet).
document.addEventListener("DOMContentLoaded", () => {
  const el = document.getElementById("listing-map");
  if (!el || typeof L === "undefined") return;

  const lat = parseFloat(el.dataset.lat);
  const lng = parseFloat(el.dataset.lng);
  if (Number.isNaN(lat) || Number.isNaN(lng)) return;

  const map = L.map(el, { scrollWheelZoom: false }).setView([lat, lng], 15);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);
  L.marker([lat, lng]).addTo(map).bindPopup(el.dataset.title || "").openPopup();
});
