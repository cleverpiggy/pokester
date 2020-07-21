
const JWTS_LOCAL_KEY = 'token';
const PERMISSIONS_KEY = 'permissions';

function getUrlToken() {
    // parse the fragment
    const fragment = window.location.hash.substr(1).split('&')[0].split('=');
    // check if the fragment includes the access token
    if ( fragment[0] === 'access_token' ) {
      // add the access token to the jwt
      return fragment[1];
    }
}

function setJwt(token) {
    localStorage.setItem(JWTS_LOCAL_KEY, token);
}

function loadJwt() {
    return localStorage.getItem(JWTS_LOCAL_KEY) || null;
}

function setPermissions(permissions){
    localStorage.setItem(PERMISSIONS_KEY, permissions);
}

function loadPermissions(){
    perms = localStorage.getItem(PERMISSIONS_KEY);
    if (perms){
        return perms.split(',');
    }
}

function logout() {
    setJwt('');
    setPermissions('');
}


function makeHeaders() {
    var token = loadJwt();
    return {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    }
}


function displayError(error){
    alert(error);
}

// .classList is important
// DOM -----------------------------------------------


function textCell(text, game){
    var cell = document.createElement('td');
    cell.textContent = text;
    return cell;
}


function playerCell(text, game){
    var cell = document.createElement('td');
    var button = document.createElement('button');
    button.textContent = text;
    button.onclick = function (){
        getPlayers(game.id);
    };
    cell.appendChild(button);
    return cell;
}

function activatePlayersTable(players, gameId){
    const playersTable = document.getElementById("players-table");
    const gamesTable = document.getElementById("games-table");
    //delete the previous stuff
    playersTable.innerHTML = "";
    const headRow = document.createElement('tr');
    const header = document.createElement('th');
    header.textContent = `Game ${gameId}`;
    headRow.appendChild(header);
    playersTable.appendChild(headRow);
    for (const player of players){
        var row = document.createElement('tr');
        row.appendChild(textCell(player.name));
        row.appendChild(textCell(player.email));
        playersTable.appendChild(row);
    }
    const backButton = document.getElementById("back-button");
    playersTable.classList.toggle("hidden");
    gamesTable.classList.toggle("hidden");
    backButton.classList.toggle("hidden");
    backButton.onclick = function(){
        playersTable.classList.toggle("hidden");
        gamesTable.classList.toggle("hidden");
        backButton.classList.toggle("hidden");
    }
}

const gameAttrs = [
    ['platform', textCell],
    ['start_time', textCell],
    ['host_id', textCell],
    ['num_registered',playerCell],
    ['max_players', textCell],
    ['id', textCell]
];

function addGamesRows(games) {
    // games -> an array of game objects
    var table = document.getElementById('games-table');
    for (const game of games){
        var row = document.createElement('tr');
        row.id = `game${game.id}`;
        for (const [attr, cellBuilder] of gameAttrs){
            var cell = cellBuilder(game[attr], game);
            row.appendChild(cell);
        }
        table.appendChild(row);
    }
}




// fetches---------------------------------------------------------

function getGames(page, pageLength){
    fetch(`/games?page=${page}&page_length=${pageLength}`)
        .then(response => response.json())
        .then(json => addGamesRows(json.games))
        .catch(error => displayError(error));
}

function getPlayers(gameId){
    //players: {"name": x, "email": y}
    fetch(`/game${gameId}/players`)
        .then(response => response.json())
        .then(json => activatePlayersTable(json.players, gameId))
        .catch(error => displayError(error))
}

function handleVerifyResponse(response){
    console.log(response);
    if (response.success){
        setJwt(token);
        setPermissions(response.permissions);
    }
}

function attemptLogin(){
    var token = getUrlToken();
    if (!token) {
        console.log('no token');
        return;
    }
    fetch(`/verify${token}`)
        .then(response => response.json())
        .then(json => function(){
            console.log(json);
            if (json.success){
                setJwt(token);
                setPermissions(json.permissions);
            }else{
                console.log('Bad response', json);
            }
        }())
        .catch(error => displayError(error))
}

window.onload = function () {
    getGames(1, 10);
    document.getElementById('logout').onclick = logout;
    attemptLogin();
    // document.getElementById("sick_button").onclick = function (){verifyToken(loadJwt())};
};

