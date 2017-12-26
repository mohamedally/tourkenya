$(document).ready(function() {

    // Call Gridder
    $(".gridder").gridderExpander({
        scrollOffset: 60,
        scrollTo: "panel", // "panel" or "listitem"
        animationSpeed: 400,
        animationEasing: "easeInOutExpo",
        onStart: function() {
            console.log("Gridder Inititialized");
        },
        onExpanded: function(object) {
            console.log("Gridder Expanded");
            $(".carousel").carousel();
        },
        onChanged: function(object) {
            console.log("Gridder Changed");
        },
        onClosed: function() {
            console.log("Gridder Closed");
        }
    });
});
