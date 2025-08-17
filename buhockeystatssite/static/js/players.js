console.log("loading players.js");

document.addEventListener("DOMContentLoaded", function(event) {
  var alterClass = function() {
    var ww = document.body.clientWidth;
    if (ww < 800) {
      $('#offcanvasPlayersFilters').addClass('offcanvas');
      $('#offcanvasPlayersFilters').addClass('offcanvas-start');
      $('#offcanvasPlayersFilters').removeClass('sidebar-buhs');
      $('#ocPlayerHeader').removeClass('sidebar-header-center');
      $('#offcanvasPlayersFilters').css("display", "flex");
 
    } else if (ww >= 801) {
      $('#offcanvasPlayersFilters').removeClass('offcanvas');
      $('#offcanvasPlayersFilters').removeClass('offcanvas-start');
      $('#offcanvasPlayersFilters').addClass('sidebar-buhs');
      $('#ocPlayerHeader').addClass('sidebar-header-center');
    };
  };
  $(window).resize(function(){
    alterClass();
  });
  //Fire it when the page first loads:
  alterClass();
});

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
    document.getElementById("pos").value = "all";
    document.getElementById("yr").value = "all";
    document.getElementById("season").value = "all";
    document.getElementById("opponent").value = "all";
    document.getElementById("arena").value = "all";
    document.getElementById("location").value = "all";

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
        option.value = "1917-18";
        option.textContent = "1917-18";
        document.getElementById("seasonStart").appendChild(option);
        document.getElementById("seasonStart").value = "1917-18";
    }

    document.getElementById("seasonEnd").value = "2024-25";
    if(document.getElementById("seasonEnd").value===""){
      document.getElementById("seasonEnd").value = "2024-25";
    }
    document.getElementById("sortval").value = "";
    document.getElementById("isAscending").value = "";
    document.getElementById("name").value = "";
    document.getElementById("number").value = "";
    document.getElementById("date").value = "";
    document.getElementById("group").value = "";
    document.getElementById("streak").value = "pts";
    // Reset Min Filters
    document.getElementById("gpmin").value = "";
    document.getElementById("goalmin").value = "";
    document.getElementById("assistmin").value = "";
    document.getElementById("ptsmin").value = "";
    document.getElementById("pensmin").value = "";
    document.getElementById("pimmin").value  = "";
    document.getElementById("minsmin").value = "";
    document.getElementById("gamin").value = "";
    document.getElementById("savesmin").value = "";
    document.getElementById("gpop").value = "==";
    document.getElementById("goalop").value = "==";
    document.getElementById("assistop").value = "==";
    document.getElementById("ptsop").value = "==";
    document.getElementById("pensop").value = "==";
    document.getElementById("pimop").value  = "==";
    document.getElementById("minsop").value = "==";
    document.getElementById("gaop").value = "==";
    document.getElementById("savesop").value = "==";
    if(event!=null){
      event.preventDefault();
      submitForm("true");
    }
}

function initializeFilters() {
    const nameInput = document.getElementById("name");
    nameInput.addEventListener("keydown", onKeydown);

    const numberInput = document.getElementById("number");
    numberInput.addEventListener("keydown", onKeydown);

    const dateInput = document.getElementById("date");
    dateInput.addEventListener("keydown", onKeydown);
    
    document.getElementById("gpmin").addEventListener("keydown", onKeydown);
    document.getElementById("goalmin").addEventListener("keydown", onKeydown);
    document.getElementById("assistmin").addEventListener("keydown", onKeydown);
    document.getElementById("ptsmin").addEventListener("keydown", onKeydown);
    document.getElementById("pensmin").addEventListener("keydown", onKeydown);
    document.getElementById("pimmin").addEventListener("keydown", onKeydown);
    document.getElementById("minsmin").addEventListener("keydown", onKeydown);
    document.getElementById("gamin").addEventListener("keydown", onKeydown);
    document.getElementById("savesmin").addEventListener("keydown", onKeydown);

    document
        .getElementById("resetButton")
        .addEventListener("click", clearFilters);

    // Hide all season stats
    const seasStatsElements = document.getElementsByClassName("season-stats");

    // Hide all stats elements
    for (let i = 0; i < seasStatsElements.length; i++) {
        seasStatsElements[i].classList.add("hidden");
    }
    
       // Hide all season stats
    const gameStatsElements = document.getElementsByClassName("game-stats");

    // Hide all stats elements
    for (let i = 0; i < gameStatsElements.length; i++) {
        gameStatsElements[i].classList.add("hidden");
    }
    document.getElementById("streakDiv").hidden = true;
    document.getElementById("streakMinDiv").hidden = true;
    var positionSelect = document.querySelector(
        'select[name="position"]'
    );
    var typeSelect = document.querySelector('select[name="type"]');
        if (positionSelect.value === "goalie") {
        document.getElementById("posDiv").hidden = true;
        document.getElementById("goalDiv").hidden = true;
        document.getElementById("assistsDiv").hidden = true;
        document.getElementById("ptsDiv").hidden = true;
        document.getElementById("gaDiv").hidden = false;
        document.getElementById("savesDiv").hidden = false;
        document.getElementById("minsDiv").hidden = false;
    } else {
        document.getElementById("posDiv").hidden = false;
        document.getElementById("goalDiv").hidden = false;
        document.getElementById("assistsDiv").hidden = false;
        document.getElementById("ptsDiv").hidden = false;
        document.getElementById("gaDiv").hidden = true;
        document.getElementById("savesDiv").hidden = true;
        document.getElementById("minsDiv").hidden = true;
    }
    if(typeSelect.value === "game" || positionSelect.value === "goalie")
    {
        document.getElementById("pensDiv").hidden = true;
        document.getElementById("pimDiv").hidden = true;
      
    }
    else{
        document.getElementById("pensDiv").hidden = false;
        document.getElementById("pimDiv").hidden = false;
    }

    clearFilters();
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
                document.getElementById("seasonEnd").value = response.season_values[response.season_values.length-1];
                document.getElementById("seasonEnd").text = response.season_values[response.season_values.length-1];

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
                
                const selectArenaElement   = $("#arena");
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
            const seasStatsElements = document.getElementsByClassName("season-stats");

            // Hide all stats elements
            for (let i = 0; i < seasStatsElements.length; i++) {
                seasStatsElements[i].classList.add("hidden");
            }
            
               // Hide all season stats
            const gameStatsElements = document.getElementsByClassName("game-stats");

            // Hide all stats elements
            for (let i = 0; i < gameStatsElements.length; i++) {
                gameStatsElements[i].classList.add("hidden");
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
            if(document.getElementById("group").value != "" && document.getElementById("group").value != "opponent")
            {
                document.getElementById("gpDiv").hidden = true;
                document.getElementById("goalDiv").hidden = true;
                document.getElementById("assistsDiv").hidden = true;
                document.getElementById("ptsDiv").hidden = true;
                document.getElementById("gaDiv").hidden = true;
                document.getElementById("savesDiv").hidden = true;
                document.getElementById("minsDiv").hidden = true;
                document.getElementById("pensDiv").hidden = true;
                document.getElementById("pimDiv").hidden = true;  
            } else {
              if (positionSelect.value === "goalie") {
                  document.getElementById("gpDiv").hidden = false;
                  document.getElementById("posDiv").hidden = true;
                  document.getElementById("goalDiv").hidden = true;
                  document.getElementById("assistsDiv").hidden = true;
                  document.getElementById("ptsDiv").hidden = true;
                  document.getElementById("gaDiv").hidden = false;
                  document.getElementById("savesDiv").hidden = false;
                  document.getElementById("minsDiv").hidden = false;
                  document.getElementById("pensDiv").hidden = true;
                  document.getElementById("pimDiv").hidden = true;
              } else {
                  document.getElementById("gpDiv").hidden = false;
                  document.getElementById("posDiv").hidden = false;
                  document.getElementById("goalDiv").hidden = false;
                  document.getElementById("assistsDiv").hidden = false;
                  document.getElementById("ptsDiv").hidden = false;
                  document.getElementById("gaDiv").hidden = true;
                  document.getElementById("savesDiv").hidden = true;
                  document.getElementById("minsDiv").hidden = true;
                  document.getElementById("pensDiv").hidden = false;
                  document.getElementById("pimDiv").hidden = false;
              }
              if(typeSelect.value === "game")
              {
                  document.getElementById("gpDiv").hidden = true;
                  document.getElementById("pensDiv").hidden = true;
                  document.getElementById("pimDiv").hidden = true;
                
              }
            }
            if(typeSelect.value === "streak")
            {
              document.getElementById("streakDiv").hidden = false;
              document.getElementById("streakMinDiv").hidden = false;
              document.getElementById("positionDiv").hidden = true;
              document.getElementById("gpDiv").hidden = true;
              document.getElementById("goalDiv").hidden = true;
              document.getElementById("assistsDiv").hidden = true;
              document.getElementById("ptsDiv").hidden = true;
              document.getElementById("gaDiv").hidden = true;
              document.getElementById("savesDiv").hidden = true;
              document.getElementById("minsDiv").hidden = true;
              document.getElementById("pensDiv").hidden = true;
              document.getElementById("pimDiv").hidden = true;
            }
            else
            {
              document.getElementById("streakDiv").hidden = true;
              document.getElementById("streakMinDiv").hidden = true;
              document.getElementById("positionDiv").hidden = false;
            }
        },
        error: function (xhr, status, error) {
            console.error("Error:", error);
        },
    });
}
 function setSort(header) {
            var columnName = header.innerHTML;
            if(!columnName)
                return;
            var thElements = document.getElementsByTagName('th');
            document.getElementById("sortval").value = columnName.replace("<span class=\"arrow\">▲</span> ","").replace("<span class=\"arrow\">▼</span> ","")

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
            }
            submitForm();
}
