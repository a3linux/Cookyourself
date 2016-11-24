/**
 * Created by yunpengx on 11/16/16.
 */

//send a new request to update the shopping list
var req;
function sendRequest() {
    if (window.XMLHttpRequest) {
        req = new XMLHttpRequest();
    } else {
        req = new ActiveXObject("Microsoft.XMLHTTP");
    }
    req.onreadystatechange = handleResponse;
    req.open("GET", "/cookyourself/get_shoppinglist", true);
    req.send();
}

function validateEmail(email) {
  var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
  return re.test(email);
}

function validate() {
  // $("#email").text("");
  var email = $("#email").val();
  if (validateEmail(email)) {
    // $("#email").text(email + " is valid :)");
    $("#email").css("color", "green");
  } else {
    // $("#email").text(email + " is not valid :(");
    $("#email").css("color", "red");
  }
  return false;
}

function sendMail() {
    validate();
    var link = "mailto:yunpengx@andrew.cmu.edu"
             // + "?cc=myCCaddress@example.com"
             + "&subject=" + escape("This is my subject")
             + "&body=" + escape(document.getElementById('email').value)
    ;

    window.location.href = link;
}

function shoppingListDisplay() {
    // Removes the old shopping list items
    var list = document.getElementById("shopping-list");
    while (list.hasChildNodes()) {
        list.removeChild(list.firstChild);
    }

    // Parse the response to get a list of Javascript object for the items
    var data = JSON.parse(req.responseText);
    var ingredients = data["ingredients"];
    var total_price = data["price"];

    var price_obj = document.getElementById("total_price");
    price_obj.className += "text";
    price_obj.innerHTML = total_price;

    // Adds each new ingredient item to the shopping list
    for (var i = 0; i < ingredients.length; i++) {
        var id = ingredients[i].id;
        var name = ingredients[i].name;
        var price = ingredients[i].price;
        var amount = ingredients[i].amount;

        var newIngre = document.createElement("li");
        newIngre.className += "list-group-item";
        // newIngre.innerHTML = name + "<span class=\"pull-right icon-remove-parent\"><button class=\"btn-list-remove\" href=\"/cookyourself/del_ingredient/" + id + "\"><span class=\"glyphicon glyphicon-remove icon-remove\"></span></button></span>";
        newIngre.innerHTML = "<strong>" + amount + "&nbsp;" + "($" + price + ")" + "&nbsp;" + name + "&nbsp;" + "</strong><a class=\"pull-right icon-remove-parent\" href=\"/cookyourself/del_ingredient/" + id + "\">X</a> ";
        list.appendChild(newIngre);
    }
}

// Callback function reserved for each request readystatechange.
// it will eventually parse the XML response for the request
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }
    shoppingListDisplay();
}
// causes the sendRequest to run every 8 seconds
window.setInterval(sendRequest, 800);
