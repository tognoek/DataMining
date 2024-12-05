let car, motor, stand;

function getColor(cluster) {
  const colors = [
    "rgba(255, 0, 0, 1)",
    "rgba(0, 0, 0, 1)",
    "rgba(0, 255, 0, 1)",
  ];
  return colors[cluster] || "rgba(0, 0, 0, 1)"; 
}
async function loadData(date) {
    if (!date) {
        alert("Please select a date");
        return;
    }

    const response = await fetch(`http://localhost:7000/api/year_month_day_hour_rate?date=${date}`);
    if (!response.ok) {
        alert('Error fetching data');
        return;
    }
    const data = await response.json();

    const hours = [];
    const carLeftRatios = [];
    const carRightRatios = [];
    const motorbikeLeftRatios = [];
    const motorbikeRightRatios = [];
    const carStandRatios = [];
    const motorbikeStandRatios = [];

    data.forEach(item => {
        hours.push(`${item.hour}:00`);
        carLeftRatios.push(item.car_left_ratio * 100);
        carRightRatios.push(item.car_right_ratio * 100);
        motorbikeLeftRatios.push(item.motorbike_left_ratio * 100);
        motorbikeRightRatios.push(item.motorbike_right_ratio * 100);
        carStandRatios.push(item.car_stand_ratio * 100);
        motorbikeStandRatios.push(item.motorbike_stand_ratio * 100);
    });

    if (car){
        car.destroy()
    }

    if (motor){
        motor.destroy()
    }

    if (stand){
        stand.destroy()
    }

    car =  new Chart(document.getElementById('carChart'), {
        type: 'bar',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Ô tô đi sang trái',
                    data: carLeftRatios,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Ô tô đi sang phải',
                    data: carRightRatios,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: `Biểu đồ tỷ lệ di chuyển trái phải của ô tô`,
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
                    beginAtZero: true
                }
            }
        }
    });

    motor = new Chart(document.getElementById('motorbikeChart'), {
        type: 'bar',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Xe máy đi sang trái',
                    data: motorbikeLeftRatios,
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Xe máy đi sang phải',
                    data: motorbikeRightRatios,
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: `Biểu đồ tỷ lệ di chuyển trái phải của xe máy`,
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
                    beginAtZero: true
                }
            }
        }
    });

    stand = new Chart(document.getElementById('standChart'), {
        type: 'bar',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Ô tô',
                    data: carStandRatios,
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Xe máy',
                    data: motorbikeStandRatios,
                    backgroundColor: 'rgba(255, 26, 186, 0.2)',
                    borderColor: 'rgba(255, 26, 186, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
              title: {
                display: true,
                text: `Biểu đồ tỷ lệ dùng xe`,
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
                    beginAtZero: true
                }
            }
        }
    });
}
document.getElementById("loadDataButton").addEventListener("click", () => {
  const date = document.getElementById("dateSelect").value;
  if (!date) {
    alert("Vui lòng chọn cả ngày và giờ.");
    return;
  }
  const formattedDate = date.split("-").join("/");
  loadData(formattedDate);
});
loadData("2024/11/30");
