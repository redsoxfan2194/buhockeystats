console.log("loading home.js");
document.getElementById("randomStatForm").addEventListener("submit", submitForm);
function submitForm(event){
const formData = $("#randomStatForm").serialize();
event.preventDefault();
    $.ajax({
        url: $("#randomStatForm").attr("action"),
        method: $("#randomStatForm").attr("method"),
        data: formData,
        success: function (response) {
        document.getElementById("result").textContent = response.result;
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        },
    });
}

function changeStatsBotImage() {
  document.getElementById('stats-bot-logo').src = '../static/images/statsbotlogo_hover.png';
}

function restoreStatsBotImage() {
  document.getElementById('stats-bot-logo').src = '../static/images/statsbotlogo.png';
}

function changeRecordsImage() {
  document.getElementById('records-logo').src = '../static/images/recordslogo_hover.png';
}

function restoreRecordsImage() {
  document.getElementById('records-logo').src = '../static/images/recordslogo.png';
}

function changePlayersImage() {
  document.getElementById('players-logo').src = '../static/images/jersey_home.png';
}

function changeTidbitsImage() {
  document.getElementById('tidbits-logo').src = '../static/images/tidbits_icon_hover.png';
}

function restoreTidbitsImage() {
  document.getElementById('tidbits-logo').src = '../static/images/tidbits_icon.png';
}

function restorePlayersImage() {
  document.getElementById('players-logo').src = '../static/images/jersey_road.png';
}

function changeHatTricksImage() {
  document.getElementById('hattricks-logo').src = '../static/images/hattricks_icon_hover.png';
}

function restoreHatTricksImage() {
  document.getElementById('hattricks-logo').src = '../static/images/hattricks_icon.png';
}

function changeShutoutsImage() {
  document.getElementById('shutouts-logo').src = '../static/images/shutouts_icon_hover.png';
}

function restoreShutoutsImage() {
  document.getElementById('shutouts-logo').src = '../static/images/shutouts_icon.png';
}

function changeTriviaImage() {
  document.getElementById('trivia-logo').src = '../static/images/trivialogo_hover.png';
}

function restoreTriviaImage() {
  document.getElementById('trivia-logo').src = '../static/images/trivialogo.png';
}

function changeBoxImage() {
  document.getElementById('box-logo').src = '../static/images/box_icon_hover.png';
}

function restoreBoxImage() {
  document.getElementById('box-logo').src = '../static/images/box_icon.png';
}

