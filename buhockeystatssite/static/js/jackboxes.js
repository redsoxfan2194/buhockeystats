let guessesLeft = 9;
let score = 0;
let gaveUp = false;
let activeBox = null;
let validating = false;
let gridTransmitted = false;

const usedPlayers = new Set();
const invalidPlayers = {};


// INITIALIZATION
document.addEventListener("DOMContentLoaded", () => {
    setupPlayerBoxes();
    setupButtons();
    setupEscapeKey();

    restoreGame();

    updateScore();
    updateGuesses();
    if (!localStorage.getItem("jacksBoxesHelpSeen"))
    {
        showHelp();
    }
});

function saveGame() 
{
    const grid = [...document.querySelectorAll(".player-box")]
        .map(box =>
            box.classList.contains("filled")
                ? box.textContent
                : null
        );

    localStorage.setItem(
        "jacksBoxesPlayed",
        gameNumber
    );

    localStorage.setItem(
        "jacksBoxesScore",
        score
    );

    localStorage.setItem(
        "jacksBoxesGuesses",
        guessesLeft
    );

    localStorage.setItem(
        "jacksBoxesGrid",
        JSON.stringify(grid)
    );
}
function restoreGame() 
{
    if (localStorage.getItem("jacksBoxesPlayed") != gameNumber)
    {
        return;
    }

    const savedGrid = JSON.parse(localStorage.getItem("jacksBoxesGrid") || "[]");

    document
        .querySelectorAll(".player-box")
        .forEach((box, index) => {

            const player = savedGrid[index];

            if (!player) {
                return;
            }

            box.textContent = player;
            box.classList.add("filled");

            usedPlayers.add(player);
        });

    score = parseInt(localStorage.getItem("jacksBoxesScore") || "0", 10);

    guessesLeft = parseInt(localStorage.getItem("jacksBoxesGuesses") || "9", 10);

    
    updateScore();
    updateGuesses();

    // Game was already finished
    if (score >= 9 || guessesLeft <= 0 || localStorage.getItem("jacksBoxesGaveUp"))
    {
        disableGame();
        showGameOver();
    }
}


// Player Search

function openSearch(box)
{

    if (!box || box.classList.contains("filled") || guessesLeft <= 0 || validating) {
        return;
    }

    closeSearch();
    activeBox = box;
    activeBox.classList.add("selected");
    const search = document.createElement("div");

    search.className = "player-search";

    search.innerHTML = `
        <input
            type="text"
            placeholder="Search for a player..."
            autocomplete="on"
        >

        <div class="player-list"></div>
    `;

    document.body.appendChild(search);
    const input = search.querySelector("input");
    const list = search.querySelector(".player-list");
    updatePlayerList(input, list);

    input.addEventListener(
        "input",
        () => {
            updatePlayerList(input, list);
        }
    );

    search.addEventListener(
        "click",
        event => {
            event.stopPropagation();
        }
    );

    positionSearch(search);

    requestAnimationFrame(() => {

        if (document.body.contains(search))
        {
            positionSearch(search);
            input.focus();
        }

    });
}


// =====================================================
// POSITION SEARCH
// =====================================================

function positionSearch(search)
{

    if (!search || !activeBox)
    {
        return;
    }

    if (!document.body.contains(activeBox))
    {
        closeSearch();
        return;
    }

    const rect = activeBox.getBoundingClientRect();

    const padding = 10;
    const gap = 8;

    const searchWidth =  Math.min(280, window.innerWidth - padding * 2);

    search.style.width = `${searchWidth}px`;

    // Force layout so height is accurate
    const searchHeight =  search.offsetHeight;

    // Default position: below box
    let left = rect.left;

    let top =
        rect.bottom + gap;

    if (left + searchWidth > window.innerWidth - padding)
    {
        left =  window.innerWidth -  searchWidth - padding;
    }

    if (left < padding)
    {
        left = padding;
    }

    if (top + searchHeight > window.innerHeight - padding
    ) {
        top = rect.top - searchHeight -  gap;
    }

    // If it doesn't fit above either,
    // keep it inside the viewport
    if (top < padding)
    {
        top = padding;
    }

    search.style.left = `${left}px`;

    search.style.top = `${top}px`;
}

// =====================================================
// SEARCH RESULTS
// =====================================================

function updatePlayerList(input, list) {

    list.innerHTML = "";

    if (!activeBox)
    {
        return;
    }

    const searchText = input.value.trim().toLowerCase();

    const row = activeBox.dataset.row;

    const col =  activeBox.dataset.col;

    const key = `${row},${col}`;

    availablePlayers.filter(player =>
            player
                .toLowerCase()
                .includes(searchText)
        )
        .forEach(player => {

            const option = document.createElement("div");
            option.className =  "player-option";
            const name = document.createElement("span");
            name.textContent =  player;
            option.appendChild(name);

            if (usedPlayers.has(player) ) {

                addAlreadyUsed(option);

            }

            else if (invalidPlayers[key] && invalidPlayers[key].has(player))
            {

                name.classList.add("invalid-player");

            }

            else
            {

                addSelectButton(option, player);

            }

            list.appendChild(option);

        });
}


function addAlreadyUsed(option)
{

    const used =  document.createElement("span");

    used.className =
        "already-used";

    used.textContent =
        "Already Used";

    option.appendChild(used);
}

function addSelectButton(option, player)
{

    const button = document.createElement("button");

    button.className = "select-button";

    button.textContent =  "Select";


    button.addEventListener(
        "click",
        event => {

            event.stopPropagation();

            if (validating || !activeBox)
            {
                return;
            }

            const box = activeBox;

            validatePlayer(player, box);
        }
    );

    option.appendChild(button);
}

function closeSearch()
{

    const search = document.querySelector(".player-search");

    if (search)
    {
        search.remove();
    }

    if (activeBox)
    {
        activeBox.classList.remove("selected");

    }

    activeBox = null;
}

async function validatePlayer(player, box)
{

    if (!box || guessesLeft <= 0 || validating)
    {
        return;
    }

    validating = true;
    const row = box.dataset.row;
    const col = box.dataset.col;
    let response;

    try
    {
        response = await fetch(
                "/jacksboxes",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({player, row, col})
                }
            );

    }
    catch (error)
    {

        console.error("Validation request failed:",error);
        validating = false;
        return;
    }

    let result;

    try
    {
        result =  await response.json();
    }
    catch (error)
    {

        console.error("Invalid response from server:",error);
        validating = false;
        return;
    }


    guessesLeft--;
    updateGuesses();

    if (result.valid)
    {

        handleCorrectPlayer(player, box);
        saveGame();
        validating = false;

        if (score >= 9 || guessesLeft <= 0)
        {
            endGame();
        }

        return;
    }

    handleInvalidPlayer(player, row, col);
    saveGame();

    validating = false;
    if (guessesLeft <= 0) {
        endGame();
    }
}

function handleCorrectPlayer(player, box)
{
    box.textContent = player;
    box.classList.add("filled");
    usedPlayers.add(player);

    score++;
    updateScore();
    closeSearch();
}


function handleInvalidPlayer(player, row, col)
{

    const key = `${row},${col}`;


    if (!invalidPlayers[key]) 
    {
        invalidPlayers[key] =  new Set();
    }

    invalidPlayers[key].add(player);
    const search = document.querySelector(".player-search");


    if (!search)
    {
        return;
    }


    search.querySelectorAll(".player-option")
        .forEach(option => {
            const name =  option.querySelector("span");

            if (!name || name.textContent !== player)
            {
                return;
            }

            name.classList.add("invalid-player");


            option.querySelector(".select-button")
                ?.remove();
        });
}


// =====================================================
// GAME STATE
// =====================================================

function updateScore()
{

    const element =  document.getElementById("score");

    if (element)
    {
        element.textContent = `${score}/9`;

    }
}
function updateGuesses()
{

    const element =  document.getElementById("guessesLeft");

    if (element)
    {
        element.textContent =  guessesLeft;
    }
}

function disableGame()
{

    document.querySelectorAll(".player-box")
        .forEach(box => {

            box.style.pointerEvents =
                "none";

        });

    const giveUp = document.getElementById("giveUp");

    if (giveUp)
    {
        giveUp.disabled =  false;

        giveUp.textContent = "Show Score";

        giveUp.classList.add("show-score-button");

    }
}

function endGame()
{

    closeSearch();
    disableGame();
    saveGame();
    transmitGrid();
    showGameOver();
}

function showGameOver()
{

    saveGame();
    const title =  document.getElementById("gameOverTitle");


    if (title)
    {
        title.textContent = `Jack's Boxes #${gameNumber}`;

    }

    const finalScore =  document.getElementById("finalScore");

    if (finalScore)
    {

        finalScore.textContent = `${score}/9`;

    }

    updateScore();
    updateGuesses();
    buildResultGrid();
    showPossibleAnswers();

    const modal =
        document.getElementById(
            "gameOverModal"
        );


    if (modal) {

        modal.style.display =
            "flex";

    }
}


function buildResultGrid()
{

    const resultGrid = document.getElementById("resultGrid");
    if (!resultGrid)
    {
        return;
    }


    resultGrid.innerHTML ="";


    for (let row = 0; row < 3;row++)
    {
        for (let col = 0; col < 3; col++)
        {
            const resultBox = document.createElement("div");
            resultBox.className = "result-box";
            const box = document.querySelector(`.player-box[data-row="${row}"][data-col="${col}"]`);

            if (box?.classList.contains("filled"))
            {
                resultBox.classList.add("correct");
            }
            resultGrid.appendChild(resultBox);

        }

    }
}


async function copyScore()
{

    let result = "";


    for (let row = 0; row < 3; row++)
    {

        for (let col = 0; col < 3; col++)
        {
            const box =  document.querySelector(`.player-box[data-row="${row}"][data-col="${col}"]`);
            result += box?.classList.contains("filled") ? "🟥" : "⬜";
        }

        result += "\n";

    }


    const text = `Jack's Boxes #${gameNumber} ${score}/9\n\n${result}\nPlay: ${window.location.origin}/jacksboxes`;


    try {
        await navigator.clipboard.writeText(text);
        const button = document.getElementById("copyScore");

        if (!button)
        {
            return;
        }

        button.textContent = "Copied!";


        setTimeout(() => {

            button.textContent =
                "Copy Score";

        }, 1500);


    } catch (error) {

        console.error(
            "Could not copy score:",
            error
        );

    }
}


function showPossibleAnswers()
{

    const grid =  document.getElementById("possibleGrid");

    if (!grid)
    {
        return;
    }

    grid.innerHTML = "";


    possibleAnswers.forEach(
        (answers, index) => {

            const box =
                document.createElement(
                    "div"
                );


            box.className =  "possible-box";


            box.textContent = answers.length;


            box.dataset.index = index;


            box.addEventListener(
                "click",
                () => {

                    showAnswers(index, answers);
                }
            );


            grid.appendChild(box);

        }
    );
}

function showAnswers(index, answers)
{

    const modal =  document.getElementById("answersModal");
    const title = document.getElementById("answersTitle");
    const list = document.getElementById("answersList");

    if (!modal || !title || !list)
    {
        return;
    }

    title.textContent = `Possible Answers (${answers.length})`;

    list.innerHTML =  "";


    if (!answers.length)
    {

        const item =  document.createElement( "div");
        item.className = "answer-item";

        item.textContent = "No possible answers.";


        list.appendChild(item);

    }
    else
    {

        answers.forEach(answer => {

                const item =
                    document.createElement(
                        "div"
                    );

                item.className =  "answer-item";
                item.textContent =  answer;

                list.appendChild(item);

            }
        );

    }

    modal.style.display = "flex";
}


function setupPlayerBoxes()
{
    document.querySelectorAll(".player-box")
        .forEach(box => {

            box.addEventListener(
                "click",
                event => {

                    event.stopPropagation();
                    if (!box.classList.contains("filled") && guessesLeft > 0 && !validating)
                    {
                        openSearch(box);
                    }
                }
            );

        });


    // Close search when clicking outside
    document.addEventListener(
        "click",
        event => {

            if (!activeBox)
            {
                return;
            }

            const search = document.querySelector(".player-search");

            if (search && search.contains(event.target))
            {
                return;
            }


            if (activeBox.contains(event.target))
            {
                return;
            }

            closeSearch();

        }
    );
}

function setupButtons()
{

    document.getElementById("copyScore")?.addEventListener("click",copyScore);
    document.getElementById("giveUp")?.addEventListener("click",handleGiveUp);

    document.getElementById("closeGameOver")?.addEventListener(
            "click",
            () => {

                const modal =document.getElementById("gameOverModal");
                if (modal)
                {
                    modal.style.display = "none";
                }

            }
        );


    document.getElementById("closeAnswers")?.addEventListener(
            "click",
            () => {

                const modal =  document.getElementById("answersModal");
                if (modal)
                {
                    modal.style.display = "none";

                }

            }
        );
        
       
    document.getElementById("helpButton")?.addEventListener("click", showHelp);
    document.getElementById("closeHelp")?.addEventListener("click", closeHelp);

}

// =====================================================
// HELP
// =====================================================

function showHelp()
{
    const modal = document.getElementById("helpModal");

    if (modal)
    {
        modal.style.display = "flex";
    }
}


function closeHelp()
{
    const modal = document.getElementById("helpModal");

    if (modal)
    {
        modal.style.display = "none";
    }

    // Remember that the user has seen the help
    localStorage.setItem("jacksBoxesHelpSeen", "true");
}

function handleGiveUp()
{

    const button = document.getElementById("giveUp");

    if (button?.classList.contains("show-score-button"))
    {
        showGameOver();
        return;
    }
    gaveUp = true;
    localStorage.setItem("jacksBoxesGaveUp", "true");
    endGame();
}

function setupEscapeKey()
{

    document.addEventListener(
        "keydown",
        event => {

            if (event.key !== "Escape")
            {
                return;
            }

            const answersModal = document.getElementById("answersModal");
            const gameOverModal = document.getElementById("gameOverModal");

            if (answersModal && answersModal.style.display === "flex")
            {
                answersModal.style.display = "none";
                return;
            }

            // Close game over
            if (gameOverModal && gameOverModal.style.display === "flex")
            {
                gameOverModal.style.display =  "none";
                return;
            }
            // Close search
            if (activeBox)
            {
                closeSearch();
            }
            
            const helpModal =  document.getElementById("helpModal");

            if (helpModal && helpModal.style.display === "flex")
            {
                closeHelp();
                return;
            }

        }
    );
}

async function transmitGrid()
{
    if (gridTransmitted)
    {
        return;
    }

    gridTransmitted = true;

    const grid = [...document.querySelectorAll(".player-box")]
        .map(box =>
            box.classList.contains("filled")
                ? box.textContent
                : null
        );

    const timestamp = new Date().toISOString();

    try
    {
        const response = await fetch(
            "/jacksboxes",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    type: 'gameEnd',
                    gameNumber: gameNumber,
                    grid: grid,
                    score: score,
                    gaveup:gaveUp,
                    guessesLeft: guessesLeft,
                    timestamp: timestamp
                })
            }
        );

        if (!response.ok)
        {
            throw new Error(`Server returned ${response.status}`);
        }

        console.log("Game end transmitted");
    }
    catch (error)
    {
        // Allow another attempt if the request actually failed
        gridTransmitted = false;
        console.error("Failed to transmit game end:", error);
    }
}


function repositionSearch()
{

    const search = document.querySelector(".player-search");


    if (search && activeBox)
    {
        positionSearch(search);

    }
}

window.addEventListener("resize", repositionSearch);
window.addEventListener("scroll", repositionSearch);