/**
 * Created by wennad.
 */
var num=3;
var d;
function recommend(num) {
    var csrftoken = getCookie('csrftoken');
    $.post("/cookyourself/change_recommend", 
        {num: num, csrfmiddlewaretoken: csrftoken})
        .done(function (data) {
            d=data;
            var list = $("#recommend_list");
            list.html('')
            for (var i = 0; i < data.dishes.length; i++) {
                dish = data.dishes[i];
                var new_post = $(dish.html);
                list.append(new_post);
            }
            //hide the + button or make it grey?
            imageCrop();
        });
}

function eventsHandle() {
    $(".als-prev").show();
    $(".als-next").show();
    $("#recommend-control").on("click", ".pick", function (event) {
        num = $(this).attr("id");
        recommend(num);
    });
    $("#again").on("click", function (event) {
        recommend(num);
    });
}

$(document).ready(function () {
    eventsHandle();
    recommend(3);
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



function imageCrop() {
    $('.myCanvas').each(function () {
        var url = this.id; //the original url that specify the image to crop
        var ctx = this.getContext("2d"); //specify 2d image to draw
        var imgObj = new Image();

        imgObj.onload = function () {
            var sx = 0;
            var sy = 0;
            var sw = this.width;    //the url pic width
            var sh = this.height;   //the url pic height
            var dw = 533;           //the width we desire
            var dh = 300;           //the height we desire
            var dx = 0;
            var dy = 0;

            ctx.drawImage(imgObj, sx, sy, sw, sh, dx, dy, dw, dh);
        };
        imgObj.src = url;
    });
}


