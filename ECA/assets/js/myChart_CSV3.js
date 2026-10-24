var ctx = document.getElementById('myChart').getContext('2d');

$.ajax({
  url:"/chart3",
  type:"POST",
  data: {},
  error: function() {
      alert("Error");
  },

  success: function(data, status, xhr) {

    debugger

    var averages = data.averages;

    // averages is like {name1: 123, name2: 234}

    var vLabels = [];
    var vData = [];

    // The chart handled here is more straightforward
    // xAxis is specified by vLabels as a list e.g. [name1, name2, ...]
    // yAxis is specified by vData as a list, corresponding to labels, e.g., [123, 234, ...]

    for (const [key, values] of Object.entries(averages)) {
      vLabels.push(key);
      vData.push(values);
    } 

    var myChart = new Chart(ctx, {
      data: {
      labels: vLabels,
      datasets: []
      },
      options: {
          responsive: false
      }
    });

    debugger
    myChart.data.datasets.push({
    label: "Average",
    type: "bar",
    borderColor: '#'+(0x1ff0000+Math.random()*0xffffff).toString(16).substr(1,6),
    borderColor: '#'+(0x1100000+Math.random()*0xffffff).toString(16).substr(1,6),
    backgroundColor: "rgba(249, 238, 236, 0.74)",
    data: vData,
    spanGaps: true
    });
    myChart.update();
    }

})
