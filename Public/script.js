const apiUrl =
  "http://127.0.0.1:5000/api/year_month_count_car_motorbike?year=2023&month=3";

  fetch(apiUrl)
  .then((response) => response.json())
  .then((data) => {
      data.sort((a, b) => a.hour - b.hour);
      const labels = data.map((item) => item.hour);
      const values = data.map((item) => item.car);
      const motorbikeValues = data.map((item) => item.motorbike);
      const ctx = document.getElementById("myChart").getContext("2d");
      new Chart(ctx, {
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
                      text: "Biểu đồ số lượng xe ô tô và xe máy tháng 3 năm 2023",
                      font: {
                          size: 20,
                      },
                      padding: {
                          top: 10,
                          bottom: 30
                      },
                      position: 'bottom' 
                  }
              },
              scales: {
                  x: {
                      title: {
                          display: true,
                          text: 'Giờ trong ngày', 
                          font: {
                              size: 14,
                          },
                      }
                  },
                  y: {
                      beginAtZero: true,
                      title: {
                          display: true,
                          text: 'Số lượng xe', 
                          font: {
                              size: 14,
                          },
                      }
                  }
              }
          }
      });
  })
  .catch((error) => {
      console.error("Lỗi khi nhận dữ liệu:", error);
  });