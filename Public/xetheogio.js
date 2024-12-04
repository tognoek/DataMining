let myChart;
document.getElementById("loadDataButton").addEventListener("click", () => {
  const date = document.getElementById("dateSelect").value;
  const hour = document.getElementById("hourSelect").value;

  if (!date || !hour) {
    alert("Vui lòng chọn cả ngày và giờ.");
    return;
  }
  const formattedDate = date.split("-").join("/");
  drawChart(formattedDate, hour)
});

async function drawChart(formattedDate, hour) {

  const queryString = `date=${formattedDate}&hour=${hour.slice(0, 2)}`; 
  const response = await fetch(`http://127.0.0.1:5000/api/year_month_day_hour_count_car_motorbike_all?${queryString}`);

  if (response.ok) {
    const data = await response.json();
    if (data.error) {
      alert(data.error);
    } else {
      if (myChart){
        myChart.destroy();
      }
      const minutes = data.map(item => item.minute);
  const carData = data.map(item => item.car);
  const motorbikeData = data.map(item => item.motorbike);
  const ctx = document.getElementById("myChart").getContext("2d");
  myChart = new Chart(ctx, {
    type: "line", 
    data: {
      labels: minutes, 
      datasets: [
        {
          label: "Số lượng ô tô",
          data: carData, 
          borderColor: "rgba(75, 192, 192, 1)",
          backgroundColor: "rgba(75, 192, 192, 0.2)",
          fill: true,
        },
        {
          label: "Số lượng xe máy",
          data: motorbikeData,
          borderColor: "rgba(255, 99, 132, 1)",
          backgroundColor: "rgba(255, 99, 132, 0.2)",
          fill: true,
        }
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Phút",
          },
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: "Số lượng xe",
          },
        },
      },
    },
  });
    }
  } else {
    alert("Lỗi khi tải dữ liệu.");
  }
}
drawChart('2024/11/30', '11:00')