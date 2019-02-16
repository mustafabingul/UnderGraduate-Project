var server;

$(document).ready(function() {
    /*server = new WebSocket("ws://localhost:7777/");
    server.onmessage = function (event) {
      console.log(event.data);
    }*/

    function checkTime(i) {
        return (i < 10) ? "0" + i : i;
    }

    function startDateTime() {
        var today = new Date(),
            h = checkTime(today.getHours()),
            m = checkTime(today.getMinutes()),
            s = checkTime(today.getSeconds());
        $("#time").html(h + ":" + m);

		var date = new Date(),
		months = ['January','February','March','April','May','June','July','August','Septembe','October','November','December'],
		days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
		$("#date").html(days[date.getDay()] + ' ' + date.getDate() + ' ' + months[date.getMonth()]);

		t = setTimeout(function () {
            startDateTime()
        }, 1000);
    }
    startDateTime();
	
	function updateWeather() {
		var weather_icons = {
			'01d':'wi-day-sunny',
			'02d':'wi-day-cloudy',
			'03d':'wi-cloudy',
			'04d':'wi-cloudy-windy',
			'09d':'wi-showers',
			'10d':'wi-rain',
			'11d':'wi-thunderstorm',
			'13d':'wi-snow',
			'50d':'wi-fog',
			'01n':'wi-night-clear',
			'02n':'wi-night-cloudy',
			'03n':'wi-night-cloudy',
			'04n':'wi-night-cloudy',
			'09n':'wi-night-showers',
			'10n':'wi-night-rain',
			'11n':'wi-night-thunderstorm',
			'13n':'wi-night-snow',
			'50n':'wi-night-alt-cloudy-windy'
		}
		
		
		$.getJSON('weather', function (weather) {
			if(weather['body']!=undefined && weather['body']!=''){
			weather = weather['body'];
			$("#weatherContainer #temperature").html(Math.round(weather['main']['temp']) + '<sup id="metric">°</sup>');
			$(".miniInfo #location").html(weather['name']);
			$("#weatherContainer #iconStatus").removeClass().addClass('wi').addClass(weather_icons[weather['weather'][0]['icon']]);
			}else{
				setTimeout(refreshInfos,1000);
			}
		});
		
		
		
	}
	
	function refreshInfos() {
		updateWeather();
		
	}
	function initMap() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(showPosition);
		} else {
			showPosition({latitude:'',longitude:''});
		}

	}
	function showPosition(position){
		
		if(position.coords.latitude!='' && position.coords.latitude!=''){
			url='weather?lat='+position.coords.latitude+'&lon='+position.coords.longitude;
			$.getJSON(url);
			setTimeout(refreshInfos,1000);
		}
		
	}
	setTimeout(refreshInfos, 1000 * 30);
	initMap();
	refreshInfos();
});