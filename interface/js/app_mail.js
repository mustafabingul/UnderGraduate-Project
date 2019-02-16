function callbackGestureMail(gesture) {
	if (gesture.gestThumbsDown && gesture.elapsedTimeWithSameGesture > 0.1)
	//haberleri istediğimiz gibi kullan...
		bringBackMainMenu();
	else if (gesture.gestSlideUp)
		smoothScrollBy(window.innerHeight, 750);
	else if (gesture.gestSlideDown)
		smoothScrollBy(window.innerHeight * -1, 750);
}

$(document).ready(function() {
	$.getJSON("mail", function(data) {
		var news = "<table>";
		if(data.length==0){
			setTimeout(function(){
				callbackGestureMail({gestPalm:true,elapsedTimeWithSameGesture:2});
			},1500);
		}
		$.each(data, function(key, mail) {
			var title = "<div class='newsHeader'><span class='title'>" + mail.subject + "</span><br>" + mail.sender.email + "("+mail.sender.name+")</div>";
			news += "<tr><td class='news_item'><div class='meta'>" + title + "<br>";
			news += "" + mail.body + "</td></tr>";
		});
		
		news += "</table>";
		$("#news").append(news);
	});
});