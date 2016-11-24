/**
 * Created by yunpengx on 11/16/16.
 */

//send a new request to update the shopping list
var req;
var shoppingInventory = "";
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
    var email = $("#email").val();
    if (validateEmail(email)) {
        $("#email").css("color", "green");
        return true;
    } else {
        $("#email").css("color", "red");
        window.alert("Please input a valid email address!")
    }
    return false;
}

function sendMail() {
    ret = validate();
    if (!ret) {
        return;
    }

    var email = $("#email").val();
    var subject = "Your shopping list from Cookyourself team";
    var body = "Hi,\n" +
        "The following is the shopping list you created on Cookyourself:\n\n"
        + shoppingInventory +
        "Thanks for your support Cookyourself, we will continue offer our best service to you.\n" +
        "The Cookyourself Team";
    $(location).attr('href', "mailto:" + email + "?"
        + "&subject="
        + encodeURIComponent(subject)
        + "&body="
        + encodeURIComponent(body)
    );
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

    var tmp = [];
    shoppingInventory = "";
    // Adds each new ingredient item to the shopping list
    for (var i = 0; i < ingredients.length; i++) {
        var id = ingredients[i].id;
        var name = ingredients[i].name;
        var price = ingredients[i].price;
        var amount = ingredients[i].amount;
        var item = "";
        var price_item = ['($', price, ')'].join("");
        item = [amount, price_item, name].join("\t");
        tmp.push(item);

        var newIngre = document.createElement("li");
        newIngre.className += "list-group-item";
        newIngre.innerHTML = "<strong>" + amount + "&nbsp;" + "($" + price + ")" + "&nbsp;" + name + "&nbsp;" + "</strong><a class=\"pull-right icon-remove-parent\" href=\"/cookyourself/del_ingredient/" + id + "\">X</a> ";
        list.appendChild(newIngre);
    }
    shoppingInventory = tmp.join("\n");
    shoppingInventory += "\nThe total price is: $" + total_price + "\n\n";
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
