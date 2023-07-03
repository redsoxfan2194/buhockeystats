console.log("loading statsbot.js");
function openHelpImage() {
  window.open(
    "{{ url_for('static', filename='images/statsbotcheatsheet.png') }}",
    "_blank"
  );
}