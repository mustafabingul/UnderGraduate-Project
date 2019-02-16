$(function(){

	function sendRequest(params){
			$.ajax({
				"crossOrigin":true,
				"method": "GET",
				"url": "/movement/gestures?params="+params,
				
				}).done(function (response) {
					console.log(response);
				});
	}
	$('#thumbsUp').on('click',function(){
		sendRequest('{"gestThumbsUp":"true", "elapsedTimeWithSameGesture": 2}');
	});
	$('#thumbsDown').on('click',function(){
		sendRequest('{"gestThumbsDown": true,"elapsedTimeWithSameGesture": 1}');
	});
	$('#palm').on('click',function(){
		sendRequest('{"gestPalm":"true", "elapsedTimeWithSameGesture": 2}');
	});
	$('#slideLeft').on('click',function(){
		sendRequest('{"gestSlideLeft": true}');
	});
	$('#slideRight').on('click',function(){
		sendRequest('{"gestSlideRight": true}');
	});
	$('#slideDown').on('click',function(){
		sendRequest('{"gestSlideDown": true}');
	});
	$('#slideUp').on('click',function(){
		sendRequest('{"gestSlideUp": true}');
	});
	
	
	
	
	
});