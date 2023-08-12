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

function restorePlayersImage() {
  document.getElementById('players-logo').src = '../static/images/jersey_road.png';
}

function changeTriviaImage() {
  document.getElementById('trivia-logo').src = '../static/images/trivialogo_hover.png';
}

function restoreTriviaImage() {
  document.getElementById('trivia-logo').src = '../static/images/trivialogo.png';
}