console.log("loading trivia.js");
$("input[name='gender']").change(function () {
  var gender = $(this).val();

  // Set different start years based on gender selection
  if (gender === "Womens") {
      document.getElementById("seasonStart").value = "2005-06";
  } else if (gender === "Mens") {
      document.getElementById("seasonStart").value = "1917-18";
  }
});

let scoreNum=0;
// JavaScript code for handling the form submission and switching screens
$(document).ready(function () {
    function clearOptions() {
        $("input[name='gender']").prop("checked", false);
        $("input[name='options']").prop("checked", false);

    }
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
        var quesNums = $("#numQuestions").val();
        $("#numQuesDisplay").text("Number of Questions: " + quesNums);

    $("#restartBtn").click(function () {
        clearOptions();
        $("#results-screen").hide();
        $("#game-screen").hide();
        $("#start-screen").show();
    });

    $("#nextBtn").click(function () {
        var index = $(this).data("index");
        var questions = $(this).data("questions");
        displayQuestion(index + 1, questions);
    });
  
    $("#numQuestions").on("input", function () {
        var quesNums = $(this).val();
        $("#numQuesDisplay").text("Number of Questions: " + quesNums);
    });

  function displayQuestion(index, questions) {
      if (index >= questions.length) {
          // All questions answered, show results screen
          $("#game-screen").hide();
          $("#results-screen").show();
          showScore(scoreNum,questions.length);
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
                  $(".choice-btn").eq(correctAnswer).removeClass("btn-outline-danger").addClass("btn-success");
              }

              // Disable all buttons after a selection is made
              disableButtons();
              if(index == questions.length-1){
                $("#nextBtn").text('See Results')
              }
              $("#nextBtn").show().data("index", index).data("questions", questions);
          });

          $("#start-screen").hide();
          $("#results-screen").hide();
          $("#game-screen").show();
          $("#nextBtn").hide();
      }
  }


    function showScore(score,numQuestions) {
        var ranking=''
        $("#score").text("Your Score: " + score);

        if ((score == 0 && numQuestions <= 20) || (numQuestions > 20 && score <= 0.1 * numQuestions)) {
          ranking = 'Eagle';
        } else if ((score <= 5 && numQuestions <= 20) || (numQuestions > 20 && (score > 0.1 * numQuestions && score <= 0.25 * numQuestions))) {
          ranking = '4th Liner';
        } else if ((score <= 10 && numQuestions <= 20) || (numQuestions > 20 && (score > 0.25 * numQuestions && score <= 0.5 * numQuestions))) {
          ranking = 'Starter';
        } else if ((score > 10 && numQuestions <= 20) || (numQuestions >= 20 && (score > 0.5 * numQuestions && score <= 0.75 * numQuestions))) {
          ranking = 'All-Conference';
        } else if (numQuestions > 20 && (score > 0.75 * numQuestions && score <= 0.9 * numQuestions)) {
          ranking = 'All-American';
        } else if (numQuestions >= 25 && score == numQuestions) {
          ranking = 'Bernie Corbett';
        } else {
          if($("input[name='gender']").val() === "Womens") {
            ranking = 'Patty Kazmaier Winner';
          } else {
            ranking = 'Hobey Baker Winner';
          }
        }
        
        $("#rank").text("Your Rank: " + ranking);
    }

});
