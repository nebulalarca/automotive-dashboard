const API_BASE = "http://localhost:5001/api";

const FILTERS = { year: 2024, brand: "all" };

async function apiFetch(endpoint) {
  const params = new URLSearchParams({
    year:  FILTERS.year,
    brand: FILTERS.brand,
  });
  const url = `${API_BASE}/${endpoint}?${params}`;
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`[API] ${endpoint} hatası:`, err);
    return null;
  }
}

async function fetchAll() {
  showLoader(true);
  try {
    const [kpis, trend, categories, brands, parts,
           automations, alarms, models, repairCost] = await Promise.all([
      apiFetch("kpis"),
      apiFetch("trend"),
      apiFetch("categories"),
      apiFetch("brands"),
      apiFetch("parts"),
      apiFetch("automations"),
      apiFetch("alarms"),
      apiFetch("models"),
      apiFetch("repair-cost"),
    ]);

    return { kpis, trend, categories, brands, parts,
             automations, alarms, models, repairCost };
  } finally {
    showLoader(false);
  }
}

async function updateFilters(year, brand) {
  if (year)  FILTERS.year  = year;
  if (brand) FILTERS.brand = brand;
  await refreshDashboard();
}

function showLoader(visible) {
  const el = document.getElementById("loader");
  if (el) el.style.display = visible ? "flex" : "none";
}
