
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
async function intializePieChart(duration) {
       let sentiment_map = {
        'Happy' : 0,
        'Sad' : 0,
        'Neutral' : 0,
    }
    const sentiment_data = await getSentimentScore(duration);
    //const sentiment_data_monthly = await getSentimentScore('monthly')
    //console.log(`This is the final weekly sentiment data : ${sentiment_data_weekly}`)
    //console.log(`This is the final monthly sentiment data : ${sentiment_data_monthly}`)


    sentiment_data.forEach(

        item => {
            const sentimentScore = item[0]
            //console.log(`This is the sentiment score: ${sentimentScore}`)
            if (sentimentScore > 0.3) {
                sentiment_map['Happy'] +=1
            }
            else if (sentimentScore < 0.3 && sentimentScore > 0){
                sentiment_map['Neutral'] +=1
            }
            else {
                sentiment_map['Sad'] +=1
            }
        }
    )
let ctx = document.getElementById("myPieChart");
let myPieChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
        labels: Object.keys(sentiment_map),
        datasets: [{
            data: Object.values(sentiment_map),
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

}


document.addEventListener('DOMContentLoaded', async function () {
    await intializePieChart('weekly')

    document.getElementById('pieChartWeeklyButton').addEventListener('click', async () => await intializePieChart('weekly'))

    document.getElementById('pieChartMontlyButton').addEventListener('click', async () => await intializePieChart('monthly'))
})