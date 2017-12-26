$(document).ready(function() {


    $("#input-1-sm").rating().on("rating.clear", function(event) {
        alert("Your rating is reset")
    }).on("rating.change", function(event, value, caption) {
        alert("You rated your experience as: " + value + " stars. Thank you!");
    });

    $("#input-2-sm").rating().on("rating.clear", function(event) {
        alert("Your rating is reset")
    }).on("rating.change", function(event, value, caption) {
        alert("You rated your experience as: " + value + "stars");
    });

    $("#input-3-sm").rating().on("rating.clear", function(event) {
        alert("Your rating is reset")
    }).on("rating.change", function(event, value, caption) {
        alert("You rated your experience as: " + value + "stars");
    });

    $("#input-4-sm").rating().on("rating.clear", function(event) {
        alert("Your rating is reset")
    }).on("rating.change", function(event, value, caption) {
        alert("You rated your experience as: " + value + "stars");
    });


});
