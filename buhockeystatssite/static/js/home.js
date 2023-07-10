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
  document.getElementById('stats-bot-logo').src = '../static/images/statsbotlogo_hover.ico';
}

function restoreStatsBotImage() {
  document.getElementById('stats-bot-logo').src = '../static/images/statsbotlogo.ico';
}

function changeRecordsImage() {
  document.getElementById('records-logo').src = '../static/images/recordslogo_hover.ico';
}

function restoreRecordsImage() {
  document.getElementById('records-logo').src = '../static/images/recordslogo.ico';
}

function changePlayersImage() {
  document.getElementById('players-logo').src = '../static/images/jersey_home.ico';
}

function restorePlayersImage() {
  document.getElementById('players-logo').src = '../static/images/jersey_road.ico';
}