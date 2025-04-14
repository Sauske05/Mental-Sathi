// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

// let labels_dict = {
//   'Positive' : 33,
//   'Negative' : 33,
//   'Neutral' : 33
// }

function updateLabelDict(jsonData) {
    if (!jsonData || !jsonData.length) return;

    // Create dictionary to store user's sentiment scores
    let userScores = {};
    let userCount = {};

    // Calculate average sentiment score for each user
    jsonData.forEach(data => {
        const userName = data.user_name;
        const score = data.sentiment_score;

        // Skip entries without valid sentiment scores
        if (score === undefined || score === null) return;

        if (!userScores[userName]) {
            userScores[userName] = score;
            userCount[userName] = 1;
        } else {
            userScores[userName] += score;
            userCount[userName] += 1;
        }
    });

    // Calculate average and classify each user
    let userClassification = {};
    for (const userName in userScores) {
        const avgScore = userScores[userName] / userCount[userName];

        // Classify based on average sentiment score
        if (avgScore > 0.5) {
            userClassification[userName] = 'Positive';
        } else if (avgScore < 0) {
            userClassification[userName] = 'Negative';
        } else {
            userClassification[userName] = 'Neutral';
        }
    }

    // Count users in each category
    let categoryCount = {
        'Positive': 0,
        'Negative': 0,
        'Neutral': 0
    };

    for (const userName in userClassification) {
        const category = userClassification[userName];
        categoryCount[category]++;
    }

    // Calculate percentages for pie chart
    const totalUsers = Object.keys(userClassification).length;
    const labels_dict = {
        'Positive': Math.round((categoryCount['Positive'] / totalUsers) * 100) || 0,
        'Negative': Math.round((categoryCount['Negative'] / totalUsers) * 100) || 0,
        'Neutral': Math.round((categoryCount['Neutral'] / totalUsers) * 100) || 0
    };

    // Handle rounding errors to ensure total is 100%
    const total = labels_dict['Positive'] + labels_dict['Negative'] + labels_dict['Neutral'];
    if (total !== 100 && totalUsers > 0) {
        const diff = 100 - total;
        // Add the difference to the largest category
        let largestCategory = 'Neutral';
        if (labels_dict['Positive'] > labels_dict[largestCategory]) largestCategory = 'Positive';
        if (labels_dict['Negative'] > labels_dict[largestCategory]) largestCategory = 'Negative';
        labels_dict[largestCategory] += diff;
    }

    return labels_dict;
}

async function initializePieChart(duration) {
    try {
        const sentimentScore = await fetchSentimentData(duration);
        //console.log("Sentiment score:", sentimentScore);
        //Object.keys(labels_dict).forEach(key => labels_dict[key] = 0);

        let labels_dict = updateLabelDict(sentimentScore);
        //console.log('The pie button clicked!')
        let ctx = document.getElementById("myPieChart");
        let myPieChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: Object.keys(labels_dict),
                datasets: [{
                    data: Object.values(labels_dict),
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


    } catch (error) {
        console.error("Failed to initialize pie chart:", error.message);
    }
}

async function fetchSentimentData(duration) {
    try {
        const url = '/sentiment/fetch_bar_sentiment_data/';
        //console.log(`Fetching from URL: ${url}`);

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
            throw new Error(`Response Status: ${response.status}`);
        }

        const responseJson = await response.json();
        return responseJson;
    } catch (error) {
        console.error(`Error fetching sentiment score: ${error.message}`);
        throw error; // Re-throw to allow caller to handle it

    }
}

document.addEventListener('DOMContentLoaded', async function () {
    await initializePieChart('weekly')

    document.getElementById('weekly_admin_pie_button').addEventListener('click', async () => await initializePieChart('weekly'))
    document.getElementById('monthly_admin_pie_button').addEventListener('click', async () => await initializePieChart('monthly'))
    document.getElementById('all_time_admin_pie_button').addEventListener('click', async () => await initializePieChart('all_time'))
})

// Pie Chart Example
