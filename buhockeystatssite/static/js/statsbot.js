console.log("loading statsbot.js");

document.addEventListener("DOMContentLoaded", function(event) {
if(document.getElementById('card-query').textContent != ""){
  document.getElementById('result-card').style.display  = "block";
}
else{
  document.getElementById('result-card').style.display ="none";
}
});