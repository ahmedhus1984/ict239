var ctx = document.getElementById('myChart').getContext('2d');

//Read the data
var f = "static/js/DataSet1.2.csv";
// var f = "./Data35.csv";


d3.csv(f,
  // When reading the csv, I must format variables:
  function(d){
    return { group : d.User, value : d.BMI, date: d.Date, num: d.Num }
  },
  // Now I can use this dataset:
  function(data) {

  debugger

  // from an Array of Objects, each one like the folloiwng
  // { group : user_1, value : 666, date: datetime_1, num: 2 }
  // transform into 
  // var vLabels = []; 
  // // ['usr_1', 'usr_2', ...] 
  // var vData = [];
  // // [ [{'x': datetime_1, 'y':666}, {'x': datetime_2, 'y':1200}], ...]

  var vLabels = []; 
  var vData = []

  // But first turn it into the following:
  var sumData = {}
  // {'usr_1': [{'x': datetime_1, 'y':666}, {'x': datetime_2, 'y':1200}],
  //    'usr_2: [{'x': datetime_1, 'y':656}, {'x': datetime_2, 'y':1100}],
  //    ...}

  for (let x = 0; x < data.length; x++) { // data is an array of dictionary
    let obj = sumData[data[x].group] || ""; // like dit.get[key] in python
    if (obj === "") {
      sumData[data[x].group]=[{'x': data[x].date, 'y':data[x].value}];
    } else {
      obj.push({'x': data[x].date, 'y':data[x].value});
    }
  }

  // Then to the final format as specificed above
  for (const [key, values] of Object.entries(sumData)) {
    vLabels.push(key);
    vData.push(values)
  }

  debugger

  var myChart = new Chart(ctx, {
    data: {
    // labels: xLabels,
    datasets: []
    },
    options: {
      responsive: true,
      maintainaspectratio: false,
      scales: {
        x: {
          type: 'time',
          time: {
            parser: 'yyyy-MM-dd',
          },
          scaleLabel: {
            display: true,
            labelString: 'Date'
          }
        },
        y: {
          scaleLabel: {
            display: true,
            labelString: 'value'
          }
        }
      }
    }
  });

    debugger
    for (i= 0; i < vLabels.length; i++ ) {
      myChart.data.datasets.push({
      label: vLabels[i],
      type: "line",
      // borderColor: '#'+(0x1ff0000+Math.random()*0xffffff).toString(16).substr(1,6),
      borderColor: '#'+(0x1100000+Math.random()*0xffffff).toString(16).substr(1,6),
      backgroundColor: "rgba(249, 238, 236, 0.74)",
      data: vData[i],
      spanGaps: true
      });
      myChart.update();
    }

})
