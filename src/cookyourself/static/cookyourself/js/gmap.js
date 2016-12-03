/**
 * Created by wennad.
 */
var map;
var markers=new Array();
var message=document.getElementById("message");

function myMap() {
  var mapCanvas = document.getElementById("map");
  mapCanvas.style="width:100%; height:180px"
  var mapOptions = {
    center: {lat: 40.441, lng: -79.996},  //default center: Pittsburgh
    zoom: 13,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(mapCanvas, mapOptions);
}

function createMarker(place){
  var l = new google.maps.LatLng(place.geometry.location.lat(),place.geometry.location.lng());
  var marker=new google.maps.Marker({position: l});
  marker.setMap(map);
  markers.push(marker);
  var infowindow = new google.maps.InfoWindow({
    content: place.name
  });
  infowindow.open(map,marker);
  drawpath();
}

function searchStore(position){
  var request = {
      location: position,
      radius: '500',
      query: 'market'
    };
    var service = new google.maps.places.PlacesService(map);
    service.textSearch(request, callback);
}

function callback(results, status) {
  if (status == google.maps.places.PlacesServiceStatus.OK) {
    createMarker(results[0]);
  }
}

function usercallback(results, status) {
  if (status == google.maps.places.PlacesServiceStatus.OK) {
      redrawMap(results[0]);
  }
}

function redrawMap(position){
  var mapCanvas = document.getElementById("map");
  var userCenter = new google.maps.LatLng(position.geometry.location.lat(), position.geometry.location.lng());
  var mapOptions = {
    center: userCenter, //from the getLocation
    zoom: 12, //0 is the earth, larger the zoom is, the map is more zoomed in.
    mapTypeId: google.maps.MapTypeId.ROADMAP
  }
  map = new google.maps.Map(mapCanvas, mapOptions);
  var marker=new google.maps.Marker({position: userCenter});
  marker.setMap(map);
  markers.splice(0, markers.length);
  markers.push(marker);
  searchStore(userCenter);

}

function getLocation() {
  var position=$("#user_location").val();
  if (position.length==0){
    $("#user_location").css("color", "red");
    window.alert("Please enter your location.");
    return false;
  }
  var request = {
    query: position
  }
  var service = new google.maps.places.PlacesService(map);
  service.textSearch(request, usercallback);
}

function drawpath(){
  var path = new google.maps.MVCArray();
  //Intialize the Direction Service
  var service = new google.maps.DirectionsService();
  //Set the Path Stroke Color
  var poly = new google.maps.Polyline({
    map: map,
    strokeColor: '#4986E7'
  });

  var src=markers[0].position;
  var des=markers[1].position;

  poly.setPath(path);
  service.route({
    origin: src,
    destination: des,
    travelMode: google.maps.DirectionsTravelMode.WALKING
  }, function(results,status){
    if (status == google.maps.DirectionsStatus.OK) {
      for (var i = 0, len = results.routes[0].overview_path.length; i < len; i++) {
        path.push(results.routes[0].overview_path[i]);
      }
    }
  });
}

$(document).ready(function () {
  myMap();
});