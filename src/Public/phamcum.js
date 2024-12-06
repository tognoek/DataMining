let carChart, motorbikeChart;

function getColor(cluster) {
  const colors = [
    "rgba(255, 0, 0, 1)",
    "rgba(0, 0, 0, 1)",
    "rgba(0, 255, 0, 1)",
  ];
  return colors[cluster] || "rgba(0, 0, 0, 1)"; 
}

async function drawClusterCharts(date) {
  const url = `http://localhost:7000/api/year_month_day_clustering_speed_time?date=${date}`;
  const response = await fetch(url);

  if (response.ok) {
    const data = await response.json();
    const labels = Array.from({ length: 25 }, (_, i) => i);
    const carData = labels.map((hour) => {
      const item = data.find((d) => d.hour === hour);
      return {
        x: hour,
        y: item ? item.car_speed : null, 
        cluster: item ? item.cluster : null,
      };
    });

    const motorbikeData = labels.map((hour) => {
      const item = data.find((d) => d.hour === hour);
      return {
        x: hour,
        y: item ? item.motorbike_speed : null, 
        cluster: item ? item.cluster : null,
      };
    });

    if (carChart) carChart.destroy();
    if (motorbikeChart) motorbikeChart.destroy();

    const ctx1 = document.getElementById("carChart").getContext("2d");
    carChart = new Chart(ctx1, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Tốc độ ô tô",
            data: carData.map((item) => ({
              x: item.x,
              y: item.y,
            })),
            backgroundColor: carData.map((item) =>
              item.cluster !== null
                ? getColor(item.cluster)
                : "rgba(200, 200, 200, 0.5)"
            ),
            pointRadius: 8, 
            pointHoverRadius: 10,
          },
        ],
      },
      options: {
        plugins: {
            legend: {
                display: false 
            }
        },
        responsive: true,
        scales: {
          x: {
            title: { display: true, text: "Giờ" },
            ticks: { stepSize: 1 },
            min: 0,
            max: 24,
          },
          y: {
            title: { display: true, text: "Tốc độ ô tô (km/h)" },
            beginAtZero: true,
          },
        },
      },
    });

    const ctx2 = document.getElementById("motorbikeChart").getContext("2d");
    motorbikeChart = new Chart(ctx2, {
      type: "scatter",
      data: {
        datasets: [
          {
            label: "Tốc độ xe máy",
            data: motorbikeData.map((item) => ({
              x: item.x,
              y: item.y,
            })),
            backgroundColor: motorbikeData.map((item) =>
              item.cluster !== null
                ? getColor(item.cluster)
                : "rgba(200, 200, 200, 0.5)"
            ),
            pointRadius: 8, 
            pointHoverRadius: 10,
          },
        ],
      },
      options: {
        plugins: {
            legend: {
                display: false 
            }
        },
        responsive: true,
        scales: {
          x: {
            title: { display: true, text: "Giờ" },
            ticks: { stepSize: 1 },
            min: 0,
            max: 24,
          },
          y: {
            title: { display: true, text: "Tốc độ xe máy (km/h)" },
            beginAtZero: true,
          },
        },
      },
    });
  } else {
    alert("Lỗi khi tải dữ liệu từ API.");
  }
}
document.getElementById("loadDataButton").addEventListener("click", () => {
  const date = document.getElementById("dateSelect").value;
  if (!date) {
    alert("Vui lòng chọn cả ngày và giờ.");
    return;
  }
  const formattedDate = date.split("-").join("/");
  drawClusterCharts(formattedDate);
});
drawClusterCharts("2024/11/30");
