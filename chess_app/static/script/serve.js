const gameContainer = document.getElementById('game-container');
let selectedSquare = null;
let names_w = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B", 
                8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
let names_b = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B", 
                8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
const colors = {0: "w", 1: "b"}

// function to send user input (move) to backend to proccess
// frontend -> backend
async function makeMove(move) {
    const response = await fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        // convert move list to json to send to backend
        body: JSON.stringify({ move }),
    });
    const result = await response.json();
    if (result.error) {
        alert(result.error);
    } else if (result.status === 'end') { // game over
        fetchGameState();
        const txt = getEnding(result.end_result)
        alert(txt);
    } else { // proceed with game
        updateBoard(result.w_coords, result.b_coords, result.promotion);
    }
}

// function to get the (possibly) updated game state
// backend -> frontend
async function fetchGameState() {
    const response = await fetch('/state');
    const state = await response.json();
    renderBoard(state.w_coords, state.b_coords);
}

// Event listener to handle user input and make move
gameContainer.addEventListener('click', (event) => {
    const square = event.target.closest('.square');
    if (!square) return;
    // check if user has already selected a square
    if (selectedSquare) {
        if (selectedSquare != square) {
            const move = [selectedSquare.dataset.coordinate, square.dataset.coordinate];
            makeMove(move);
            selectedSquare.classList.remove('selected');
            selectedSquare = null;
        } else {
            alert("Select different squares")
            selectedSquare.classList.remove('selected');
            selectedSquare = null;
        }
    } else { // add square to selected class and wait for another click
        selectedSquare = square;
        selectedSquare.classList.add('selected');
    }
});

// function to update board handling promotions
function updateBoard(w_coords, b_coords, promotion) {
    if (promotion) {
        console.log("promotion not none")
        promoteQueen(promotion)
    }
    console.log("board updated")
    renderBoard(w_coords, b_coords);
}

// input form: {'index': piece id, 'color': piece color, 'coord': piece position}
function promoteQueen(input) {
    let names = input.color ? names_b : names_w
    names[input.index] = 'Q'
    console.log(names)
    const square = document.querySelector(`[data-coordinate='${input.coord}']`);
    if (square) {
        const img = square.querySelector('img');
        // only allowing promoting to queen for now
        img.src = getPieceImageUrl('Q', input.color); 
    }
}

// render board given piece coords
function renderBoard(w_coords, b_coords) {
    gameContainer.innerHTML = '';
    // create hmtl elements for all 64 squares
    for (let row = 0; row < 8; row++) {
        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            // add square css and light/dark bg dependent on the diagonal (c1+c2)%2==0
            square.classList.add('square', (row + col) % 2 === 0 ? 'light' : 'dark');
            square.dataset.coordinate = `${7-row},${col}`;
            gameContainer.appendChild(square);
        }
    }
    // update squares with piece images
    renderPieces(w_coords, 0);
    renderPieces(b_coords, 1);
}

// function to find all pieces of color and create image at their position
function renderPieces(coords, color) {
    const names = color ? names_b : names_w
    coords.forEach((coord, index) => {
        // get the square with coordinate = coord
        // NOTE row coord is 7-row coord on board to show white on bottom
        // could dynamically change this to reflect color user is playing
        const square = document.querySelector(`[data-coordinate='${coord[0]},${coord[1]}']`);
        if (square) {
            const img = document.createElement('img');
            img.src = getPieceImageUrl(names[index], color); 
            img.classList.add('piece');
            square.appendChild(img);
        }
    });
}

function getPieceImageUrl(type, color) {
    switch (type) {
        case 'Q':
            return color ? '/static/Qb.png' : '/static/Qw.png';
        case 'K':
            return color ? '/static/Kb.png' : '/static/Kw.png';
        case 'R':
            return color ? '/static/Rb.png' : '/static/Rw.png';
        case 'B':
            return color ? '/static/Bb.png' : '/static/Bw.png';
        case 'N':
            return color ? '/static/Nb.png' : '/static/Nw.png';
        case 'P':
            return color ? '/static/Pb.png' : '/static/Pw.png';
        default:
            return '/static/empty.png';
    }
}

function getEnding(input) {
    // Determine ending based on the input
    switch(input) {
            case 2:
                return "White checkmated Black. White wins. Game over."
            case 3:
                return "White stalemated Black. It's a draw. Game over."
            case 4:
                return "Black checkmated White. Black wins. Game over."
            case 5:
                return "Black stalemated White. It's a draw. Game over."
        }
}

fetchGameState();