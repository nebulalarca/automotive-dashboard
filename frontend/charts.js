let _charts = {};

function mountChart(id, config) {
  if (_charts[id]) _charts[id].destroy();
  _charts[id] = new Chart(document.getElementById(id), config);
}

function buildTrendChart(data) {
  const { months, faults, repairs } = data;
  mountChart("trendChart", {
    type: "line",
    data: {
      labels: months,
      datasets: [
        {
          label: "Arıza",
          data: faults,
          borderColor: "#E24B4A",
          backgroundColor: "rgba(226,75,74,.08)",
          fill: true, tension: .4,
          pointRadius: 4, pointBackgroundColor: "#E24B4A",
          pointBorderColor: "#fff", pointBorderWidth: 2,
        },
        {
          label: "Tamir",
          data: repairs,
          borderColor: "#1D9E75",
          backgroundColor: "rgba(29,158,117,.08)",
          fill: true, tension: .4,
          pointRadius: 4, pointBackgroundColor: "#1D9E75",
          pointBorderColor: "#fff", pointBorderWidth: 2,
          borderDash: [6, 3],
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y: { ticks: { font: { size: 11 } }, grid: { color: "rgba(128,128,128,.1)" } },
        x: { ticks: { font: { size: 11 } }, grid: { display: false } },
      },
    },
  });
}

function buildCategoryChart(cats) {
  mountChart("catChart", {
    type: "doughnut",
    data: {
      labels: cats.map(c => c.name),
      datasets: [{
        data: cats.map(c => c.pct),
        backgroundColor: cats.map(c => c.color),
        borderWidth: 2, borderColor: "transparent", hoverOffset: 10,
      }],
    },
    options: {
      responsive: true, maintainAspectRatio: false, cutout: "62%",
      plugins: {
        legend: { display: false },
        tooltip: { callbacks: { label: c => `${c.label}: %${c.parsed}` } },
      },
    },
  });
  document.getElementById("catLegend").innerHTML = cats.map(c =>
    `<span style="display:flex;align-items:center;gap:4px">
       <span style="width:10px;height:10px;border-radius:2px;background:${c.color};flex-shrink:0"></span>
       ${c.name} <strong>%${c.pct}</strong>
     </span>`
  ).join("");
}

function buildCostChart(data) {
  const { brands, hours, costs, colors } = data;
  mountChart("costChart", {
    type: "bar",
    data: {
      labels: brands,
      datasets: [
        {
          label: "Ort. Süre (sa)",
          data: hours,
          backgroundColor: colors.map(c => c + "BB"),
          yAxisID: "y",
          borderRadius: 4,
        },
        {
          label: "Maliyet (₺00)",
          data: costs.map(c => Math.round(c / 100)),
          backgroundColor: "rgba(226,75,74,.15)",
          borderColor: "#E24B4A",
          borderWidth: 1.5,
          type: "line",
          yAxisID: "y2",
          tension: .4,
          pointRadius: 4,
          pointBackgroundColor: "#E24B4A",
        },
      ],
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        y:  { position: "left",  ticks: { font: { size: 11 } }, grid: { color: "rgba(128,128,128,.1)" } },
        y2: { position: "right", ticks: { font: { size: 11 } }, grid: { display: false } },
        x:  { ticks: { font: { size: 11 } }, grid: { display: false } },
      },
    },
  });
}

function buildMtbfChart(models) {
  const sorted = [...models].sort((a, b) => b.mtbf - a.mtbf);
  const BRAND_COLORS = {
    "BMW":"#E24B4A","Mercedes":"#378ADD","Toyota":"#1D9E75",
    "Volkswagen":"#EF9F27","Ford":"#7F77DD","Honda":"#D4537E",
    "Audi":"#0F6E56","Hyundai":"#993C1D"
  };
  mountChart("mtbfChart", {
    type: "bar",
    data: {
      labels: sorted.map(m => `${m.brand} ${m.model}`),
      datasets: [{
        label: "MTBF (gün)",
        data: sorted.map(m => m.mtbf),
        backgroundColor: sorted.map(m => (BRAND_COLORS[m.brand] || "#888") + "CC"),
        borderRadius: 4,
      }],
    },
    options: {
      indexAxis: "y",
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { ticks: { font: { size: 10 } }, grid: { color: "rgba(128,128,128,.1)" } },
        y: { ticks: { font: { size: 10 } }, grid: { display: false } },
      },
    },
  });
}
