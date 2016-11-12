function addIngredient (id){
    $.post("/cookyourself/add_ingredient/"+ id)
    .done(function(data){
        //updateComment(id);
        //hide the + button or make it grey?
    });
}  

function events_handle(){
   $("#ingre-list").on("click", ".glyphicon glyphicon-check", function( event ) {
        var id=$(this).attr("id");
        /*if(id == 0)
        {
          addAllIngredient();
        }
        else*/
        addIngredient(id);
   });
}

$(document).ready(function () {

  events_handle();
  
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