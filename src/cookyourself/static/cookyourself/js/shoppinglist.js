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

// Callback function reserved for each request readystatechange.
// it will eventually parse the XML response for the request
function handleResponse() {
    if (req.readyState != 4 || req.status != 200) {
        return;
    }
    // Removes the old shopping list items
    var list = document.getElementById("shopping-list");
    while (list.hasChildNodes()) {
        list.removeChild(list.firstChild);
    }

    // Parse the response to get a list of Javascript object for the items
    var data = JSON.parse(req.responseText);
    var ingredients = data["ingredients"];
    var total_price = data["price"];

    // Adds each new ingredient item to the shopping list
    for (var i = 0; i < ingredients.length; i++) {
        var id = ingredients[i].id;
        var name = ingredients[i].name;
        console.log("dish id:" + id);
        console.log("dish name:" + name);

        var newIngre = document.createElement("li");
        newIngre.className += "list-group-item";
        newIngre.innerHTML = name + "<span class=\"pull-right icon-remove-parent\"><button class=\"btn-list-remove\" href=\"/cookyourself/del_ingredient/" + id + "\"><span class=\"glyphicon glyphicon-remove icon-remove\"></span></button></span>";
        list.appendChild(newIngre);
    }
}
// causes the sendRequest to run every 10 seconds
window.setInterval(sendRequest, 1000);