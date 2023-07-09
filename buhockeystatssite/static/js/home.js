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
        console.log(response.result);
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        },
    });
}