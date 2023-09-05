document.getElementById("stop_alarm").addEventListener("click", stop_alarm);

function stop_alarm() {
    var alarm_sound= document.getElementById('alarm_sound');
    alarm_sound.pause();
    alarm_sound.currentTime = 0;
}

function play_alarm() {
   var alarm_sound= document.getElementById('alarm_sound');

    if (alarm_sound.paused) {
        alarm_sound.currentTime = 0; // Start from the beginning
        alarm_sound.play();
    }
}