        var max_ver = [];
        var min_ver = [];

        document.getElementById("animate").checked = !!animate;

        if (plot_option[0] === 0){
            document.getElementById("showEdgeCheck").checked = true;
            $("#myContainer2").css("display", "block");
        }
        else{
            document.getElementById("showEdgeCheck").checked = false;
            $("#myContainer2").css("display", "none");
        }

        if (plot_option[1] === 1){
            document.getElementById("minMaxCheck").checked = true;
            $("#myContainer3").css("display", "block");
        }
        else {
            document.getElementById("minMaxCheck").checked = false;
            $("#myContainer3").css("display", "none");
        }

        document.getElementById("topology").value = topology;

        function drawEdge() {
            if (document.getElementById("showEdgeCheck").checked) {
                $("#myContainer2").css("display", "block");
            }
            else {
                $("#myContainer2").css("display", "none");
            }
        }

        function drawMinMax() {
            if (document.getElementById("minMaxCheck").checked){
                $("#myContainer3").css("display", "block");
            }
            else {
                $("#myContainer3").css("display", "none");
            }
        }
        /*
        function setup(){
            createCanvas(600, 600, WEBGL);
            background(0);

            if(topology === "circle"){
                p.background(180);
                p.fill(0);
                p.ellipse(p.width/2, p.width/2, p.height, p.height);
            }

            for (var key in json) {
                if (json.hasOwnProperty(key)) {
                    var val = json[key];

                    fill(255, 200, 0);
                    noStroke();
                    ellipsoid((val[0])[0] * offset, (val[0])[1] * offset, point_size, point_size);

                    for (var i = 0; i < max_vertex.length; i++){
                        if (val[0][0] === max_vertex[i][0] && val[0][1] === max_vertex[i][1]){
                            max_ver.push(val);
                        }
                    }

                    for (var i = 0; i < min_vertex.length; i++){
                        if (val[0][0] === min_vertex[i][0] && val[0][1] === min_vertex[i][1]){
                            min_ver.push(val);
                        }
                    }
                }
            }
        }
        */

        var c_back = function( p ) {
            var lowerBound = 0;

            p.setup = function() {
                p.createCanvas(600, 600);
                p.background(0);
                p.frameRate(60);

                if(topology === "circle"){
                    p.background(180);
                    p.fill(0);
                    p.ellipse(p.width/2, p.width/2, p.height, p.height);
                }

                p.fill(255, 200, 0);
                p.noStroke();

                if(!animate) {
                    for (var key in json) {
                        if (json.hasOwnProperty(key)) {
                            var val = json[key];

                            p.ellipse((val[0])[0] * offset, (val[0])[1] * offset, point_size, point_size);

                            for (var i = 0; i < max_vertex.length; i++) {
                                if (val[0][0] === max_vertex[i][0] && val[0][1] === max_vertex[i][1]) {
                                    max_ver.push(val);
                                }
                            }

                            for (var i = 0; i < min_vertex.length; i++) {
                                if (val[0][0] === min_vertex[i][0] && val[0][1] === min_vertex[i][1]) {
                                    min_ver.push(val);
                                }
                            }
                        }
                    }
                }
            };
            p.draw = function () {
                if(animate) {
                    if (lowerBound < cellCount) {
                        var cell = lowerBound;
                        if (cells.hasOwnProperty(cell)) {
                            for (var m = 0; m < cells[cell].length; m++) {
                                var xComp = cells[cell][m][0];
                                var yComp = cells[cell][m][1];
                                xComp = (xComp < 0.0001) ? xComp.toExponential().toString().replace("-", "-0") : xComp;
                                yComp = (yComp < 0.0001) ? yComp.toExponential().toString().replace("-", "-0") : yComp;

                                var val = json[pointMap["[" + xComp + ", " + yComp + "]"]];
                                p.ellipse((val[0])[0] * offset, (val[0])[1] * offset, point_size, point_size);

                                for (var i = 0; i < max_vertex.length; i++) {
                                    if (val[0][0] === max_vertex[i][0] && val[0][1] === max_vertex[i][1]) {
                                        max_ver.push(val);
                                    }
                                }

                                for (var i = 0; i < min_vertex.length; i++) {
                                    if (val[0][0] === min_vertex[i][0] && val[0][1] === min_vertex[i][1]) {
                                        min_ver.push(val);
                                    }
                                }
                            }
                        }
                        lowerBound++;
                    }
                }
            };
        };
        var canvasBackground = new p5(c_back, 'myContainer1');

        var c_edges = function( p ) {
            var lowerBound = 0;
            var c = 0;
            p.setup = function() {
                p.createCanvas(600, 600);
                p.background(0, 0, 0, 0);

                p.stroke(255, 255, 255, 75);
                p.strokeWeight(0.5);

                if(!animate) {
                    for (var key in json) {
                        if (json.hasOwnProperty(key)) {
                            var val = json[key];

                            for (var i = 1; i < val.length; i++) {
                                var v = val[i];
                                p.line((val[0])[0] * offset, (val[0])[1] * offset, (json[v][0])[0] * offset, (json[v][0])[1] * offset);
                            }
                        }
                    }
                }
            };
            p.draw = function () {
                if(animate) {
                    if (lowerBound < cellCount) {
                        var cell = lowerBound;
                        if (cells.hasOwnProperty(cell)) {
                            for (var m = 0; m < cells[cell].length; m++) {
                                var xComp = cells[cell][m][0];
                                var yComp = cells[cell][m][1];
                                xComp = (xComp < 0.0001) ? xComp.toExponential().toString().replace("-", "-0") : xComp;
                                yComp = (yComp < 0.0001) ? yComp.toExponential().toString().replace("-", "-0") : yComp;

                                var val = json[pointMap["[" + xComp + ", " + yComp + "]"]];
                                for (var i = 1; i < val.length; i++) {
                                    var v = val[i];
                                    p.line((val[0])[0] * offset, (val[0])[1] * offset, (json[v][0])[0] * offset, (json[v][0])[1] * offset);
                                }
                            }
                        }
                        lowerBound++;
                    }
                }
            };
        };
        var canvasEdges = new p5(c_edges, 'myContainer2');

        var c_min_max = function( p ) {
            var drawFlagMax = true;
            var drawFlagMin = true;
            p.setup = function() {
                p.createCanvas(600, 600);
                p.background(0,0,0,0);
                p.strokeWeight(1);

                if(!animate) {
                    p.fill(255, 0, 0, 255);
                    p.stroke(255, 0, 0);

                    max_ver.forEach(function (element) {
                        for (var i = 1; i < element.length; i++) {
                            var v = element[i];

                            p.line((element[0])[0] * offset, (element[0])[1] * offset, (json[v][0])[0] * offset, (json[v][0])[1] * offset);
                            p.ellipse((element[0])[0] * offset, (element[0])[1] * offset, point_size, point_size);
                        }
                    });

                    p.fill(0, 0, 255, 255);
                    p.stroke(0, 0, 255);

                    min_ver.forEach(function (element) {
                        if (element.length === 1) {
                            p.ellipse((element[0])[0] * offset, (element[0])[1] * offset, point_size, point_size);
                            return;
                        }
                        for (var i = 1; i < element.length; i++) {
                            var v = element[i];
                            p.line((element[0])[0] * offset, (element[0])[1] * offset, (json[v][0])[0] * offset, (json[v][0])[1] * offset);
                            p.ellipse((element[0])[0] * offset, (element[0])[1] * offset, point_size, point_size);
                        }
                    });
                }
            };
            p.draw = function () {
                if(animate) {
                    if (drawFlagMin) {
                        p.fill(0, 0, 255, 255);
                        p.stroke(0, 0, 255, 100);

                        min_ver.forEach(function (element) {
                            if (element.length === 1) {
                                p.ellipse((element[0])[0] * offset, (element[0])[1] * offset, point_size, point_size);
                                return;
                            }
                            for (var i = 1; i < element.length; i++) {
                                var v = element[i];
                                p.line((element[0])[0] * offset, (element[0])[1] * offset, (json[v][0])[0] * offset, (json[v][0])[1] * offset);
                                p.ellipse((element[0])[0] * offset, (element[0])[1] * offset, point_size, point_size);
                            }
                            drawFlagMin = false;
                        });
                    }
                    if (drawFlagMax) {
                        p.fill(255, 0, 0, 255);
                        p.stroke(255, 0, 0, 200);

                        max_ver.forEach(function (element) {
                            for (var i = 1; i < element.length; i++) {
                                var v = element[i];

                                p.line((element[0])[0] * offset, (element[0])[1] * offset, (json[v][0])[0] * offset, (json[v][0])[1] * offset);
                                p.ellipse((element[0])[0] * offset, (element[0])[1] * offset, point_size, point_size);
                            }
                            drawFlagMax = false;
                        });
                    }
                }
            };
        };
        var canvasMinMax = new p5(c_min_max, 'myContainer3');