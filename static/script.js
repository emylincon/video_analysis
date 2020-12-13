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

var advert_count = 20;

function pad(n, width, z) {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

const predicted = document.querySelector('#predicted');
const room = document.querySelector('#room');

function update_predicted(no){
    if(no === 1){
        predicted.classList.add('lit-text');
        predicted.classList.remove('not-lit');
        room.classList.add('not-lit');
        room.classList.remove('lit-text');
    }
    else{
        predicted.classList.remove('lit-text');
        predicted.classList.add('not-lit');
        room.classList.remove('not-lit');
        room.classList.add('lit-text');
    }
}

async function update_advert(){
    const res = await fetch('/get_advert');
    const advert = await res.json();
    update_predicted(advert.is_predicted);
    disappear();
    setTimeout(function (){
        appear(advert.advert);
    }, 1000);
}

function advert_counter(){
    let counter = document.querySelector('#counter');
    advert_count -= 1;
    counter.innerHTML = pad(advert_count, 2);
    if(advert_count === 0){
        update_advert();
        advert_count = 20;
    }
}

function disappear(){
    let nodes = document.querySelectorAll('.pod');
    for(let i = 0; i<nodes.length; i++){
        nodes[i].classList.add('disappear');
    }

    setTimeout(function(){
        for(let i = 0; i<nodes.length; i++){
            nodes[i].remove();
        }
        let group_node = document.querySelectorAll('.group-pod');
        group_node[0].remove();
        group_node[1].remove();
    }, 1000)
}

function create_pod(age, gender, item, image, percent){
    let sex = {'male': '<i class="fas fa-male" style="color: rgb(66, 66, 228);"></i>', 'female': '<i class="fas fa-female" style="color: rgb(228, 66, 206);"></i>'}
    let node = document.createElement('div');
    node.classList.add('pod');
    node.classList.add('pod_image_create');
    node.innerHTML = `
    <div class="pod-in">
    <br>
    <div class="text1">${percent}% ${sex[gender]}</div>
    <div class="text3">Aged ${age}</div>
    <div class="text2">are likely to purchase</div>
    <div class="text3">${item}</div>
</div>
    `;
    node.style.backgroundImage = `url('${image}')`;
    console.log(node.style.backgroundImage);
    return node;
}

function create_group_pod(){
    let group_node = [];
    for(let i=0; i<2; i++){
        let node = document.createElement('div');
        node.classList.add('group-pod');
        group_node.push(node);
    }
    return group_node;
}

function appear(data){
    let main_pod = document.querySelector('.main-pod');
    let group_node = create_group_pod();

    let alt = 0;
    for(let i=0; i< 4; i++){
        group_node[alt].appendChild(create_pod(age=data[i].age, gender=data[i].gender,
            item=data[i].item, image=data[i].image, percent=data[i].percent));
        alt = alt^1;
    }
    for(let i=0; i<2; i++){
        main_pod.appendChild(group_node[i]);
    }
}

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
    advert_counter();
}

setInterval(update, 1000);