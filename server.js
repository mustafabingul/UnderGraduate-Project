var express = require('express');
var config = require('./conf');
var app = express();
var http = require('http').Server(app);

app.use(express.static('./interface'));

app.get('/', function (req, res) {
  res.sendFile(__dirname + '/interface/home.html');
});

var applications = require('./apps');
app.get('/weather', applications.weather);
app.get('/news', applications.news);
app.get('/exchange',applications.exchange);
app.get('/mail',applications.mail);
app.get('/auth',applications.auth);

// Forwarding between motion server and client
require('./move')(app, http);

http.listen(config.web.port, function () {
  console.log('Server listening on port %d', config.web.port);
});