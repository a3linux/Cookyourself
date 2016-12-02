
$(document).ready(function () {
	populateList();
	$('#post-form').on ('submit', function(event){
	//event.preventDefault();
	   //console.log("form submitted to js");
       create_post();
       return false;
    });
    window.setInterval(getUpdates, 5000);

  // CSRF set-up copied from Django docs
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
});

function getCookie(name) {  
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function create_post(){
	var csrftoken = getCookie('csrftoken');
    var content= $('#post-content').val();
    if (content.length!=0){
       $.post("/cookyourself/create_post",
       {
         content: content,
         dish: $('#dish_id').val(),
         csrfmiddlewaretoken: csrftoken
       })
       .done(function(data) 
       { 
         if (data['redirect']){
            window.location.href=data['redirect'];
         }
        $('#post-content').val("");
          getUpdates();
        }); 
    }
}

function populateList() {
    var csrftoken = getCookie('csrftoken');
    $.post("/cookyourself/update_posts",
    {
    	time: "1970-01-01T00:00+00:00",
    	dishid: $('#dish_id').val(),
        csrfmiddlewaretoken: csrftoken
    })
    .done(function(data) 
    {
        if (data['redirect']){
          window.location.href=data['redirect'];
        }
        var list = $("#post-list");
        list.data('max-time', data['max-time']);
        list.html('')
        for (var i = 0; i < data.posts.length; i++) {
            post = data.posts[i];
            var new_post = $(post.html);
            new_post.data("post-id", post.id);
            list.append(new_post);
        }
    });
}

function getUpdates() {
    var csrftoken = getCookie('csrftoken');
    var list = $("#post-list")
    var max_time = list.data("max-time")
    $.post("/cookyourself/update_posts/",
    {
    	time: max_time,
    	dishid: $('#dish_id').val(),
        csrfmiddlewaretoken: csrftoken
    })
    .done(function(data) {
        if (data['redirect']){
         window.location.href=data['redirect'];
        }
        list.data('max-time', data['max-time']);
        for (var i = 0; i < data.posts.length; i++) {
            var post = data.posts[i];
            var new_post = $(post.html);
            new_post.data("post-id", post.id);
            list.prepend(new_post);
        }
    });
}