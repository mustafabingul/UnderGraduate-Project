function callbackGestureNews(gesture) {
	if (gesture.gestThumbsDown && gesture.elapsedTimeWithSameGesture > 0.1)
	//haberleri istediğimiz gibi kullan...
		bringBackMainMenu();
	else if (gesture.gestSlideUp)
		smoothScrollBy(window.innerHeight, 750);
	else if (gesture.gestSlideDown)
		smoothScrollBy(window.innerHeight * -1, 750);
}

$(document).ready(function() {
	$.getJSON("news", function(data) {
		var news = "<table>";
		if(data.length==0){
			setTimeout(function(){
				callbackGestureNews({gestPalm:true,elapsedTimeWithSameGesture:2});
			},1500);
		}
		$.each(data, function(key, news_item) {
			var img = "<img src='" + news_item.img + "'/>";
			var title = "<div class='newsHeader'><span class='title'>" + news_item.title + "</span><br>" + news_item.category + "</div>";
			news += "<tr><td class='news_item'><div class='thumbnail'>" + img + "</div>" + "<div class='meta'>" + title + "<br>";
			news += "" + news_item.description + "</td></tr>";
		});
		
		news += "</table>";
		$("#news").append(news);
	});
});