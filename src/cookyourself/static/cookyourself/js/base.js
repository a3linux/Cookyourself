/**
 * Created by yunpengx on 10/28/16.
 * Modified by wennad on 11/18/16--fb login
 */
var id=null;
var usr=null;
var p_url=null;
var g=null;
var l=null;
var e=null;

$(document).ready(function () {
  // CSRF set-up copied from Django docs
  var csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    beforeSend: function(xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", csrftoken);
    }
  });
  $.getScript('//connect.facebook.net/en_US/sdk.js', function(){
    FB.init({
       appId      : '945239262274790',
      cookie     : true,  // enable cookies to allow the server to access 
                        // the session
       xfbml      : true,  // parse social plugins on this page
       version    : 'v2.8' // use graph api version 2.8
    }); 
    checkLoginState(); 
  });
  document.getElementById("timestamp").innerHTML = String(new Date().getFullYear());
  eventHandle();  
});

function eventHandle(){
  $("#fb-login").on("click", function( event ) { 
        event.preventDefault();
        FB.login(function(response){
        checkLoginState();     

        },{scope: 'public_profile,email,user_location'});
   });
    $("#fb-signup").on("click", function( event ) { 
        event.preventDefault();
        FB.login(function(response){
              checkLoginState();
              
        }, {scope: 'public_profile,email,user_location'});
   });
    $("#fb-logout").on("click", function( event ) { 
        event.preventDefault();
        FB.logout(function(response){
           // Handle the response object
           logoutUser();   
        }); 
   });
   $('#navbar-search-input').keypress(function(event){
    // If RNTER key is pressed
    if (event.which == 13){
      event.preventDefault();
      var target = event.target||event.srcElement;
      var content = target.value.trim();
      if(content) {
        window.location.replace("/cookyourself/search/?q="+content);
      }
    }
   }); 
}

function getUserInfo(callback) {
  FB.api('/me', 'get', { fields: 'name, gender, email, location' }, function(response) {
    usr=response.name;
    id=response.id;
    g=response.gender;
    if (response.email){
      e=response.email;
    }
    if(response.location){
      l=response.location.name;
    }  
    callback(addUser);
  });
}

function GetPic(callback) {
    FB.api("/me/picture?type=large", { redirect: 0 }, function (response) {
    if (response && !response.error) {
        /* handle the result */
      p_url=response.data['url'];
      document.getElementById("portrait").src = p_url;
      $('#more').hide();
      $('#portrait').show();
      document.getElementById("user_photo").style= "padding-top: 8px; padding-bottom: 8px;";
      }
      callback();
    });
}

function addUser(){
    var csrftoken = getCookie('csrftoken');
    $.post("/cookyourself/add_user",
    {
      uid: id,
      username: usr,
      url: p_url,
      gender: g,
      location:l,
      csrfmiddlewaretoken: csrftoken
    })
    .done(function(data) 
      { 
        if (data['redirect']){
          window.location.href=data['redirect'];
        }
        if (data['usrid']){
          var usrid=data['usrid'];
          document.getElementById("profile_link").href ="/cookyourself/profile/"+ usrid;
        }
        
    }); 
}

function logoutUser() {
  var csrftoken = getCookie('csrftoken');
  $.post("/cookyourself/logout_user", {csrfmiddlewaretoken: csrftoken})
  .done(function(data)
  {
    if(data['redirect']){
      window.location.href=data['redirect'];
    }
  });    
}


  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      $("#fb-logout").show(); 
      $("#profile").show();
      $("#list").show();
      $("#fb-login").hide(); 
      $("#fb-signup").hide();
      document.getElementById("user_status").value=1;
      getUserInfo(GetPic);

    } else if (response.status === 'not_authorized') {
      // The person is logged into Facebook, but not your app.
      $("#fb-signup").show(); 
      $("#fb-login").hide(); 
      $("#profile").hide();
      $("#list").hide();
      $("#fb-logout").hide(); 
      $('#portrait').hide();
      $('#more').show();
      $('#portrait').removeAttr('src');
      document.getElementById("user_status").value=0;
      document.getElementById("user_photo").style= "padding-top: 14px; padding-bottom: 2px;";  
    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
        $("#fb-signup").show(); 
        $("#fb-login").show();
        $("#fb-logout").hide(); 
        $("#profile").hide();
        $("#list").hide();
        $('#portrait').hide();
        $('#more').show();
        $('#portrait').removeAttr('src');
        document.getElementById("user_status").value=0;
        //document.getElementById("portrait").style= "width: 33px; height: 18px;";
        document.getElementById("user_photo").style= "padding-top: 14px; padding-bottom: 2px;";
    }
  }


  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }



  // Now that we've initialized the JavaScript SDK, we call
  // FB.getLoginStatus().  This function gets the state of the
  // person visiting this page and can return one of three states to
  // the callback you provide.  They can be:
  //
  // 1. Logged into your app ('connected')
  // 2. Logged into Facebook, but not your app ('not_authorized')
  // 3. Not logged into Facebook and can't tell if they are logged into
  //    your app or not.
  //
  // These three cases are handled in the callback function.


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