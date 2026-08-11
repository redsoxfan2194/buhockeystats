console.log("loading daily_trivia.js");

// JavaScript code for handling the form submission and switching screens
const pts = [0, 0, 0, 0, 0];
var triviaNum = 1;

$(document).ready(function () {

    // -----------------------------
    // Check if game was already played
    // -----------------------------
    const lastPlayedTimestamp = localStorage.getItem('lastPlayedTimestamp');
    const savedResultsScreenContent = localStorage.getItem('resultsScreenContent');

    if (lastPlayedTimestamp) {
        const currentTime = new Date().getTime();
        const millisecondsInADay = 24 * 60 * 60 * 1000;

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


    // -----------------------------
    // Game options form
    // -----------------------------
    $("#game-options-form").submit(function (event) {
        event.preventDefault();

        var formData = $(this).serializeArray();
        var questions = [];

        $.ajax({
            url: $("#game-options-form").attr("action"),
            method: $("#game-options-form").attr("method"),
            data: formData,

            success: function (response) {
                questions = response.quiz;
                triviaNum = response.triviaNum;

                displayQuestion(0, questions);
            },

            error: function (xhr, status, error) {
                console.error("Error:", error);
            }
        });
    });


    // -----------------------------
    // Restart button
    // -----------------------------
    $("#restartBtn").click(function () {

        for (let s = 0; s < 5; s++) {
            pts[s] = 0;
        }

        index = 0;

        $("#results-screen").hide();
        $("#game-screen").hide();
        $("#start-screen").show();
    });


    // -----------------------------
    // Next button
    // -----------------------------
    $("#nextBtn").click(function () {

        var index = $(this).data("index");
        var questions = $(this).data("questions");

        displayQuestion(index + 1, questions);
    });


    // -----------------------------
    // Display question
    // -----------------------------
    function displayQuestion(index, questions) {

        if (index >= questions.length) {

            // All questions answered, show results screen
            $("#game-screen").hide();
            $("#results-screen").show();

            showScore();

            // Save results-screen content to localStorage
            localStorage.setItem(
                'resultsScreenContent',
                $("#results-screen").html()
            );

            // Update lastPlayedTimestamp in localStorage
            localStorage.setItem(
                'lastPlayedTimestamp',
                new Date().getTime()
            );

        } else {

            var question = questions[index];

            $("#questionNumber").text(
                "Question " + (index + 1) + " of " + questions.length + ":"
            );

            $("#questionText").text(question.question);

            $("#choices").empty();

            question.choices.forEach(function (choice, idx) {

                var choiceBtn = $("<button>")
                    .text(choice)
                    .addClass("btn btn-outline-danger choice-btn")
                    .data("index", idx);

                $("#choices").append(choiceBtn);
            });


            var wrongCounter = 0;
            var showButtons = false;


            // Show guess buttons
            for (let i = 1; i <= 3; i++) {
                document.getElementById("guess" + i).style.display = 'inline-block';
            }


            // Disable all buttons after a selection is made
            function disableButtons() {
                $(".choice-btn").prop("disabled", true);
            }


            // Answer selection
            $(".choice-btn").click(function () {

                var selectedChoice = $(this).data("index");
                var correctAnswer = question.correctAnswer;


                // Correct answer
                if (selectedChoice === correctAnswer) {

                    $(this)
                        .removeClass("btn-outline-danger")
                        .addClass("btn-success");

                    pts[index] = 5 - (2 * wrongCounter);

                    showButtons = true;

                }

                // Wrong answer
                else {

                    $(this)
                        .removeClass("btn-outline-danger")
                        .addClass("btn-danger");

                    $(this).prop("disabled", true);

                    wrongCounter += 1;

                    document.getElementById(
                        "guess" + wrongCounter
                    ).style.display = 'none';
                }


                // Three wrong guesses
                if (wrongCounter > 2) {
                    showButtons = true;
                }


                // Show next button
                if (showButtons) {

                    disableButtons();

                    if (index == questions.length - 1) {
                        $("#nextBtn").text("See Results");
                    } else {
                        $("#nextBtn").text("Next Question");
                    }

                    $("#nextBtn")
                        .show()
                        .data("index", index)
                        .data("questions", questions);
                }
            });


            // Switch screens
            $("#start-screen").hide();
            $("#results-screen").hide();
            $("#game-screen").show();

            $("#nextBtn").hide();
        }
    }


    // -----------------------------
    // Show score
    // -----------------------------
    function showScore() {

        let scoreStr = "";
        let scoreTot = 0;

        for (let i = 0; i < 5; i++) {

            let starStr = "";

            for (let s = 0; s < pts[i]; s++) {
                starStr += "🚨";
                scoreTot += 1;
            }

            if (starStr === "") {
                starStr = "❌";
            }

            scoreStr +=
                "Question: " +
                (i + 1) +
                " " +
                starStr +
                "<br>";
        }

        $("#score").html(
            scoreStr + "\nScore: " + scoreTot + "/25"
        );
    }


    // -----------------------------
    // Copy score text
    // -----------------------------
    function copyScore() {

        let scoreTot = 0;

        let scoreStr =
            "BU Hockey Stats Trivia #" +
            triviaNum +
            "\n";

        for (let i = 0; i < 5; i++) {

            let starStr = "";

            for (let s = 0; s < pts[i]; s++) {
                starStr += "🚨";
                scoreTot += 1;
            }

            if (starStr === "") {
                starStr = "❌";
            }

            scoreStr +=
                "Question: " +
                (i + 1) +
                " " +
                starStr +
                "\n";
        }

        return (
            scoreStr +
            "\nScore: " +
            scoreTot +
            "/25" +
            "\nbuhockeystats.com/trivia"
        );
    }


    // -----------------------------
    // Share button / tooltip
    // -----------------------------
    const shareButton = document.getElementById("shareBtn");

    if (shareButton) {

        // Initialize Bootstrap tooltip
        const tooltip = new bootstrap.Tooltip(shareButton);


        shareButton.addEventListener("click", async function () {

            try {

                // Get score text
                const textToCopy = copyScore();

                // Copy to clipboard
                await navigator.clipboard.writeText(textToCopy);


                // Change tooltip text
                shareButton.setAttribute(
                    "data-bs-original-title",
                    "Copied!"
                );

                // Show tooltip
                tooltip.show();


                // Change tooltip back after 2 seconds
                setTimeout(function () {

                    tooltip.hide();

                    shareButton.setAttribute(
                        "data-bs-original-title",
                        "Copy to clipboard"
                    );

                }, 2000);


            } catch (err) {

                console.error(
                    "Failed to copy score:",
                    err
                );

            }

        });
    }

});