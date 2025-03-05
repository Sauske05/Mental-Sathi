Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


//let userName = sessionStorage.getItem('user_id');
let ctx_bar = document.getElementById("myAreaChart").getContext("2d");

let emotions = ["Happy", "Sad", "Angry", "Excited", "Calm", "Anxious"];
let emotions_dict = {
    "Happy": 0, "Sad": 0, "Angry": 0, "Excited": 0, "Calm": 0, "Anxious": 0
};

async function getSentimentData() {
    const url = `http://127.0.0.1:8000/sentiment/fetch_sentiment_data/arun`;

  console.log('Attempting to fetch URL:', url);
  console.log('Full resolved URL will be:', window.location.pathname + url);
  //const url = `sentiment/fetch_sentiment_data/arun`;
  //console.log(userName)
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Response status: ${response.status}`);
    }

    const json = await response.json();
    console.log(json);
    return json;
  } catch (error) {
    console.error('Error fetching sentiment data:', error.message);
    return null;
  }
}

function updateEmotionDict(jsonData) {
    if (!jsonData) return;

    jsonData.forEach(data => {
        if (emotions_dict.hasOwnProperty(data.sentiment_data)) {
            emotions_dict[data.sentiment_data] += 1;
        }
    });
}

// Initialization function to set up charts
async function initializeDashboard() {
    try {
        // Fetch sentiment data
        const sentimentData = await getSentimentData();

        // Update emotion dictionary
        updateEmotionDict(sentimentData);

        // Update frequencies for bar chart
        let frequencies = Object.values(emotions_dict);

        // Create or update bar chart
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
                // ... (rest of the options remain the same as in original code)
            }
        });

    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

// Call initialization when the page loads
document.addEventListener('DOMContentLoaded', initializeDashboard);
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
