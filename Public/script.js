let myChart;
document
  .getElementById("loadDataButton")
  .addEventListener("click", function () {
    const year = document.getElementById("yearSelect").value;
    const month = document.getElementById("monthSelect").value;
    get(year, month);
  });

const get = (year, month) => {
  if (myChart) {
    myChart.destroy();
  }
  const apiUrl = `http://127.0.0.1:5000/api/year_month_count_car_motorbike?year=${year}&month=${month}`;
  fetch(apiUrl)
    .then((response) => response.json())
    .then((data) => {
      data.sort((a, b) => a.hour - b.hour);
      const labels = data.map((item) => item.hour);
      const values = data.map((item) => item.car);
      const motorbikeValues = data.map((item) => item.motorbike);

      const ctx = document.getElementById("myChart").getContext("2d");
      myChart = new Chart(ctx, {
        type: "line",
        data: {
          labels: labels,
          datasets: [
            {
              label: "Ô tô",
              data: values,
              fill: false,
              borderColor: "rgb(75, 192, 192)",
              tension: 0.1,
            },
            {
              label: "Xe máy",
              data: motorbikeValues,
              fill: false,
              borderColor: "rgb(255, 99, 132)",
              tension: 0.1,
            },
          ],
        },
        options: {
          responsive: true,
          aspectRatio: 3,
          plugins: {
            title: {
              display: true,
              text: `Biểu đồ số lượng xe ô tô và xe máy ${month}/${year}`,
              font: {
                size: 20,
              },
              padding: {
                top: 10,
                bottom: 30,
              },
            },
          },
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    })
    .catch((error) => {
      console.error("Lỗi khi nhận dữ liệu:", error);
    });
};
get(2024, 11);
