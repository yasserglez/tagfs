/*
  Assorted Javascript Functions for The Wordpress Wiki Theme.
  Author: Derek Herman http://valendesigns.com (November 2008)
*/

$(document).ready(function(){
	// Toggle FAQs
	$("#faq > li > a").click(function(){
		if ($(this).next("ul").is(":hidden")) {
			$(this).next("ul").slideDown("fast");
			$(this).addClass("down");
			return false;
		} else {
			$(this).next("ul").slideUp("fast");
			$(this).removeClass("down");
			return false;
		}
	});
	// Toggle Navigation
	$("#navigation > li > a").click(function(){
		if ($(this).next("ul").is(":hidden")) {
			$(this).next("ul").slideDown("fast");
			$(this).addClass("current-item");
			return false;
		} else {
			$(this).next("ul").slideUp("fast");
			$(this).removeClass("current-item");
			return false;
		}
	});
	// Show Current Navigation
	$('.current-cat').parents('ul,li').addClass('show'); 
});