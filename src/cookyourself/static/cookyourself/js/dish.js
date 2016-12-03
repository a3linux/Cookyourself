/**
 * Created by wennad.
 */
function addIngredient(iid) {
    var csrftoken = getCookie('csrftoken');
    var did = document.getElementById("dish_id").value;
    $.post("/cookyourself/add_ingredient/" + iid, {dishid: did, csrfmiddlewaretoken: csrftoken})
        .done(function (data) {
            if (data['redirect']){
                window.location.href=data['redirect'];
            }
        });
}

function upvote() {
    var csrftoken = getCookie('csrftoken');
    var did = document.getElementById("dish_id").value;
    $.post("/cookyourself/upvote_dish", {dishid: did, csrfmiddlewaretoken: csrftoken})
        .done(function (data) {
            if (data['redirect']){
                window.location.href=data['redirect'];
            }
            var popularity=data['popularity']
            $('#popularity').text(popularity);
        });
}

function save() {
    var stat = $('#user_status').val();
    if (stat == 0){
       alert("Please join us, then you can save your favorite recipe!");
    }
    else {
        var csrftoken = getCookie('csrftoken');
        var did = document.getElementById("dish_id").value;
        $.post("/cookyourself/save_dish", {dishid: did, csrfmiddlewaretoken: csrftoken})
        .done(function (data) {
            if (data['redirect']){
                window.location.href=data['redirect'];
            }
            $('#heart').css("color", "#ea1c1c"); 
        });
    }
    
}

function eventsHandle() {
    $("#ingre-list").on("click", ".glyphicon", function (event) {
        var iid = $(this).attr("id");
        var stat = $('#user_status').val();
        if (stat ==0 ){
            alert("Please join us, then you can make a shopping list!");
        }
        else{
            addIngredient(iid);
        }
    });
    $("#upvote").on("click", function(event){
        upvote();
    });
    $("#save").on("click", function(event){
        save();
    });
}

function ifsaved() {
   var saved = document.getElementById("saved").value;
   if (saved==1)
   {
     $('#heart').css("color", "#ea1c1c");
   }
}

$(document).ready(function () {
    ifsaved();
    eventsHandle();
    var csrftoken = getCookie('csrftoken');
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    });
});

// CSRF set-up copied from Django docs
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
