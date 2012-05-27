#!env node

var fs = require ('fs'),
    path = require ('path'),
    express = require ('express'),
    app = express.createServer();

var fetchData = function () {
    var data = fs.readFileSync (process.env.HOME + '/.simple-monitoring/logs/uptimelog', 'ascii');
    var lines = data.split ("\n");
    var r = [];

    for (l in lines) {
        var v = lines [l].split (" "),
            s = v.length,
            v1 = v[s -3],
            v5 = v[s -2],
            v15 = v[s -1];
        r.push ([v1,v5,v15]);
    }

    return r;
}
app.configure(function(){

    // disable layout
    app.set("view options", {layout: false});

    // make a custom html template
    app.register('.html', {
        compile: function(str, options){
            return function(locals){
                return str;
            };
        }
    });

    app.use("/js", express.static(__dirname + '/js'));
});

app.get ('/', function (req, res) {
    res.render ('reporting.html');
});

app.get ('/uptime', function (req, res) {
    res.send (fetchData());
});


app.listen (7777);
