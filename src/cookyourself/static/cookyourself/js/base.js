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
   id=null;
   usr=null;
   p_url=null;
   g=null;
   l=null;
   e=null;
   $.ajaxSetup({ cache: true });
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

function eventHandle(){
  $("#fb-login").on("click", function( event ) { 
        event.preventDefault();
        FB.login(function(response){
         // console.log("fb-login");
          //console.log(response);
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
           var current_url=window.location.href;
          // console.log(current_url);
           if (current_url=="http://54.244.78.192/cookyourself/" || current_url=="http://54.244.78.192/")
            checkLoginState();
           else 
            window.location.href = "/cookyourself";        
        }); 
   }); 
}

function getUserInfo(callback) {
  //console.log("getUserInfo");
  FB.api('/me', 'get', { fields: 'name, gender, email, location' }, function(response) {
    //console.log(response);
    usr=response.name;
    id=response.id;
    g=response.gender;
    if (response.email){
      e=response.email;
      //console.log("this user has email:"+e);
    }
    else{
      //console.log("this user doesn't have email");
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
     // console.log(response);
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
    //console.log("addUser");
    //console.log("usrname:"+usr);
    //console.log("id:"+id);
    $.post("/cookyourself/add_user",
    {
      uid: id,
      username: usr,
      url: p_url,
      gender: g,
      location:l
    })
    .done(function(data) 
      { 
       // console.log("login success"); 
        var usrid=data['usrid'];
        document.getElementById("profile_link").href ="/cookyourself/profile/"+ usrid;
      }); 
}

function logoutUser() {
  $.post("/cookyourself/logout_user")
  //.done(function() { //console.log("logout success"); }); 
}


  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    // console.log('statusChangeCallback');
    // console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      $("#fb-logout").show(); 
      $("#profile").show();
      $("#fb-login").hide(); 
      $("#fb-signup").hide();
      getUserInfo(GetPic);

    } else if (response.status === 'not_authorized') {
      // The person is logged into Facebook, but not your app.
      $("#fb-signup").show(); 
      $("#fb-login").hide(); 
      $("#profile").hide();
      $("#fb-logout").hide(); 
      $('#portrait').hide();
      $('#more').show();
      $('#portrait').removeAttr('src');
      //document.getElementById("portrait").style= "width: 33px; height: 18px;";
      document.getElementById("user_photo").style= "padding-top: 14px; padding-bottom: 2px;";  
    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
        $("#fb-signup").show(); 
        $("#fb-login").show();
        $("#fb-logout").hide(); 
        $("#profile").hide();
        $('#portrait').hide();
        $('#more').show();
        $('#portrait').removeAttr('src');
        //document.getElementById("portrait").style= "width: 33px; height: 18px;";
        document.getElementById("user_photo").style= "padding-top: 14px; padding-bottom: 2px;";
        //document.getElementById("user_photo").src="";  
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