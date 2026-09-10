const themeToggleBtn = document.getElementById("theme-toggle");
const htmlElement = document.documentElement;

function applyTheme(theme) {
  htmlElement.setAttribute("data-theme", theme);
  themeToggleBtn.textContent = theme === "dark" ? "🌙 " : "☀️";
  localStorage.setItem("blackmonitor-theme", theme);
}

const savedTheme = localStorage.getItem("blackmonitor-theme") || "dark";
applyTheme(savedTheme);

themeToggleBtn.addEventListener("click", () => {
  const current = htmlElement.getAttribute("data-theme");
  applyTheme(current === "dark" ? "light" : "dark");
});


let cpuDonut = null, ramDonut = null, diskDonut = null;
let cpuHistoryChart = null, ramHistoryChart = null, networkChart = null;

function makeDonut(canvasId, color) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  return new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Used", "Free"],
      datasets: [{
        data: [0, 100],
        backgroundColor: [color, "#1E293B"],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      cutout: "70%",
      plugins: { legend: { display: false } },
    },
  });
}

function updateDonut(chart, value, labelElementId) {
  chart.data.datasets[0].data = [value, 100 - value];
  chart.update();
  document.getElementById(labelElementId).textContent = value + "%";
}

async function updateLatest() {
  try {
    const response = await fetch("/api/stats/latest");
    const data = await response.json();

    if (cpuDonut === null) {
      cpuDonut = makeDonut("cpu-donut", "#F2A93B");
      ramDonut = makeDonut("ram-donut", "#21C7A8");
      diskDonut = makeDonut("disk-donut", "#5B8DEF");
    }

    updateDonut(cpuDonut, data.cpu_percent, "cpu-donut-label");
    updateDonut(ramDonut, data.ram_percent, "ram-donut-label");
    updateDonut(diskDonut, data.disk_percent, "disk-donut-label");

    document.getElementById("uptime-value").textContent = data.uptime_formatted;

    if (data.battery_percent !== null && data.battery_percent !== undefined) {
      const plugged = data.battery_plugged ? "⚡" : "";
      document.getElementById("battery-value").textContent =
        data.battery_percent + "% " + plugged;
    } else {
      document.getElementById("battery-value").textContent = "N/A";
    }

    document.getElementById("temp-value").textContent =
      data.cpu_temp_c !== null && data.cpu_temp_c !== undefined
        ? data.cpu_temp_c + "°C"
        : "N/A";

    document.getElementById("status").textContent =
      "Last updated: " + new Date().toLocaleTimeString();
  } catch (error) {
    document.getElementById("status").textContent = "Connection lost";
  }
}

function buildAreaChart(canvasId, label, color) {
  const ctx = document.getElementById(canvasId).getContext("2d");
  return new Chart(ctx, {
    type: "line",
    data: {
      labels: [],
      datasets: [{
        label: label,
        data: [],
        borderColor: color,
        backgroundColor: color + "33",
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, max: 100 } },
    },
  });
}

async function updateHistory() {
  const response = await fetch("/api/stats/history");
  const data = await response.json();

  const labels = data.map(row => new Date(row.timestamp).toLocaleTimeString());
  const cpuValues = data.map(row => row.cpu_percent);
  const ramValues = data.map(row => row.ram_percent);
  const sentRates = data.map(row => row.net_sent_mbps);
  const recvRates = data.map(row => row.net_recv_mbps);

  if (cpuHistoryChart === null) {
    cpuHistoryChart = buildAreaChart("cpu-history-chart", "CPU %", "#F2A93B");
    ramHistoryChart = buildAreaChart("ram-history-chart", "RAM %", "#21C7A8");

    const ctx = document.getElementById("network-chart").getContext("2d");
    networkChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: [],
        datasets: [
          { label: "Upload MB/s", data: [], borderColor: "#F2A93B", tension: 0.3 },
          { label: "Download MB/s", data: [], borderColor: "#21C7A8", tension: 0.3 },
        ],
      },
      options: { responsive: true, maintainAspectRatio: false },
    });
  }

  cpuHistoryChart.data.labels = labels;
  cpuHistoryChart.data.datasets[0].data = cpuValues;
  cpuHistoryChart.update();

  ramHistoryChart.data.labels = labels;
  ramHistoryChart.data.datasets[0].data = ramValues;
  ramHistoryChart.update();

  networkChart.data.labels = labels;
  networkChart.data.datasets[0].data = sentRates;
  networkChart.data.datasets[1].data = recvRates;
  networkChart.update();
}

async function updateProcesses() {
  const response = await fetch("/api/processes");
  const data = await response.json();

  const tbody = document.getElementById("process-table-body");
  tbody.innerHTML = "";

  data.forEach(proc => {
    const row = document.createElement("tr");
    row.innerHTML =
      `<td>${proc.name}</td><td>${proc.cpu_percent}%</td><td>${proc.memory_percent}%</td>`;
    tbody.appendChild(row);
  });
}

updateLatest();
updateHistory();
updateProcesses();

setInterval(updateLatest, 5000);
setInterval(updateHistory, 15000);
setInterval(updateProcesses, 5000);