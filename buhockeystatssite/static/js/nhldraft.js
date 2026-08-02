console.log("loading nhldraft.js");

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
    document.getElementById("team").value = "all";
    document.getElementById("country").value = "all";
    document.getElementById("draft").value = "all";

    document.getElementById("draftStart").value = "1970";

    document.getElementById("draftEnd").value = "2026";
    if(document.getElementById("draftEnd").value===""){
      document.getElementById("draftEnd").value = "2026";
    }
    document.getElementById("sortval").value = "";
    document.getElementById("isAscending").value = "";
    document.getElementById("name").value = "";
    document.getElementById("group").value = "";
    // Reset Min Filters
    document.getElementById("rdmin").value = "";
    document.getElementById("pickmin").value = "";
    document.getElementById("pirmin").value = "";
    if(event!=null){
      event.preventDefault();
      submitForm("true");
    }
}

function initializeFilters() {
    const nameInput = document.getElementById("name");
    nameInput.addEventListener("keydown", onKeydown);
    
    document.getElementById("rdmin").addEventListener("keydown", onKeydown);
    document.getElementById("pickmin").addEventListener("keydown", onKeydown);
    document.getElementById("pirmin").addEventListener("keydown", onKeydown);

    document
        .getElementById("resetButton")
        .addEventListener("click", clearFilters);


    clearFilters();
}

function submitForm(reset = "false") {
    const formData = $("#draftForm").serialize();

    $.ajax({
        url: $("#draftForm").attr("action"),
        method: $("#draftForm").attr("method"),
        data: formData,
        success: function (response) {
            $("#draftTable").html(response.draftData);
            $("#sortval").value = response.sortval;
            if (reset === "true") {
                const selectDraftElement = $("#draft");
                selectDraftElement.empty();
                selectDraftElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.draft_values, function (index, item) {
                    selectDraftElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectDraftStartElement = $("#draftStart");
                selectDraftStartElement.empty();
                $.each(response.draft_values, function (index, item) {
                    selectDraftStartElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });

                const selectDraftEndElement = $("#draftEnd");
                selectDraftEndElement.empty();
                $.each(response.draft_values, function (index, item) {
                    selectDraftEndElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });
                document.getElementById("draftEnd").value = response.draft_values[response.draft_values.length-1];
                document.getElementById("draftEnd").text = response.draft_values[response.draft_values.length-1];

                const selectTeamElement = $("#team");
                selectTeamElement.empty();
                selectTeamElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.teams_values, function (index, item) {
                    selectTeamElement.append(
                        $("<option>", {
                            value: item,
                            text: item,
                        })
                    );
                });
                
                const selectCountryElement   = $("#country");
                selectCountryElement.empty();
                selectCountryElement.append(
                    $("<option>", {
                        value: "all",
                        text: "All",
                    })
                );
                $.each(response.country_values, function (index, item) {
                    selectCountryElement.append(
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
