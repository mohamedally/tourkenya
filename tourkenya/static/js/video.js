function progressbar(percent) {
    var szazalek=Math.round((meik*100)/ossz);
    document.getElementById("szliderbar").style.width = percent + '%';
    document.getElementById("szazalek").innerHTML = percent + '%';
}

var elapsedTime = 0;

function timer() {
    if (elapsedTime > 100) {
        document.getElementById("szazalek").style.color = "#FFF";
        document.getElementById("szazalek").innerHTML = "Completed.";
        if (elapsedTime >= 107) {
            clearInterval(interval);
            history.go(-1);
        }
    } else {
        progressbar(elapsedTime);
    }
    elapsedTime++;

}

var myVar = setInterval(function () {
    timer()
}, 100);

function fullScreen() {
    var elem = document.getElementById("Video1");
    var clip = document.getElementById("my-video");
    elem.play();
    clip.pause();
    if (elem.requestFullscreen) {
        elem.requestFullscreen();
    } else if (elem.mozRequestFullScreen) {
        elem.mozRequestFullScreen();
    } else if (elem.webkitRequestFullscreen) {
        elem.webkitRequestFullscreen();
    }
}
$(document).on('webkitExitFullScreen', function () {
    var elem = document.getElementById("Video1");
    var clip = document.getElementById("my-video");
    elem.pause();
    clip.play();
});

function vidplay() {
    var video = document.getElementById("Video1");
    var button = document.getElementById("play");
    if (video.paused) {
        video.play();
        button.textContent = "||";
    } else {
        video.pause();
        button.textContent = ">";
    }
}

function restart() {
    var video = document.getElementById("Video1");
    video.currentTime = 0;
}

function skip(value) {
    var video = document.getElementById("Video1");
    video.currentTime += value;
}
