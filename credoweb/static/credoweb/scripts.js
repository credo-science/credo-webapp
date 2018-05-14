$(document).ready(function () {

    //handler for displaying "big images"
    $(".big_img").click(function () {

        var image = $(this).attr("src");
        $("#new_img").attr("src", image);
        $("#image_view").css("display", "block");
    });


    $("#close_img_view").click(function() {
        $("#image_view").css("display", "none");
    });
});