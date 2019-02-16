var config = require('./conf');
var fs = require('fs');
var request = require('request');
var url = require('url');
var socketClient = null;
var socketIO = null;

module.exports = function (app, http) {
	socketIO = require('socket.io')(http);

	// Web Socket IO for sending gestures to client
	socketIO.of('/movement').on('connection', function(socket){
		socketClient = socket;
	});

	app.get('/movement/gestures', function (req, res) {
		try {
			console.log(req.query.params);
			socketClient.emit('gestures', req.query.params);
		}  catch(e) {console.log("Bir hata oluştu: movement get.");
		console.log("E>>> "+e);}
		res.sendStatus(200);
	});
}