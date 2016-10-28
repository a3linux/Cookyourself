/**
 * Created by yunpengx on 10/28/16.
 */

$(document).ready(function () {

    var clockElement = document.getElementById("clock");
    function updateClock(clock) {
        // clock.innerHTML = new Date(Date.now()).toLocaleString()
        clock.innerHTML = moment().format('MMM D, YYYY, h:mm:ss a')
    }
    updateClock(clockElement);

    setInterval(function () {
        updateClock(clockElement);
    }, 60000);
});