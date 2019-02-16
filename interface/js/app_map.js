function callbackGestureMap(gesture) {
	if (gesture.gestThumbsDown && gesture.elapsedTimeWithSameGesture > 0.1)
		bringBackMainMenu();
}

function initMap() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        x.innerHTML = "Geolocation is not supported by this browser.";
    }

}
function  showPosition(position) {
    var mapDiv = document.getElementById('map');

    var map = new google.maps.Map(mapDiv, {
        center: {lat: position.coords.latitude, lng: position.coords.longitude}, zoom: 15
    });

    var marker = new google.maps.Marker({
        position: {lat: position.coords.latitude, lng: position.coords.longitude},
        map: map,
        icon: '../img/home.png'
    });
    var trafficLayer = new google.maps.TrafficLayer();
    trafficLayer.setMap(map);
}