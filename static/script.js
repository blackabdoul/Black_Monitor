async function updateLatest() {
  try {
    const response = await fetch("/api/stats/latest");
    const data = await response.json();

    document.getElementById("cpu-value").textContent = data.cpu_percent + "%";
    document.getElementById("ram-value").textContent = data.ram_percent + "%";
    document.getElementById("disk-value").textContent = data.disk_percent + "%";
    document.getElementById("disk-detail").textContent =
      data.disk_used_gb + " / " + data.disk_total_gb + " GB";

    document.getElementById("status").textContent =
      "Last updated: " + new Date().toLocaleTimeString();
  } catch (error) {
    document.getElementById("status").textContent = "Connection lost";
  }
}

let historyChart = null;

async function updateHistory() {
  const response = await fetch("/api/stats/history");
  const data = await response.json();

  const labels = data.map(row => {
    const date = new Date(row.timestamp);
    return date.toLocaleTimeString();
  });

  const cpuValues = data.map(row => row.cpu_percent);
  const ramValues = data.map(row => row.ram_percent);

  if (historyChart === null) {
    const ctx = document.getElementById("history-chart").getContext("2d");
    historyChart = new Chart(ctx, {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            label: "CPU %",
            data: cpuValues,
            borderColor: "#F2A93B",
            tension: 0.3,
          },
          {
            label: "RAM %",
            data: ramValues,
            borderColor: "#21C7A8",
            tension: 0.3,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: { beginAtZero: true, max: 100 },
        },
      },
    });
  } else {
    historyChart.data.labels = labels;
    historyChart.data.datasets[0].data = cpuValues;
    historyChart.data.datasets[1].data = ramValues;
    historyChart.update();
  }
}

updateLatest();
updateHistory();

setInterval(updateLatest, 5000);
setInterval(updateHistory, 30000);