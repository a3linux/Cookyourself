/**
 * Created by yunpengx on 11/12/16.
 */

/**
 * Resize the image to the standard height and keep the original image's ratio of width and height
 * @param standardHeight
 */
function imageResize(standardHeight) {
    $('.imageResize').each(function () {
        var standardHeight = standardHeight;    // standard height for post images
        var ratio = 0;          // used for aspect ratio
        var width = $(this).width(); // current image width
        var height = $(this).height(); // current image height

        // check if the current height is larger than the max
        if (height != standardHeight) {
            ratio = standardHeight / height;
            $(this).css("height", standardHeight);
            $(this).css("width", ratio * width);
            width = width * ratio;
        }
    })
}

/**
 * image Crop using the html5 canvas tag
 * Refer to examples in dish.html and recommendation.html
 */
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

$(document).ready(function () {
    imageCrop();
});