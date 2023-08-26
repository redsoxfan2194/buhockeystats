console.log("loading daily_trivia.js");
// JavaScript code for handling the form submission and switching screens
const pts=[0,0,0,0,0];
var triviaNum=1;
$(document).ready(function () {
    const lastPlayedTimestamp = localStorage.getItem('lastPlayedTimestamp');
    const savedResultsScreenContent = localStorage.getItem('resultsScreenContent');
    if (lastPlayedTimestamp) {
        const currentTime = new Date().getTime();
        const millisecondsInADay = 24 * 60 * 60 * 1000; // Number of milliseconds in a day

        if (currentTime - parseInt(lastPlayedTimestamp) < millisecondsInADay) {
            // Game has been played today, show results screen
            showScore();
            $("#start-screen").hide();
            $("#results-screen").show();
        } else {
            // Game not played today, show start screen
            $("#start-screen").show();
            $("#results-screen").hide();
        }
    } else {
        // No previous timestamp found, show start screen
        $("#start-screen").show();
        $("#results-screen").hide();
    }
        // Insert saved results-screen content if available
    if (savedResultsScreenContent) {
        $("#results-screen").html(savedResultsScreenContent);
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
                       triviaNum=response.triviaNum;
                       displayQuestion(0, questions);
                    },
                    error: function (xhr, status, error) {
                        console.error("Error:", error);
                    },
                });

        });

    $("#restartBtn").click(function () {
      for(let s = 0; s < 5;s++)
      {
         pts[s]=0;
      }
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
        
        // Save results-screen content to localStorage
        localStorage.setItem('resultsScreenContent', $("#results-screen").html());
        
        // Update lastPlayedTimestamp in localStorage
        localStorage.setItem('lastPlayedTimestamp', new Date().getTime());
      
      } else {
          var question = questions[index];
          $("#questionNumber").text("Question "+(index+1)+" of " + questions.length + ":")
          $("#questionText").text(question.question);
          $("#choices").empty();
          question.choices.forEach(function (choice, idx) {
              var choiceBtn = $("<button>").text(choice).addClass("btn btn-outline-danger choice-btn").data("index", idx);
              $("#choices").append(choiceBtn);
          });
          var wrongCounter = 0;
          var showButtons= false;
          for(let i = 1; i<=3; i++)
          {
            document.getElementById("guess"+i).style.display ='inline-block';
          }
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
                  pts[index]=5-(2*wrongCounter);
                  showButtons=true
              } else {
                  $(this).removeClass("btn-outline-danger").addClass("btn-danger");
                  $(this).prop("disabled", true);
                  // Highlight the correct answer in green
                  wrongCounter+=1;
                  document.getElementById("guess"+wrongCounter).style.display ='none';
              }
              if(wrongCounter>2)
                showButtons=true;
              // Disable all buttons after a selection is made
              if(showButtons)
              {
                disableButtons();
                if(index == questions.length-1){
                  $("#nextBtn").text('See Results')
                }
                else{
                  $("#nextBtn").text('Next Question')
                }
                $("#nextBtn").show().data("index", index).data("questions", questions);
              }
          });

          $("#start-screen").hide();
          $("#results-screen").hide();
          $("#game-screen").show();
          $("#nextBtn").hide();
      }
  }


function showScore() {
  scoreStr = "";
  scoreTot=0;
  for (let i = 0; i < 5; i++) {
  starStr= "";
  for(let s = 0; s < pts[i];s++)
  {
     starStr+="🚨";
     scoreTot+=1;
  }
  if(starStr===""){
     starStr="❌"
  }
  scoreStr += "Question: " + (i + 1) + " " + starStr + '<br>';
  }

  $("#score").html(scoreStr+"\nScore: " + scoreTot+"/25");
}

});

function copyScore() {
  scoreTot=0;
  // Get the text field
  scoreStr="BU Hockey Stats Trivia #"+ triviaNum+ "\n"
  for (let i = 0; i < 5; i++) {
    starStr= "";
    for(let s = 0; s < pts[i];s++)
    {
       starStr+="🚨";
       scoreTot+=1;
    }
    if(starStr===""){
       starStr="❌";
    }
    scoreStr += "Question: " + (i + 1) + " " + starStr + '\n';
  }
   
   // Copy the text inside the text field
  return scoreStr+"\nScore: " + scoreTot+"/25"+'\nbuhockeystats.com/trivia';
} 

const shareButton = document.getElementById('shareBtn');
let tooltipTimeout;

// Function to update the tooltip text
function updateTooltipText(text) {
  const tooltip = new bootstrap.Tooltip(shareButton);
  tooltip.hide();
  tooltip.update();
  shareButton.setAttribute('data-bs-original-title', text);
  tooltip.show();
  clearTimeout(tooltipTimeout);
  tooltipTimeout = setTimeout(() => {
    tooltip.hide();
  }, 2000); // Hide the tooltip after 2 seconds
}

// Function to handle button click event
function handleButtonClick() {
  const textToCopy = copyScore(); 
  const textArea = document.createElement('textarea');
  textArea.value = textToCopy;
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand('copy');
  document.body.removeChild(textArea);

  updateTooltipText('Copied');
  setTimeout(() => {
    updateTooltipText('Copy to clipboard');
  }, 2000);
}

// Add event listeners
shareButton.addEventListener('click', handleButtonClick);
