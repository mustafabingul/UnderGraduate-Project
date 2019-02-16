function callbackGestureExchange(gesture) {
	if (gesture.gestThumbsDown && gesture.elapsedTimeWithSameGesture > 0.1)
	//haberleri istediğimiz gibi kullan...
		bringBackMainMenu();
	else if (gesture.gestSlideUp)
		smoothScrollBy(window.innerHeight, 750);
	else if (gesture.gestSlideDown)
		smoothScrollBy(window.innerHeight * -1, 750);
}

$(document).ready(function() {
	$.getJSON("exchange", function(data) {
		if(data.length==0){
			setTimeout(function(){
				callbackGestureExchange({gestPalm:true,elapsedTimeWithSameGesture:2});
			},1500);
		}
		$.each(data, function(key, currecy) {
           var s='<tr><td style="width:500px;">'+currecy.name+'</td><td>'+currecy.value+'</td></tr>';
           $("#exchange tbody").append(s);
		});
		$("#exchange table").show();
	});
});