Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

let ctx_bar = document.getElementById("myAreaChart").getContext("2d");

let emotions = ["Happy", "Sad", "Angry", "Excited", "Calm", "Anxious"];
let frequencies = [45, 50, 42, 48, 46, 44];

new Chart(ctx_bar, {
    type: 'bar',
    data: {
        labels: emotions,
        datasets: [{
            label: "Emotion Frequency",
            backgroundColor: [
                "rgba(78, 115, 223, 0.7)",
                "rgba(231, 74, 59, 0.7)",
                "rgba(246, 194, 62, 0.7)",
                "rgba(28, 200, 138, 0.7)",
                "rgba(133, 135, 150, 0.7)",
                "rgba(54, 185, 204, 0.7)"
            ],
            borderColor: [
                "rgba(78, 115, 223, 1)",
                "rgba(231, 74, 59, 1)",
                "rgba(246, 194, 62, 1)",
                "rgba(28, 200, 138, 1)",
                "rgba(133, 135, 150, 1)",
                "rgba(54, 185, 204, 1)"
            ],
            borderWidth: 2,
            borderRadius: 10,
            data: frequencies
        }]
    },
    options: {
        maintainAspectRatio: false,
        responsive: true,
        layout: {
            padding: {
                left: 10,
                right: 25,
                top: 25,
                bottom: 0
            }
        },
        scales: {
            x: {
                ticks: {color: "white", font: {size: 14}},
                grid: {display: false}
            },
            y: {
                ticks: {
                    color: "white",
                    font: {size: 14},
                    padding: 10
                },
                grid: {
                    color: "rgba(255,255,255,0.2)"
                }
            }
        },
        plugins: {
            legend: {
                display: false,
                labels: {
                    color: "white",
                    font: {size: 14}
                }
            },
            tooltip: {
                backgroundColor: "rgba(0, 0, 0, 0.8)",
                titleColor: "white",
                bodyColor: "white",
                padding: 10,
                cornerRadius: 5
            }
        },
        animation: {
            duration: 1500,
            easing: 'easeOutBounce'
        }
    }
});


// Pie Chart Example
let ctx = document.getElementById("myPieChart");
let myPieChart = new Chart(ctx, {
  type: 'doughnut',
  data: {
    labels: ["Happy", "Sad", "Neutral"],
    datasets: [{
      data: [55, 30, 15],
      backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
      hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
      hoverBorderColor: "rgba(234, 236, 244, 1)",
    }],
  },
  options: {
    maintainAspectRatio: false,
    tooltips: {
      backgroundColor: "rgb(255,255,255)",
      bodyFontColor: "#858796",
      borderColor: '#dddfeb',
      borderWidth: 1,
      xPadding: 15,
      yPadding: 15,
      displayColors: false,
      caretPadding: 10,
    },
    legend: {
      display: false
    },
    cutoutPercentage: 80,
  },
});
