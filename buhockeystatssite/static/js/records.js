console.log("loading records.js");
document.addEventListener("DOMContentLoaded", function(event) {
  $('#offset').val("200");
  var alterClass = function() {
    var ww = document.body.clientWidth;
    if (ww < 800) {
      $('#offcanvasRecordsFilters').addClass('offcanvas');
      $('#offcanvasRecordsFilters').addClass('offcanvas-start');
      $('#offcanvasRecordsFilters').removeClass('sidebar-buhs');
      $('#ocRecHeader').removeClass('sidebar-header-center');
      $('#offcanvasRecordsFilters').css("display", "flex");
      
    } else if (ww >= 801) {
      $('#offcanvasRecordsFilters').removeClass('offcanvas');
      $('#offcanvasRecordsFilters').removeClass('offcanvas-start');
      $('#offcanvasRecordsFilters').addClass('sidebar-buhs');
      $('#ocRecHeader').addClass('sidebar-header-center');
    };
  };
  $(window).resize(function(){
    alterClass();
  });
  //Fire it when the page first loads:
  alterClass();
  loadMoreData(); // Load initial data
});

function loadMoreData() {
    let offset = parseInt($('#offset').val());
    $.ajax({
        url: `/load_more/${offset}`,
        success: function(response) {
            $('#resultTable').append(response.data);
            offset += 200;
            $('#offset').val(offset);
            if(response.data != null)
            {
              loadMoreData()
            }
        }
    });
}


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
    document.getElementById("result").value = "all";
    document.getElementById("opponent").value = "all";
    document.getElementById("season").value = "all";
    document.getElementById("buscoreop").value = "==";
    document.getElementById("buscore").value = "";
    document.getElementById("oppscoreop").value = "==";
    document.getElementById("oppscore").value = "";
    document.getElementById("burankop").value = "==";
    document.getElementById("burank").value = "";
    document.getElementById("opprankop").value = "==";
    document.getElementById("opprank").value = "";
    document.getElementById("endYear").value = "{{maxYear}}";

    if (document.getElementById("gender").value === "Womens") {
        document.getElementById("seasonStart").value = "2005-06";
        document.getElementById("startYear").value = 2005;
    } else {
        document.getElementById("seasonStart").value = "1917-18";
        document.getElementById("startYear").value = 1917;
        if(document.getElementById("seasonStart").value==="")
        {
          const option = document.createElement("option");
          option.value = "1917-18";
          option.textContent = "1917-18";
          document.getElementById("seasonStart").appendChild(option);
          document.getElementById("seasonStart").value = "1917-18";
          document.getElementById("startYear").value = 1917;
        }
    }

    document.getElementById("seasonEnd").value = "2024-25";
    document.getElementById("DOW").value = -1;
    document.getElementById("month").value = 0;
    document.getElementById("day").value = 0;
    document.getElementById("tourney").value = "All";
    document.getElementById("conference").value = "all";
    document.getElementById("coach").value = "all";
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

    const buRankInput = document.getElementById("burank");
    buRankInput.addEventListener("keydown", onKeydown);

    const oppRankInput = document.getElementById("opprank");
    oppRankInput.addEventListener("keydown", onKeydown);

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
    $("#offset").val("200");
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
            if (document.getElementById("sortval").value) {
                var thElements = document.getElementsByTagName("th");
                var clickedText = document.getElementById("sortval").value;
                var groupText = document.getElementById("grouping").value;
                for (var i = 0; i < thElements.length; i++) {
                    var th = thElements[i];
                    var thText = th.textContent || th.innerText;
                    if (thText === clickedText || (clickedText === "sort" && thText === groupText)) {
                        var arrow = th.querySelector(".arrow");
                        arrow = document.createElement("span");
                        arrow.className = "arrow";
                        if (
                            document.getElementById("isAscending").value === ""
                        ) {
                            arrow.innerHTML = "";
                        } else {
                            if (
                                document.getElementById("isAscending").value ===
                                "false"
                            ) {
                                arrow.innerHTML = "▲"; // Up arrow unicode
                            } else {
                                arrow.innerHTML = "▼"; // down arrow unicode
                            }
                            th.appendChild(arrow);
                            th.innerHTML += " ";
                        }
                    }
                }
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

                document.getElementById("seasonEnd").value = "2024-25";
                document.getElementById("seasonEnd").text = "2024-25";

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
                
                selectConferenceElement.append(
                    $("<option>", {
                        value: "conf",
                        text: "Conference Games",
                    })
                );
                selectConferenceElement.append(
                    $("<option>", {
                        value: "nc",
                        text: "Non-Conference",
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
                        document.getElementById("sortDiv").hidden = false;
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
                    document.getElementById("sortDiv").hidden = true;
                    
                    
                }
            }
            loadMoreData();
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

 function setSort(header) {
            var columnName = header.innerHTML;
            if(!columnName)
                return;
            var thElements = document.getElementsByTagName('th');
            document.getElementById("sortval").value = columnName.replace("<span class=\"arrow\">▲</span> ","").replace("<span class=\"arrow\">▼</span> ","")
            if(document.getElementById("sortval").value === "")
            {
              document.getElementById("sortval").value="sort";
            }
            // Clear arrow from all other th elements
            for (var i = 0; i < thElements.length; i++) {
                var th = thElements[i];
                if (th !== header) {
                    var arrow = th.querySelector('.arrow');
                    if (arrow) {
                        th.removeChild(arrow);
                        th.innerHTML = th.innerHTML.trim();
                    }
                }
            }

            var arrow = header.querySelector('.arrow');
            if (arrow === null) {
                // Add up arrow
                arrow = document.createElement('span');
                arrow.className = 'arrow';
                arrow.innerHTML = '▼'; // Up arrow unicode

                header.appendChild(arrow);
                header.innerHTML += ' ';
                document.getElementById("isAscending").value = "true";
            } else if (arrow.innerHTML === '▼') {
                // Change to down arrow
                arrow.innerHTML = '▲'; // Down arrow unicode
                document.getElementById("isAscending").value = "false";
            } else {
                // Remove arrow
                header.removeChild(arrow);
                header.innerHTML = header.innerHTML.trim(); // Remove trailing space
                document.getElementById("isAscending").value = "";
                document.getElementById("sortval").value="sort";
            }
            submitForm();
}
