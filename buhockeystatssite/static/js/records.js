console.log("loading records.js");

const onKeydown = function (event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent form submission
        submitForm();
    }
};
initializeFilters();
function clearFilers(event) {
    document.getElementById("arena").value = "all";
    document.getElementById("location").value = "all";
    document.getElementById("opponent").value = "all";
    document.getElementById("season").value = "all";
    document.getElementById("buscoreop").value = "==";
    document.getElementById("buscore").value = "";
    document.getElementById("oppscoreop").value = "==";
    document.getElementById("oppscore").value = "";
    document.getElementById("endYear").value = "{{maxYear}}";

    if (document.getElementById("gender").value === "Womens") {
        document.getElementById("seasonStart").value = "2005-06";
        document.getElementById("startYear").value = 2005;
    } else {
        const option = document.createElement("option");
        option.value = "1917-18";
        option.textContent = "1917-18";
        document.getElementById("seasonStart").appendChild(option);
        document.getElementById("seasonStart").value = "1917-18";
        document.getElementById("startYear").value = 1917;
    }

    document.getElementById("seasonEnd").value = "2022-23";
    document.getElementById("DOW").value = -1;
    document.getElementById("month").value = 0;
    document.getElementById("day").value = 0;
    document.getElementById("tourney").value = "All";
    document.getElementById("conference").value = "all";
    document.getElementById("coach").value = "all";
    document.getElementById("tabletype").value = "";
    document.getElementById("grouping").value = "Opponent";
    document.getElementById("grouping").hidden = true;
    document.getElementById("groupLabel").hidden = true;
    if(event!=null){
      event.preventDefault();
      submitForm("true");
    }
}

function toggleArrow() {
    var arrowUp = document.getElementById("arrowUp");
    var arrowDown = document.getElementById("arrowDown");
    var arrowStateField = document.getElementById("isAscending");

    if (arrowStateField.value.toLowerCase() === "true") {
        arrowDown.style.display = "none";
        arrowUp.style.display = "inline-block";
        document.getElementById("isAscending").value = false;
    } else {
        arrowUp.style.display = "none";
        arrowDown.style.display = "inline-block";
        document.getElementById("isAscending").value = true;
    }

    submitForm();
}

function toggleDropdowns() {
    var selection = document.getElementById("range").value;

    var sYear = document.getElementById("startYear");
    var eYear = document.getElementById("endYear");
    var sSeason = document.getElementById("seasonStart");
    var eSeason = document.getElementById("seasonEnd");

    if (selection === "year") {
        sYear.style.display = "block";
        eYear.style.display = "block";
        sYear.disabled = false;
        eYear.disabled = false;
        sSeason.style.display = "none";
        eSeason.style.display = "none";
        sSeason.disabled = true;
        eSeason.disabled = true;
    } else if (selection === "season") {
        sYear.style.display = "none";
        eYear.style.display = "none";
        sYear.disabled = true;
        eYear.disabled = true;
        sSeason.style.display = "block";
        eSeason.style.display = "block";
        sSeason.disabled = false;
        eSeason.disabled = false;
    } else {
        sSeason.style.display = "block";
        eSeason.style.display = "block";
        sYear.style.display = "block";
        eYear.style.display = "block";
        sSeason.disabled = false;
        eSeason.disabled = false;
        sYear.disabled = false;
        eYear.disabled = false;
    }
}
function initializeFilters() {
    document
        .getElementById("resetButton")
        .addEventListener("click", clearFilers);

    const buScoreInput = document.getElementById("buscore");
    buScoreInput.addEventListener("keydown", onKeydown);

    const oppScoreInput = document.getElementById("oppscore");
    oppScoreInput.addEventListener("keydown", onKeydown);

    const sYearInput = document.getElementById("startYear");
    sYearInput.addEventListener("keydown", onKeydown);

    const eYearInput = document.getElementById("endYear");
    eYearInput.addEventListener("keydown", onKeydown);

    document.getElementById("grouping").hidden = true;
    document.getElementById("groupLabel").hidden = true;

    var select = document.getElementById("sortval");
    const optionToHide = document.querySelectorAll(".rec-sort");

    // Hide all rec-sort elements
    for (let i = 0; i < optionToHide.length; i++) {
        optionToHide[i].classList.add("hidden");
    }

    var arrowStateField = document.getElementById("isAscending");
    if (arrowStateField.value === "True") {
        arrowUp.style.display = "none";
        arrowDown.style.display = "inline-block";
    } else {
        arrowUp.style.display = "inline-block";
        arrowDown.style.display = "none";
    }

    var checkbox = document.getElementById("hideEx");
    var checkboxState = document.getElementById("hideExStatus");
    checkbox.checked = checkboxState.value === "true";

    var selection = document.getElementById("range").value;
    var sYear = document.getElementById("startYear");
    var eYear = document.getElementById("endYear");
    var sSeason = document.getElementById("seasonStart");
    var eSeason = document.getElementById("seasonEnd");
    if (selection === "year") {
        sYear.style.display = "block";
        eYear.style.display = "block";
        sYear.disabled = false;
        eYear.disabled = false;
        sSeason.style.display = "none";
        eSeason.style.display = "none";
        sSeason.disabled = true;
        eSeason.disabled = true;
    } else if (selection === "season") {
        sYear.style.display = "none";
        eYear.style.display = "none";
        sYear.disabled = true;
        eYear.disabled = true;
        sSeason.style.display = "block";
        eSeason.style.display = "block";
        sSeason.disabled = false;
        eSeason.disabled = false;
    } else {
        sSeason.style.display = "block";
        eSeason.style.display = "block";
        sYear.style.display = "block";
        eYear.style.display = "block";
        sSeason.disabled = false;
        eSeason.disabled = false;
        sYear.disabled = false;
        eYear.disabled = false;
    }

    // Add event listener to the month dropdown
    document.getElementById("month").addEventListener("change", populateDays);
    clearFilers();
}

function submitForm(reset = "false") {
    const formData = $("#resForm").serialize();
    var recSort = document.querySelectorAll(".rec-sort");
    var resSort = document.querySelectorAll(".res-sort");

    $.ajax({
        url: $("#resForm").attr("action"),
        method: $("#resForm").attr("method"),
        data: formData,
        success: function (response) {
            $("#resultTable").html(response.resTable);
            $("#record").html("Record: " + response.result);

            if (!document.getElementById("tabletype").value) {
                document.getElementById("grouping").hidden = true;
                document.getElementById("groupLabel").hidden = true;
            } else {
                document.getElementById("grouping").hidden = false;
                document.getElementById("groupLabel").hidden = false;
            }

            if (reset === "true") {
                document.getElementById("startYear").value = response.minYear;
                document.getElementById("startYear").min = response.minYear;
                document.getElementById("startYear").placeholder =
                    response.minYear;

                const selectSeasElement = $("#season");
                selectSeasElement.empty();
                selectSeasElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.season_values, function (index, item) {
                    selectSeasElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectseasStartElement = $("#seasonStart");
                selectseasStartElement.empty();
                $.each(response.season_values, function (index, item) {
                    selectseasStartElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectseasEndElement = $("#seasonEnd");
                selectseasEndElement.empty();
                $.each(response.season_values, function (index, item) {
                    selectseasEndElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                document.getElementById("seasonEnd").value = "2022-23";
                document.getElementById("seasonEnd").text = "2022-23";

                const selectArenaElement = $("#arena");
                selectArenaElement.empty();
                selectArenaElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.arena_values, function (index, item) {
                    selectArenaElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });
                
                const selectConferenceElement = $("#conference");
                selectConferenceElement.empty();
                selectConferenceElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.conference_values, function (index, item) {
                    selectConferenceElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectOppElement = $("#opponent");
                selectOppElement.empty();
                selectOppElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.opponents_values, function (index, item) {
                    selectOppElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectCoachElement = $("#coach");
                selectCoachElement.empty();
                selectCoachElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.coach_values, function (index, item) {
                    selectCoachElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectTourneyElement = $("#tourney");
                selectTourneyElement.empty();
                $.each(response.tourney_values, function (index, item) {
                    selectTourneyElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                if (document.getElementById("tabletype").value != "record") {
                    if (resSort[0].classList.contains("hidden")) {
                        // Hide all rec-sort elements
                        for (let i = 0; i < recSort.length; i++) {
                            recSort[i].classList.add("hidden");
                        }

                        // show all res-sort elements
                        for (let i = 0; i < resSort.length; i++) {
                            resSort[i].classList.remove("hidden");
                        }
                        document.getElementById("sortval").value = "date";
                    }
                } else {
                    // Hide all res-sort elements
                    for (let i = 0; i < resSort.length; i++) {
                        resSort[i].classList.add("hidden");
                    }
                    // show all rec-sort elements
                    for (let i = 0; i < recSort.length; i++) {
                        recSort[i].classList.remove("hidden");
                    }
                    document.getElementById("sortval").value = "sort";
                }
            }
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        },
    });
}

// Function to populate the days based on the selected month
function populateDays() {
    const monthSelect = document.getElementById("month");
    const daySelect = document.getElementById("day");
    const selectedMonth = parseInt(monthSelect.value);
    const daysInMonth = new Date(2020, selectedMonth, 0).getDate();

    if (selectedMonth === 0) {
        daySelect.innerHTML = ""; // Clear the day dropdown
        const defaultOption = document.createElement("option");
        defaultOption.value = 0;
        defaultOption.textContent = "All";
        defaultOption.selected = true;
        daySelect.appendChild(defaultOption);
        return;
    }

    daySelect.innerHTML = ""; // Clear the day dropdown

    // Add default "Day" option
    const defaultOption = document.createElement("option");
    defaultOption.value = 0;
    defaultOption.textContent = "All";
    defaultOption.selected = true;
    daySelect.appendChild(defaultOption);

    // Add options for each day
    for (let i = 1; i <= daysInMonth; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = i;

        if (i === parseInt(daySelect.value)) {
            option.selected = true; // Mark the option as selected
        }

        daySelect.appendChild(option);
    }
}
