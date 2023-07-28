console.log("loading trivia_challenge.js");
// JavaScript code for handling the form submission and switching screens
var scoreNum=0;
$(document).ready(function () {

        $("#game-options-form").submit(function (event) {
            event.preventDefault();
            var formData = $(this).serializeArray();
            var questions=[];
            $.ajax({
                    url: $("#game-options-form").attr("action"),
                    method: $("#game-options-form").attr("method"),
                    data: formData,
                    success: function (response) {
                       questions=response.quiz;
                       displayQuestion(0, questions);
                    },
                    error: function (xhr, status, error) {
                        console.error("Error:", error);
                    },
                });

        });

    $("#restartBtn").click(function () {
        scoreNum=0;
        index=0;
        $("#results-screen").hide();
        $("#game-screen").hide();
        $("#start-screen").show();
    });

    $("#nextBtn").click(function () {
        var index = $(this).data("index");
        var questions = $(this).data("questions");
        displayQuestion(index + 1, questions);
    });
  
  function displayQuestion(index, questions) {
      if (index >= questions.length) {
          // All questions answered, show results screen
          $("#game-screen").hide();
          $("#results-screen").show();
          showScore();
      } else {
          var question = questions[index];
          $("#questionNumber").text("Question "+(index+1)+" of " + questions.length + ":")
          $("#questionText").text(question.question);
          $("#choices").empty();
          question.choices.forEach(function (choice, idx) {
              var choiceBtn = $("<button>").text(choice).addClass("btn btn-outline-danger choice-btn").data("index", idx);
              $("#choices").append(choiceBtn);
          });

          // Disable all buttons after a selection is made
          function disableButtons() {
              $(".choice-btn").prop("disabled", true);
          }

          $(".choice-btn").click(function () {
              var selectedChoice = $(this).data("index");
              var correctAnswer = question.correctAnswer;

              // Check if the selected answer is correct
              if (selectedChoice === correctAnswer) {
                  $(this).removeClass("btn-outline-danger").addClass("btn-success");
                  scoreNum=scoreNum+1;
              } else {
                  $(this).removeClass("btn-outline-danger").addClass("btn-danger");
                  // Highlight the correct answer in green
              }

              // Disable all buttons after a selection is made
              disableButtons();
              if(index == questions.length-1){
                $("#nextBtn").text('See Results')
              }
              else{
                $("#nextBtn").text('Next Question')
              }
              $("#nextBtn").show().data("index", index).data("questions", questions);
          });

          $("#start-screen").hide();
          $("#results-screen").hide();
          $("#game-screen").show();
          $("#nextBtn").hide();
      }
  }


    function showScore() {
        $("#score").text("Your Score: " + scoreNum);
    }

});
