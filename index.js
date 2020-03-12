var http = require('http');
var express = require('express');
var app = express();
var fs = require('fs');


var path = __dirname;
var file;

app.use(express.static(__dirname));


var server = app.listen(8080, function () {

});

fs.readdir(path, function(err, items) {
	console.log(items);

	for (var i = 0; i < items.length; i++) {
		var idx = items[i].length - 4;
		var suffix = items[i].substr(idx);
		if (suffix == 'html') {
			// then serve the file
			file = items[i];
		}
		console.log(items[i]);
	}

});

app.get('/', function(req, res) {
	fs.readdir(path, function(err, items) {
	console.log(items);

	for (var i = 0; i < items.length; i++) {
		var idx = items[i].length - 4;
		var suffix = items[i].substr(idx);
		if (suffix == 'html') {
			// then serve the file
			file = items[i];
		}
		console.log(items[i]);
	}

	});


	res.sendFile(__dirname + '/' + file);
});

