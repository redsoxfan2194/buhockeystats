console.log("loading players.js");
initializeFilters();
function onKeydown(event) {
    if (event.key === "Enter") {
        event.preventDefault(); // Prevent form submission
        submitForm();
    }
}

function onClick() {
    if (hiddenDiv.style.display === "none" || hiddenDiv.style.display === "") {
        hiddenDiv.style.display = "block";
    } else {
        hiddenDiv.style.display = "none";
    }
}

function clearFilters(event) {
    event.preventDefault();
    document.getElementById("pos").value = "all";
    document.getElementById("yr").value = "all";
    document.getElementById("season").value = "all";
    document.getElementById("opponent").value = "all";

    if (document.getElementById("gender").value === "Womens") {
        document.getElementById("seasonStart").value = "2005-06";
    } else if (document.getElementById("type").value !== "game") {
        const option = document.createElement("option");
        option.value = "1917-18";
        option.textContent = "1917-18";
        document.getElementById("seasonStart").appendChild(option);
        document.getElementById("seasonStart").value = "1917-18";
    } else {
        const option = document.createElement("option");
        option.value = "2002-03";
        option.textContent = "2002-03";
        document.getElementById("seasonStart").appendChild(option);
        document.getElementById("seasonStart").value = "2002-03";
    }

    document.getElementById("seasonEnd").value = "2022-23";
    document.getElementById("sortval").value = "";
    document.getElementById("isAscending").value = "";
    document.getElementById("name").value = "";
    document.getElementById("number").value = "Number";
    document.getElementById("date").value = "Date";
    document.getElementById("group").value = "";
    submitForm("true");
}

function initializeFilters() {
    const nameInput = document.getElementById("name");
    nameInput.addEventListener("keydown", onKeydown);

    const numberInput = document.getElementById("number");
    numberInput.addEventListener("keydown", onKeydown);

    const dateInput = document.getElementById("date");
    dateInput.addEventListener("keydown", onKeydown);

    document
        .getElementById("resetButton")
        .addEventListener("click", clearFilters);

    var mobileButton = document.getElementById("filterMenu");
    mobileButton.addEventListener("click", onClick);
}

function submitForm(reset = "false") {
    const formData = $("#playerForm").serialize();

    $.ajax({
        url: $("#playerForm").attr("action"),
        method: $("#playerForm").attr("method"),
        data: formData,
        success: function (response) {
            $("#statTable").html(response.statTable);
            $("#sortval").value = response.sortval;

            if (reset === "true") {
                const selectSeasElement = $("#season");
                selectSeasElement.empty();
                selectSeasElement.append(
                    $("<option>", {
                        value: "all",
                        text: "Season",
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

                const selectOppElement = $("#opponent");
                selectOppElement.empty();
                selectOppElement.append(
                    $("<option>", {
                        value: "all",
                        text: "Opponent",
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
            }

            if (document.getElementById("sortval").value) {
                var thElements = document.getElementsByTagName("th");
                var clickedText = document.getElementById("sortval").value;

                for (var i = 0; i < thElements.length; i++) {
                    var th = thElements[i];
                    var thText = th.textContent || th.innerText;
                    if (thText === clickedText) {
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

            var positionSelect = document.querySelector(
                'select[name="position"]'
            );
            var typeSelect = document.querySelector('select[name="type"]');
            var seasonStats = document.getElementsByClassName("season-stats");
            var gameStats = document.getElementsByClassName("game-stats");

            // Hide all season stats
            const statsElements = document.querySelectorAll(
                ".season-stats, .game-stats"
            );

            // Hide all stats elements
            for (let i = 0; i < statsElements.length; i++) {
                statsElements[i].classList.add("hidden");
            }

            // Show stats elements based on the selected type
            if (typeSelect.value === "season") {
                for (let i = 0; i < seasonStats.length; i++) {
                    seasonStats[i].classList.remove("hidden");
                }
            } else if (typeSelect.value === "game") {
                // Do nothing for game stats
                for (let i = 0; i < gameStats.length; i++) {
                    gameStats[i].classList.remove("hidden");
                }
            }

            if (positionSelect.value === "goalie") {
                document.getElementById("pos").hidden = true;
            } else {
                document.getElementById("pos").hidden = false;
            }
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        },
    });
}