// Set new default font family and font color to mimic Bootstrap's default styling
Chart.defaults.global.defaultFontFamily = 'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif';
Chart.defaults.global.defaultFontColor = '#858796';

function number_format(number, decimals, dec_point, thousands_sep) {
    // *     example: number_format(1234.56, 2, ',', ' ');
    // *     return: '1 234,56'
    number = (number + '').replace(',', '').replace(' ', '');
    var n = !isFinite(+number) ? 0 : +number,
        prec = !isFinite(+decimals) ? 0 : Math.abs(decimals),
        sep = (typeof thousands_sep === 'undefined') ? ',' : thousands_sep,
        dec = (typeof dec_point === 'undefined') ? '.' : dec_point,
        s = '',
        toFixedFix = function (n, prec) {
            var k = Math.pow(10, prec);
            return '' + (n * k) / k;
        };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + (n)).split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

async function getSentimentScore(duration) {

    try {
        // const user_email_fetch = await fetch('/get_session/', {
        //     method: 'GET'
        // })
        //
        // user_email = user_email_fetch.json()

        const url = '/sentiment/fetch_sentimentScore/';

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(
                {
                    'duration': duration,
                    'type': 'all_users'
                }
            )
        })

        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const json = await response.json()
        console.log(`This is the json data ${json}`)
        return json;


    } catch (e) {
        console.log(e)
        return null
    }
}

async function initializeAreaChart(duration) {
    const sentiment_data = await getSentimentScore(duration);
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

// Initialize sentiment scores for all days to 0
    let sentimentByDay = {
        "Sunday": 0,
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0
    };

// Populate sentiment scores from data
    sentiment_data.forEach(item => {
        const sentimentScore = item[0];
        const date = new Date(item[1]);
        const dayOfWeek = date.getDay();
        const dayName = dayNames[dayOfWeek];

        sentimentByDay[dayName] += sentimentScore;
    });

    //console.log(sentiment_data);
    //console.log(`This is the sentiment score ${sentimentByDay}`);

// Get current day and reorder days to show last 7 days ending with today
    const today = new Date();
    const currentDayIndex = today.getDay(); // 0 = Sunday, 1 = Monday, etc.

// Create a reordered array of days starting from 7 days ago and ending with today
    let reorderedDays = [];
    for (let i = 0; i < 7; i++) {
        // Calculate the day index (0-6) going back from current day
        // We add 7 before modulo to ensure we get a positive number
        const dayIndex = (currentDayIndex - 6 + i + 7) % 7;
        reorderedDays.push(dayNames[dayIndex]);
    }

// Create corresponding array of sentiment values in the same order
    const reorderedSentimentData = reorderedDays.map(day => sentimentByDay[day]);


    // Area Chart Example
    var ctx = document.getElementById("myAreaChart");

    //console.log('Area Chart buttons trigerred!')
    var myLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: reorderedDays,
            datasets: [{
                label: "Score",
                lineTension: 0.3,
                backgroundColor: "rgba(78, 115, 223, 0.05)",
                borderColor: "rgba(78, 115, 223, 1)",
                pointRadius: 3,
                pointBackgroundColor: "rgba(78, 115, 223, 1)",
                pointBorderColor: "rgba(78, 115, 223, 1)",
                pointHoverRadius: 3,
                pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                pointHitRadius: 10,
                pointBorderWidth: 2,
                data: reorderedSentimentData,
            }],
        },
        options: {
            maintainAspectRatio: false,
            layout: {
                padding: {
                    left: 10,
                    right: 25,
                    top: 25,
                    bottom: 0
                }
            },
            scales: {
                xAxes: [{
                    time: {
                        unit: 'date'
                    },
                    gridLines: {
                        display: false,
                        drawBorder: false
                    },
                    ticks: {
                        maxTicksLimit: 7
                    }
                }],
                yAxes: [{
                    ticks: {
                        maxTicksLimit: 5,
                        padding: 10,
                        // Include a dollar sign in the ticks
                        callback: function (value, index, values) {
                            //return number_format(value);
                            return value
                        }
                    },
                    gridLines: {
                        color: "rgb(234, 236, 244)",
                        zeroLineColor: "rgb(234, 236, 244)",
                        drawBorder: false,
                        borderDash: [2],
                        zeroLineBorderDash: [2]
                    }
                }],
            },
            legend: {
                display: false
            },
            tooltips: {
                backgroundColor: "rgb(255,255,255)",
                bodyFontColor: "#858796",
                titleMarginBottom: 10,
                titleFontColor: '#6e707e',
                titleFontSize: 14,
                borderColor: '#dddfeb',
                borderWidth: 1,
                xPadding: 15,
                yPadding: 15,
                displayColors: false,
                intersect: false,
                mode: 'index',
                caretPadding: 10,
                callbacks: {
                    label: function (tooltipItem, chart) {
                        var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                        return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
                    }
                }
            }
        }
    });

}

document.addEventListener('DOMContentLoaded', async function () {
    await initializeAreaChart('weekly')

    document.getElementById('all_time_area_chart_button').addEventListener('click', async () => await initializeAreaChart('all_time'))

    document.getElementById('monthly_area_chart_button').addEventListener('click', async () => await initializeAreaChart('monthly'))
    document.getElementById('weekly_area_chart_button').addEventListener('click', async () => await initializeAreaChart('weekly'))
})

