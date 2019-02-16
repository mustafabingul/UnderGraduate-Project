
var config = {};
config.widget = {};
config.widget.news = {};
config.widget.weather = {};
config.widget.exchange={};
config.widget.mail={};
config.web = {};

config.widget.weather.appid = 'cd36283f084c172cea971f6b1644b1b1';
config.widget.weather.url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&appid=' + config.widget.weather.appid;
config.widget.weather.lat='';
config.widget.weather.lon='';
config.widget.weather.refreshRateInMinutes = 10;
config.widget.news.url =  'http://www.cumhuriyet.com.tr/rss/1.xml';
config.widget.news.refreshRateInMinutes = 60;
/** Exchange */
config.widget.exchange.url='http://data.fixer.io/api/latest?access_key=f4ca30bfdae8c5f74223f5aab84af00d&symbols=EUR,USD,GBP,TRY,JPY';
config.widget.exchange.refreshRateInMinutes=240;
config.widget.exchange.symbols={EUR:"EURO",USD:"ABD DOLARI",GBP:'STERLİN',TRY:'TÜRK LİRASI',JPY:'JAPON YENİ'};

/**Mail */
config.widget.mail.refreshRateInMinutes=15;
config.widget.mail.authUrl='https://login.microsoftonline.com/common/oauth2/v2.0/authorize';
config.widget.mail.tokenUrl='https://login.microsoftonline.com/organizations/oauth2/v2.0/token';
config.widget.mail.redirectUrl='http://localhost:3000/auth';
config.widget.mail.code='';
config.widget.mail.access_token='';
config.widget.mail.refresh_token='';
config.widget.mail.client_id='b650ba2f-bf7f-48cd-94ec-fa6ce6d2807f';
config.widget.mail.client_secret='oqDKAP430?rapgeWZB68^*]';
config.widget.mail.scope='openid profile offline_access User.Read Mail.Read';
/**------------------------------ */
config.web.port = 3000;

module.exports = config;
