var request = require('request');
var cheerio = require('cheerio');
var config = require('./conf');
var url = require('url');

var news = [];
var refreshNews = function() {
	console.log("News Fonksiyonu Başladı.");
	request(config.widget.news.url, function (error, response, xml) {

		if (error || response.statusCode !== 200){
			console.log("Newsde Hata Oluştu.");return;
		}
		var parseString = require('xml2js').parseString;
		parseString(xml, function (err, result) {
			items = result.rss.channel[0].item;
			items.forEach(function(item) {
					var entry_news = new Object();
					entry_news.title = item.title;
					entry_news.description = item.description;
					//entry_news.description = item.description.replace("/<img[^>]+src\\s*=\\s*['\"]([^'\"]+)['\"][^>]*>/gi"," ");
					entry_news.category = item.category;
					entry_news.img = item.enclosure[0]['$']['url'];
					news.push(entry_news);

			});
		});
	console.log('News Fonksiyonu Bitti.');
	});
}
setInterval(refreshNews, 1000 * 60 * config.widget.news.refreshRateInMinutes);
refreshNews();

module.exports.news = function (req, res) {
	res.send(JSON.stringify(news));
}

var weather = {};
var refreshWeather = function() {
	if(config.widget.weather.lat!='' && config.widget.weather.lon!='' && config.widget.weather.lat!==undefined && config.widget.weather.lon!==undefined){
		var url=config.widget.weather.url+'&lat='+config.widget.weather.lat+'&lon='+config.widget.weather.lon;
		request({url: url, json: true}, function (error, response, body) {
			if (!error && response.statusCode === 200) {
				weather = response;
			}else{
				console.log('Weather Bilgisi Alınamadı. Bir Hata Oluştu');
			}
		});
	}else{
		console.log('Weather Konum Bilgisi Bulunamadı.');
	}
}
setInterval(refreshWeather, 1000 * 60 * config.widget.weather.refreshRateInMinutes);
refreshWeather();

module.exports.weather = function (req, res) {
	var query=url.parse(req.url, true).query;
	if(config.widget.weather.lat=='' && config.widget.weather.lon==''){
		if(query.lat!='' && query.lon!='' && query.lat!=undefined && query.lon!=undefined){
			config.widget.weather.lat=query.lat;
			config.widget.weather.lon=query.lon;
			refreshWeather();
		}
	}
	res.send(weather);
}

var exchange=[];
var refreshExchange=function(){
	console.log("Exchange Fonksiyonu Başladı.");
	request({url:config.widget.exchange.url,json:true},function (error, response, json) {

		if (error || response.statusCode !== 200){
			console.log("Exchange Hata Oluştu.");return;
		}
		if(json.success){
			for(var i in json.rates){
				if(i!='TRY'){
					var currency=new Object();
					currency.name=config.widget.exchange.symbols[i];
					currency.value=parseFloat(json.rates.TRY/json.rates[i]).toFixed(3)
					exchange.push(currency);
				}
			}
		}
		console.log('Exchange Fonksiyonu Bitti.');
	});
}
setInterval(refreshExchange, 1000 * 60 * config.widget.exchange.refreshRateInMinutes);
refreshExchange();
module.exports.exchange = function (req, res) {
	res.send(JSON.stringify(exchange));
}



/** GET MAiL With Api  */
var mails=[];
var refreshMail=function(){
	if(config.widget.mail.access_token!=''){
		var options = { method: 'GET',
				url: 'https://graph.microsoft.com/v1.0/me/MailFolders/Inbox/messages',
				json:true,
				headers: 
				{ 
					Authorization: 'Bearer '+config.widget.mail.access_token,
					'Content-Type': 'application/x-www-form-urlencoded' 
				}
			};

		request(options, function (error, response, body) {
			if (error) return;
			mails=[];
			if(body.value!=undefined){
                body.value.forEach(data => {
                    var mail=new Object();
                    mail.sender={};
                    mail.sender.name=data.sender.emailAddress.name;
                    mail.sender.email=data.sender.emailAddress.address;
                    mail.subject=data.subject;
                    mail.body=data.bodyPreview;
                    mails.push(mail);
                });
			}
			console.log('Mailler Çekildi.');
		});
	}else{
		console.log('Access Token Yok O yüzden çalışmadı.');
	}
	
}
refreshMail();
module.exports.mail = function (req, res) {
	res.send(JSON.stringify(mails));
}


/* Mail Auth Set Token */

var getToken=function(param) {
	var form={ 
		client_id: config.widget.mail.client_id,
		scope: config.widget.mail.scope,
		redirect_uri: config.widget.mail.redirectUrl,
		client_secret: config.widget.mail.client_secret,
		'Content-Type': 'application/x-www-form-urlencoded' 
	};
	if(param){
		form.code=config.widget.mail.code;
		form.grant_type='authorization_code';
		
	}else{
		if(config.widget.mail.refresh_token!=''){
			form.refresh_token=config.widget.mail.refresh_token;
			form.grant_type='refresh_token';
			console.log('Refresh Token Çalışıyor.');
		}
	}
	var options = { method: 'POST',url: config.widget.mail.tokenUrl,json:true,form:form};
	request(options, function (error, response, json) {
		if (error) return;
		
	
		if(json.access_token!='' && json.access_token!=='undefined'){
			config.widget.mail.access_token=json.access_token;
			config.widget.mail.refresh_token=json.refresh_token;
			console.log('Token Alındı.');
			console.log('-------------------');
			refreshMail();
		}
	});
} 
setInterval(getToken, 1000 * 60 * config.widget.mail.refreshRateInMinutes);
module.exports.auth = function (req, res) {
	var query=url.parse(req.url, true).query;
	if(query.code=='' || query.code===undefined){
		var redirect_uri=config.widget.mail.redirectUrl;
		/*if(req.rawHeaders[1]!=''){
			redirect_uri=req.rawHeaders[1];
		}*/
		console.log(redirect_uri);
		res.redirect(config.widget.mail.authUrl+'?scope='+config.widget.mail.scope+'&redirect_uri='+redirect_uri+'&client_id='+config.widget.mail.client_id+'&response_type=code');
	}else{
		config.widget.mail.code=query.code;
		getToken(true);
		res.send(JSON.stringify({'success':true}));
	}
	
}