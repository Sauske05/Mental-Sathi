Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';


//let userName = sessionStorage.getItem('user_id');
let ctx_bar = document.getElementById("myAreaChart").getContext("2d");

let emotions = ["Happy", "Sad", "Angry", "Excited", "Calm", "Anxious"];
let emotions_dict = {
    "Happy": 0, "Sad": 0, "Angry": 0, "Excited": 0, "Calm": 0, "Anxious": 0
};
async function getSentimentData(duration) {
    try {
        const user_email_response = await fetch('/get_session/', {
            method : "GET",
        })
       const user_email = await user_email_response.json()
        console.log(`This is the email -> ${user_email.userEmail}`)
        const url = `http://127.0.0.1:8000/sentiment/fetch_sentiment_data/${user_email.userEmail}`;

        console.log('Attempting to fetch URL:', url);
        console.log('Full resolved URL will be:', window.location.pathname + url);
        //const url = `sentiment/fetch_sentiment_data/arun`;
        //console.log(userName)
        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json',

                },
                body: JSON.stringify({
                    'duration': duration
                })
            });
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
    } catch (error) {
        console.error('Error fetching User Email:', error.message);
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

async function initializeDashboard(duration) {
    try {
        const sentimentData = await getSentimentData(duration);

        Object.keys(emotions_dict).forEach(key => emotions_dict[key] = 0);

        updateEmotionDict(sentimentData);

        let frequencies = Object.values(emotions_dict);

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
                    }
                }
            }
        });

    } catch (error) {
        console.error('Dashboard initialization error:', error);
    }
}

// Call initialization when the page loads
document.addEventListener('DOMContentLoaded', async function () {
    await initializeDashboard('weekly');

    document.getElementById('areaWeeklyButton').addEventListener('click', async () => await initializeDashboard('weekly'))
    document.getElementById('areaMonthlyButton').addEventListener('click', async () => await initializeDashboard('monthly'))
    document.getElementById('areaAllTimeButton').addEventListener('click', async () => await initializeDashboard('all_time'))

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
