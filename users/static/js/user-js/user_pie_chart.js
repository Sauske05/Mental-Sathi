
async function getSentimentScore(duration) {
    try {
        const user_email_fetch = await fetch('/get_session/', {
            method: 'GET'
        });

        let user_email = await user_email_fetch.json()
        const url = '/sentiment/fetch_sentimentScore/'

        const response = await fetch(url, {
            method : "POST",
            body :
            JSON.stringify({'duration' : duration,
            headers : {
                'Content-Type' : 'application/json'
            }
        })
    })
    console.log(response)
     if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const json = await response.json()
        console.log(`This is the json data ${json}`)
        return json;
    } catch (Exception) {
        console.log(Exception);
        return null;
    }

}

document.addEventListener('DOMContentLoaded', async function () {
// Pie Chart Example
    const sentiment_data_weekly = await getSentimentScore('weekly');
    const sentiment_data_monthly = await getSentimentScore('monthly')
    console.log(`This is the final weekly sentiment data : ${sentiment_data_weekly}`)
    console.log(`This is the final monthly sentiment data : ${sentiment_data_monthly}`)

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


})