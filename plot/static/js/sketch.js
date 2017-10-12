function loadJSON(callback) {

    var xobj = new XMLHttpRequest();
        xobj.overrideMimeType("application/json");
    xobj.open('GET', "json/data.json", true); // Replace 'my_data' with the path to your file
    xobj.onreadystatechange = function () {
          if (xobj.readyState == 4 && xobj.status == "200") {
            // Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
            callback(xobj.responseText);
          }
    };
    xobj.send(null);
 }
var actual_JSON = loadJSON(function(response) {
    actual_JSON = JSON.parse(response);
});

function setup() {
    createCanvas(1000, 1000);
    background(0);

    var json = actual_JSON;

    for (var key in json) {
        if (json.hasOwnProperty(key)) {
            var val = json[key];
            k = JSON.parse(key);

            fill(255, 0, 175, 150);
            noStroke();
            ellipse(k[0] * 1000, k[1] * 1000, 5, 5);

            for (var i = 0; i < val.length; i++) {
                var v = val[i];
                stroke(255);
                line(k[0] * 1000, k[1] * 1000, v[0] * 1000, v[1] * 1000);
            }
        }
    }
}

function draw() {
}