
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
  function getCookie(name) {  
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
});

function create_post(){
	// console.log("create_post");
	// console.log($('#post-content').val());
	// console.log($('#post-dish').val())
    $.post("/cookyourself/create_post",
    {
      content: $('#post-content').val(),
      dish: $('#post-dish').val()
    })
    .done(function(data) 
    { 
      $('#post-content').val("");
	    // console.log("request success");
	    // console.log(data);
	    getUpdates();
    }); 
}

function populateList() {
    $.post("/cookyourself/update_posts",
    {
    	time: "1970-01-01T00:00+00:00",
    	dishid: $('#post-dish').val()
    })
    .done(function(data) 
    {
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
    var list = $("#post-list")
    var max_time = list.data("max-time")
    $.post("/cookyourself/update_posts/",
    {
    	time: max_time,
    	dishid: $('#post-dish').val()
    })
    .done(function(data) {
        list.data('max-time', data['max-time']);
        for (var i = 0; i < data.posts.length; i++) {
            var post = data.posts[i];
            var new_post = $(post.html);
            new_post.data("post-id", post.id);
            list.prepend(new_post);
        }
    });
}