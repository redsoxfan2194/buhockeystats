
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
          

          function displayQuestion(index, questions) {
              if (index >= questions.length) {
                  // All questions answered, show results screen
                  $("#game-screen").hide();
                  $("#results-screen").show();
                  showScore(scoreNum);
              } else {
                  var question = questions[index];
                  $("#questionNumber").text("Question "+(index+1)+":")
                  $("#questionText").text(question.question);
                  $("#choices").empty();
                  question.choices.forEach(function (choice, idx) {
                      var choiceBtn = $("<button>").text(choice).addClass("btn btn-secondary choice-btn").data("index", idx);
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
                          $(this).removeClass("btn-secondary").addClass("btn-success");
                          scoreNum=scoreNum+1;
                      } else {
                          $(this).removeClass("btn-secondary").addClass("btn-danger");
                          // Highlight the correct answer in green
                          $(".choice-btn").eq(correctAnswer).removeClass("btn-secondary").addClass("btn-success");
                      }

                      // Disable all buttons after a selection is made
                      disableButtons();

                      $("#nextBtn").show().data("index", index).data("questions", questions);
                  });

                  $("#start-screen").hide();
                  $("#results-screen").hide();
                  $("#game-screen").show();
                  $("#nextBtn").hide();
              }
          }


            function showScore(score) {
                $("#score").text("Your Score: " + score);
            }

        });
