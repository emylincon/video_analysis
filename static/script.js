const start = new Date("Nov 19, 2020 12:00:00").getTime();
Chart.defaults.global.defaultFontColor = 'white';

var ctx = document.getElementById('gender').getContext('2d');
var myGender = new Chart(ctx, {
    type: 'horizontalBar',
    data: {
        labels: ['Male', 'Female'],
        datasets: [{
            label: '# of Gender Detected',
            data: [1,1],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                },

            }],
            xAxes: [{
                gridLines: {
                    display: true,
                    color: 'rgb(211,211,211, 0.16)'
                  }
            }]
        }
    }
});

var ctx1 = document.getElementById('age').getContext('2d');
var myAge = new Chart(ctx1, {
    type: 'bar',
    data: {
        labels: ['Infant', 'Baby', 'Child', 'Teen', 'Young', 'Adult', 'Middle', 'Senior'],
        datasets: [{
            label: '# of Age Group Detected',
            data: [1, 1, 1, 2, 1, 1, 1, 1],
            backgroundColor: [
                'rgba(255, 99, 132, 0.2)',
                'rgba(54, 162, 235, 0.2)',
                'rgba(255, 206, 86, 0.2)',
                'rgba(75, 192, 192, 0.2)',
                'rgba(153, 102, 255, 0.2)',
                'rgba(255, 159, 64, 0.2)',
                'rgba(77, 131, 137, 0.2)',
                'rgba(248, 228, 13, 0.2)'
            ],
            borderColor: [
                'rgba(255, 99, 132, 1)',
                'rgba(54, 162, 235, 1)',
                'rgba(255, 206, 86, 1)',
                'rgba(75, 192, 192, 1)',
                'rgba(153, 102, 255, 1)',
                'rgba(255, 159, 64, 1)',
                'rgba(255, 255, 255, 1)',
                'rgba(248, 228, 13, 1)'
            ],
            borderWidth: 1
        }]
    },
    options: {
        scales: {
            yAxes: [{
                ticks: {
                    beginAtZero: true
                },
                gridLines: {
                    display: true,
                    color: 'rgb(211,211,211, 0.16)'
                  }
            }]
        }
    }
});

function timeCount(){
    var now = new Date().getTime();
    var myCount =  now - start;
    var days = Math.floor(myCount / (1000 * 60 * 60 * 24));
    var hours = Math.floor((myCount  % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    var minutes = Math.floor((myCount  % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.floor((myCount  % (1000 * 60)) / 1000);

    document.getElementById("time").innerHTML = "<span style='color:#0088a9;'>RUNTIME</span><br><span>" + days + "d " + hours + "h "
  + minutes + "m " + seconds + "s </span>";
}

async function update_stat(){
    const response = await fetch('/get_stat');
    const data = await response.json();
    myAge.data.datasets[0].data = data.age;
    myGender.data.datasets[0].data = data.gender;
    let node = document.querySelector('#p-no');
    node.innerHTML = `${data.faces} Faces`;
}

function update(){
    timeCount();
    update_stat();
    myAge.update();
    myGender.update();
}

setInterval(update, 1000);