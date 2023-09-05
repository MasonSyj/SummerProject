document.addEventListener('DOMContentLoaded', function() {
    let previous_data = JSON.parse(localStorage.getItem('filter_chart_data4'))
    // let first_time = formatTime();
        let data = previous_data || {
        labels: [],
        // labels: ['1', '3', '3', '4', '5', '6'],
        datasets: [{
            label: 'dissolved_solids',
            backgroundColor: 'silver',
            borderColor: 'silver',
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
                max: 600,
                ticks: {
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

    var ctx = document.getElementById('lineChart4').getContext('2d');
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
        lineChart.data.datasets.forEach((dataset) => {
            dataset.data.push(dissolved_solids);
        });

        localStorage.setItem('filter_chart_data4', JSON.stringify(lineChart.data))
        lineChart.update();
    }, 2000);
});

