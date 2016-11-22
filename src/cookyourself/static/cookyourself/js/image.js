/**
 * Created by yunpengx on 11/12/16.
 */
$(document).ready(function () {
    $('.image_300h').each(function () {
        var standardHeight = 300;    // standard height for post images
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
    });

    $('.image_400h').each(function () {
        var standardHeight = 400;    // standard height for post images
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
});