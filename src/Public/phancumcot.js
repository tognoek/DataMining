let carChart, motorbikeChart;

function getColor(cluster) {
  const colors = [
    "rgba(255, 0, 0, 0.8)", // Màu cho cluster 0
    "rgba(0, 0, 255, 0.8)", // Màu cho cluster 1
    "rgba(0, 255, 0, 0.8)", // Màu cho cluster 2
  ];
  return colors[cluster] || "rgba(0, 0, 0, 0.8)"; // Mặc định màu đen
}

async function drawClusterCharts(date) {
  const url = `http://localhost:7000/api/year_month_day_clustering_speed_time?date=${date}`;
  const response = await fetch(url);

  if (response.ok) {
    const data = await response.json();
    
    const carClusterStats = [ { count: 0, totalSpeed: 0 }, { count: 0, totalSpeed: 0 }, { count: 0, totalSpeed: 0 }];
    const motorbikeClusterStats = [ { count: 0, totalSpeed: 0 }, { count: 0, totalSpeed: 0 }, { count: 0, totalSpeed: 0 }];
    
    data.forEach((item) => {
      carClusterStats[item.cluster].count++;
      carClusterStats[item.cluster].totalSpeed += item.car_speed;
      motorbikeClusterStats[item.cluster].count++;
      motorbikeClusterStats[item.cluster].totalSpeed += item.motorbike_speed;
    });
    const carAvgSpeeds = carClusterStats.map(stat => (stat.count > 0 ? stat.totalSpeed / stat.count : 0));
    const motorbikeAvgSpeeds = motorbikeClusterStats.map(stat => (stat.count > 0 ? stat.totalSpeed / stat.count : 0));
    const carData = {
      labels: ['Nhóm 1', 'Nhóm 2', 'Nhóm 3'],
      datasets: [
        {
          label: 'Số lượng ô tô',
          data: carClusterStats.map(stat => stat.count),
          backgroundColor: ['rgba(255, 0, 0, 0.8)', 'rgba(0, 0, 255, 0.8)', 'rgba(0, 255, 0, 0.8)'],
          borderColor: ['rgba(255, 0, 0, 1)', 'rgba(0, 0, 255, 1)', 'rgba(0, 255, 0, 1)'],
          borderWidth: 1,
        },
      ],
    };

    const motorbikeData = {
      labels: ['Nhóm 1', 'Nhóm 2', 'Nhóm 3'],
      datasets: [
        {
          label: 'Số lượng xe máy',
          data: motorbikeClusterStats.map(stat => stat.count),
          backgroundColor: ['rgba(255, 0, 0, 0.8)', 'rgba(0, 0, 255, 0.8)', 'rgba(0, 255, 0, 0.8)'],
          borderColor: ['rgba(255, 0, 0, 1)', 'rgba(0, 0, 255, 1)', 'rgba(0, 255, 0, 1)'],
          borderWidth: 1,
        },
      ],
    };

    if (carChart) carChart.destroy();
    if (motorbikeChart) motorbikeChart.destroy();
    
    const ctx1 = document.getElementById("carChart").getContext("2d");
    carChart = new Chart(ctx1, {
      type: "bar",
      data: carData,
      options: {
        responsive: true,
        scales: {
          x: {
            title: { display: true, text: "Phân nhóm dữ liệu ô tô" },
          },
          y: {
            title: { display: true, text: "Số lượng xe" },
            beginAtZero: true,
          },
        },
        plugins: {
          legend: {
              display: false // Tắt hiển thị legend
          },
          tooltip: {
            callbacks: {
              label: function(tooltipItem) {
                const count = tooltipItem.raw;
                const clusterIndex = tooltipItem.dataIndex;
                const avgSpeed = carAvgSpeeds[clusterIndex];
                return `Số lượng xe: ${count} - Tốc độ trung bình: ${avgSpeed.toFixed(2)} km/h`;
              }
            }
          }
        }
      },
    });

    const ctx2 = document.getElementById("motorbikeChart").getContext("2d");
    motorbikeChart = new Chart(ctx2, {
      type: "bar",
      data: motorbikeData,
      options: {
        responsive: true,
        scales: {
          x: {
            title: { display: true, text: "Phân nhóm dữ liệu xe máy" },
          },
          y: {
            title: { display: true, text: "Số lượng xe" },
            beginAtZero: true,
          },
        },
        plugins: {
          legend: {
              display: false 
          },
          tooltip: {
            callbacks: {
              label: function(tooltipItem) {
                const count = tooltipItem.raw;
                const clusterIndex = tooltipItem.dataIndex;
                const avgSpeed = motorbikeAvgSpeeds[clusterIndex];
                return `Số lượng xe: ${count} - Tốc độ trung bình: ${avgSpeed.toFixed(2)} km/h`;
              }
            }
          }
        }
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
