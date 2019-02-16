$(document).ready(function() {



	loadWidget("img/map.png", "app_map.html", "callbackGestureMap");
	loadWidget("img/news.png", "app_news.html", "callbackGestureNews");
	loadWidget("img/exchange.png","app_exchange.html","callbackGestureExchange");
	loadWidget("img/mail.png","app_mail.html","callbackGestureMail");
	loadWidget("img/quest.png","foo.html","CallFoo");
	// Widget click event
	$('body').on('click', '.swiper-slide-active', function() {
		var widget = $(this);
		$("#widget").load(widget.data('render'), function() {
			setCallbackGesture(window[widget.data('callback')]);
			$(".screen-page-1").addClass("pt-page-moveToLeftFade");
			$(".screen-page-2").addClass("pt-page-current pt-page-moveFromRightFade");
			setTimeout(function () { 
				$(".screen-page-1").removeClass("pt-page-current pt-page-moveToLeftFade");
				$(".screen-page-2").removeClass("pt-page-moveFromRightFade");
				$("#menuContainer").hide();
				$("#infoContainer").hide();
			}, 1000);
		});
	});
	
	var motionSocket = io.connect('/movement');
	motionSocket.on('gestures', function(jsonArray) {
		console.log(jsonArray);
		for (jsonGesture in jsonArray) break;
		console.log(jsonArray);
		gesture = JSON.parse(jsonArray);
		if(gesture.gestThumbsUp==true){
			console.log('gestThumbsUp:true -- Elapsed:'+gesture.elapsedTimeWithSameGesture);
		}
		callbackGesture(gesture);

	});
});

function loadWidget(img, render_page, callback) {
	$(".swiper-wrapper").prepend(
	"<img class='swiper-slide' src='" + img
	+ "' data-render='" + render_page
	+ "' data-callback='" + callback
	+ "' />");
	
	swiperMenu = new Swiper ('.swiper-container', {
		// Optional parameters
		direction: 'horizontal',
		loop: true,

		// If we need pagination
		pagination: '.swiper-pagination',

		// Navigation arrows
		nextButton: '.swiper-button-next',
		prevButton: '.swiper-button-prev',

		preloadImages: true,
		effect: 'coverflow',
		centeredSlides: true,
		slidesPerView: 3,
		coverflow: {
			rotate: 50,

			depth: 100,
			modifier: 1,
			slideShadows: false,
			stretch: 0,
		}
	});
	swiperMenu.slideNext(false);
}

var swiperMenu = null;
function callbackGestureMainMenu(gesture) {
    //right-left slide.. ANA MENUYUU
	if ((!gesture.gestThumbsUp && gesture.elapsedTimeWithSameGesture > 100) ||
		(!gesture.gestHandFound && gesture.elapsedTimeWithSameGesture > 100))
	{	
		$(".pt-page-2").addClass("pt-page-moveToRightFade");
		$(".pt-page-1").addClass("pt-page-current pt-page-moveFromLeftFade");
		setTimeout(function () { 
			$(".pt-page-1").removeClass("pt-page-moveFromLeftFade");
			$(".pt-page-2").removeClass("pt-page-current pt-page-moveToRightFade");
		}, 1000);
		setCallbackGesture(callbackGestureMenuButton);
		
		return;
	}else{console.log("Girmedi.");}
	
	if (gesture.gestSlideLeft)
		swiperMenu.slideNext(false);
	else if (gesture.gestSlideRight)
		swiperMenu.slidePrev(false);
	else if (gesture.gestPalm && gesture.elapsedTimeWithSameGesture > 0.3)
		$('.swiper-slide-active').click();
}

function setCallbackGesture(callback) {
	callbackGesture = callback;
}

function bringBackMainMenu() {
	$("#menuContainer").show();
	$("#infoContainer").show();
	$(".screen-page-2").addClass("pt-page-moveToRightFade");
	$(".screen-page-1").addClass("pt-page-current pt-page-moveFromLeftFade");
	setTimeout(function () { 
		$(".screen-page-2").removeClass("pt-page-current pt-page-moveToRightFade");
		$(".screen-page-1").removeClass("pt-page-moveFromLeftFade");
		$("#widget").html("");
	}, 800);
	setCallbackGesture(callbackGestureMainMenu);
	window.scrollTo(0, 0);
}

function smoothScrollBy(position, timeInMs) {
	for (var nbFrame = 1; nbFrame <= 60; nbFrame += 1)
	{
		setTimeout(function() {
			window.scrollBy(0, position / 60);
		}, timeInMs / 60 * nbFrame);
	}
}