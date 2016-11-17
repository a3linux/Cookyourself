/**
 * Created by yunpengx on 10/28/16.
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
});

function eventHandle(){
  $("#fb-login").on("click", function( event ) { 
        FB.login(function(response){
          console.log("fb-login");
          console.log(response);
          checkLoginState();     

        },{scope: 'public_profile,email,user_location'});
   });
    $("#fb-signup").on("click", function( event ) { 
        FB.login(function(response){
              checkLoginState();
              
        }, {scope: 'public_profile,email,user_location'});
   });
    $("#fb-logout").on("click", function( event ) { 
        FB.logout(function(response){
           // Handle the response object
           logoutUser();
           var current_url=window.location.href;
           console.log(current_url);
           //window.location.href = "/cookyourself";
              
        }); 
   }); 
}

function getUserInfo(callback) {
  //var username;
  //var p_url;
  //addUser(1);
  console.log("getUserInfo");
  FB.api('/me', 'get', { fields: 'name, gender, email, location' }, function(response) {
    console.log(response);
    usr=response.name;
    id=response.id;
    g=response.gender;
    if (response.email){
      e=response.email;
      console.log("this user has email:"+e);
    }
    else{
      console.log("this user doesn't have email");
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
      console.log(response);
        /* handle the result */
      p_url=response.data['url'];
      document.getElementById("portrait").src = p_url; 
      }
      callback();
    });
}

function addUser(){
    console.log("addUser");
    console.log("usrname:"+usr);
    console.log("id:"+id);
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
        console.log("login success"); 
        var usrid=data['usrid'];
        document.getElementById("profile_link").href ="/cookyourself/profile/"+ usrid;
      }); 
}

function logoutUser() {
  $.post("/cookyourself/logout_user")
  .done(function() { console.log("logout success"); }); 
}


  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
     console.log('statusChangeCallback');
     console.log(response);
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
      $('#portrait').removeAttr('src');
      //document.getElementById("user_photo").src="";  

    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
        $("#fb-signup").show(); 
        $("#fb-login").show();
        $("#fb-logout").hide(); 
        $("#profile").hide();
        $('#portrait').removeAttr('src');
        //document.getElementById("user_photo").src="";  
    }
  }

  /*function initialStatusCallback(response) {
     console.log('initialStatusCallback');
     console.log(response);
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
      getUserInfo(response);
      addUser();
      
    } else if (response.status === 'not_authorized') {
      // The person is logged into Facebook, but not your app.
      $("#fb-signup").show(); 
      $("#fb-login").hide(); 
      $("#profile").hide();
      $("#fb-logout").hide(); 
      $('#portrait').removeAttr('src');
      //document.getElementById("user_photo").src="";  

    } else {
      // The person is not logged into Facebook, so we're not sure if
      // they are logged into this app or not.
        $("#fb-signup").show(); 
        $("#fb-login").show();
        $("#fb-logout").hide(); 
        $("#profile").hide();
        $('#portrait').removeAttr('src');
        //document.getElementById("user_photo").src="";  
    }
  }

  function initialLoginState() {
    FB.getLoginStatus(function(response) {
      initialStatusCallback(response);
    });
  }*/

  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }

  /*window.fbAsyncInit = function() {
  FB.init({
    appId      : '945239262274790',
    cookie     : true,  // enable cookies to allow the server to access 
                        // the session
    xfbml      : true,  // parse social plugins on this page
    version    : 'v2.8' // use graph api version 2.8
  });
  FB.getLoginStatus(function(response) {
    statusChangeCallback(response);
  });

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


  };*/

  // Load the SDK asynchronously
   /*(function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));*/