document.addEventListener('DOMContentLoaded', function() {
    let previous_data = JSON.parse(localStorage.getItem('dis_chart_data'))
    let first_time = formatTime();
    let data = previous_data || {
        labels: [],
        datasets: [{
            label: 'water_level',
            backgroundColor: 'blue',
            borderColor: 'blue',
            borderWidth: 2,
            data: [],
        }]
    };

    var options = {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            y: {
                min: 0,
                max: 100,
                ticks: {
                    stepSize: 1,
                    callback: function(value) {
                        return value.toFixed(0);
                    }},
                beginAtZero: true
            }
        },

        plugins: {
            tooltip: {
            mode: 'nearest',
            intersect: false,
            callbacks: {
                label: function(context) {
                    var label = context.dataset.label || '';
                    if (label) {
                        label += ': ';
                    }

                    if (context.parsed.y !== null) {
                        label += context.parsed.y.toFixed(2); // Display last value with 2 decimal places
                    }

                    return label;
                    }
                }
            }
        }
    };

    var ctx = document.getElementById('lineChart1').getContext('2d');
    var lineChart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });


    setInterval(function() {
        var length = lineChart.data.labels.length;

        if (length >= 10) {
            lineChart.data.labels.shift();
            lineChart.data.datasets.forEach((dataset) => {
                dataset.data.shift();
            });
            length--;
        }

        var current_time = formatTime();
        lineChart.data.labels.push(current_time);
        lineChart.data.datasets[0].data.push(water_level)

        localStorage.setItem('dis_chart_data', JSON.stringify(lineChart.data))
        lineChart.update();
    }, 2000);
});

