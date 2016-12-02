$(document).ready(function () {
    populateList();
    $('#message-form').on ('submit', function(event){
    //event.preventDefault();
       create_message();
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
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
  return cookieValue;
}

function create_message(){
    var csrftoken = getCookie('csrftoken');
    var content= $('#message-content').val();
    if(content.length!=0){
        $.post("/cookyourself/create_message",
        {
            content: content,
            ownerid: $('#owner_id').val(),
            csrfmiddlewaretoken: csrftoken
        })
        .done(function(data) 
        { 
            if (data['redirect']){
               window.location.href=data['redirect'];
            }
            $('#message-content').val("");
               getUpdates();
        }); 
    }
}

function populateList() {
    var csrftoken = getCookie('csrftoken');
    $.post("/cookyourself/update_messages",
    {
        time: "1970-01-01T00:00+00:00",
        ownerid: $('#owner_id').val(),
        csrfmiddlewaretoken: csrftoken
    })
    .done(function(data) 
    {
        if (data['redirect']){
          window.location.href=data['redirect'];
        }
        var list = $("#message-list");
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
    var list = $("#message-list");
    var max_time = list.data("max-time");
    var csrftoken = getCookie('csrftoken');
    $.post("/cookyourself/update_messages/",
    {
        time: max_time,
        ownerid: $('#owner_id').val(),
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
