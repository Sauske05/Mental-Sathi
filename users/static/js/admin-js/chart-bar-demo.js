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
            return '' + Math.round(n * k) / k;
        };
    // Fix for IE parseFloat(0.55).toFixed(0) = 0;
    s = (prec ? toFixedFix(n, prec) : '' + Math.round(n)).split('.');
    if (s[0].length > 3) {
        s[0] = s[0].replace(/\B(?=(?:\d{3})+(?!\d))/g, sep);
    }
    if ((s[1] || '').length < prec) {
        s[1] = s[1] || '';
        s[1] += new Array(prec - s[1].length + 1).join('0');
    }
    return s.join(dec);
}

var ctx = document.getElementById("myBarChart");

let emotions = ["Happy", "Sad", "Angry", "Excited", "Calm", "Anxious"];
let emotions_dict = {
    "Happy": 0, "Sad": 0, "Angry": 0, "Excited": 0, "Calm": 0, "Anxious": 0
};

async function getSentimentData(duration) {
    try {
        // const user_email_response = await fetch('/get_session/', {
        //     method: "GET",
        // })
        // const user_email = await user_email_response.json()
        // console.log(`This is the email -> ${user_email.userEmail}`)
        const url = `http://127.0.0.1:8000/sentiment/fetch_bar_sentiment_data/`;

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


// Bar Chart Example
async function initializeDashboard(duration) {
    try {
        const sentimentData = await getSentimentData(duration)
        console.log(sentimentData)
        Object.keys(emotions_dict).forEach(key => emotions_dict[key] = 0);

        updateEmotionDict(sentimentData);
        console.log(emotions_dict)

        let frequencies = Object.values(emotions_dict);
        console.log(frequencies)
        var myBarChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: emotions,
                datasets: [{
                    label: "Emotion Frequency",
                    backgroundColor: "#4e73df",
                    hoverBackgroundColor: "#2e59d9",
                    borderColor: "#4e73df",
                    data: frequencies,
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
                            unit: 'day'
                        },
                        gridLines: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            maxTicksLimit: 6
                        },
                        maxBarThickness: 25,
                    }],
                    yAxes: [{
                        ticks: {
                            min: 0,
                            maxTicksLimit: 5,
                            padding: 10,
                            // Include a dollar sign in the ticks
                            callback: function (value, index, values) {
                                return number_format(value);
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
                    titleMarginBottom: 10,
                    titleFontColor: '#6e707e',
                    titleFontSize: 14,
                    backgroundColor: "rgb(255,255,255)",
                    bodyFontColor: "#858796",
                    borderColor: '#dddfeb',
                    borderWidth: 1,
                    xPadding: 15,
                    yPadding: 15,
                    displayColors: false,
                    caretPadding: 10,
                    callbacks: {
                        label: function (tooltipItem, chart) {
                            var datasetLabel = chart.datasets[tooltipItem.datasetIndex].label || '';
                            return datasetLabel + ': ' + number_format(tooltipItem.yLabel);
                        }
                    }
                },
            }
        });


    } catch (e) {
        console.log(e)
    }
}


document.addEventListener('DOMContentLoaded', async function () {
    await initializeDashboard('weekly');

    // document.getElementById('areaWeeklyButton').addEventListener('click', async () => await initializeDashboard('weekly'))
    // document.getElementById('areaMonthlyButton').addEventListener('click', async () => await initializeDashboard('monthly'))
    // document.getElementById('areaAllTimeButton').addEventListener('click', async () => await initializeDashboard('all_time'))

});

