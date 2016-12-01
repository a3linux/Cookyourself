function addIngredient(iid) {
    var csrftoken = getCookie('csrftoken');
    var did = document.getElementById("dish_id").value;
    $.post("/cookyourself/add_ingredient/" + iid, {dishid: did, csrfmiddlewaretoken: csrftoken})
        .done(function (data) {
            //updateComment(id);
            //hide the + button or make it grey?
            //console.log("ingredient added:" + iid + "for dish:" + did);
        });
}

function upvote() {
    var csrftoken = getCookie('csrftoken');
    var did = document.getElementById("dish_id").value;
    $.post("/cookyourself/upvote_dish", {dishid: did, csrfmiddlewaretoken: csrftoken})
        .done(function (data) {
            var popularity=data['popularity']
            //hide the + button or make it grey?
            $('#popularity').text(popularity);
            //console.log("dish popularity added:" + did );
            //console.log("popularity" + popularity);
        });
}

function save() {
    var csrftoken = getCookie('csrftoken');
    var did = document.getElementById("dish_id").value;
    $.post("/cookyourself/save_dish", {dishid: did, csrfmiddlewaretoken: csrftoken})
    .done(function (data) {
        $('#heart').css("color", "#ea1c1c");
    });
}

function eventsHandle() {
    $("#ingre-list").on("click", ".glyphicon", function (event) {
        var iid = $(this).attr("id");
        //console.log("iid:" + iid);
        //addAllIngredient();
        addIngredient(iid);
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
   //console.log("saved: "+ saved);
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
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
