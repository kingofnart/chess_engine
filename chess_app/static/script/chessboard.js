class ChessBoard {

    constructor() {
        this.gameContainer = document.getElementById('game-container');
        this.gameContainerWrapper = document.getElementById('game-container-wrapper');
        this.turnIndicator = document.getElementById('turn-indicator');
        this.blackTimer = document.getElementById('black-timer');
        this.whiteTimer = document.getElementById('white-timer');
        this.rowLabels = document.getElementById('row-labels')
        this.columnLabels = document.getElementById('column-labels')
        this.selectedSquare = null;
        this.names_w = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B", 
                        8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
        this.names_b = {0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
                        8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"}
        // used as interval IDs
        this.timerIntervals = { white: null, black: null };
        // Event listener to handle user input and make move
        this.gameContainer.addEventListener('click', (event) => this.handleClick(event));
        // fetch initial game state
        this.fetchGameState();
        this.renderLabels();
    }


    // function to send user input (move) to backend to proccess
    // frontend -> backend
    async makeMove(move) {
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
            if (result.error === "invalid") {
                this.flashInvalidMove(document.querySelector(`[data-coordinate='${move[0]}']`), 
                                      document.querySelector(`[data-coordinate='${move[1]}']`));
            } else if (result.error === "king safety") {
                this.flashInvalidMove(document.querySelector(`[data-coordinate='${result.coords[0]}']`),
                                      document.querySelector(`[data-coordinate='${result.coords[0]}']`));
            }
        } else if (result.status === 'end') { // game over
            this.fetchGameState();
            const txt = this.getEnding(result.end_result)
            alert(txt);
        } else if (result.status === 'move applied') { // proceed with game
            this.updateBoard(result.w_coords, result.b_coords, result.turn, result.promotion);
        }
    }


    // function to get the (possibly) updated game state
    // backend -> frontend
    async fetchGameState() {
        const response = await fetch('/state');
        const state = await response.json();
        this.renderBoard(state.w_coords, state.b_coords);
        this.updateTurnIndicator(state.turn)
        this.updateTimers(state.turn);
    }


    handleClick(event) {
        const square = event.target.closest('.square');
        if (!square) return;
        // check if user has already selected a square
        if (this.selectedSquare) {
            if (this.selectedSquare != square) {
                const move = [this.selectedSquare.dataset.coordinate, square.dataset.coordinate];
                this.makeMove(move);
                this.selectedSquare.classList.remove('selected');
                this.selectedSquare = null;
            } else {
                this.flashInvalidMove(this.selectedSquare, this.selectedSquare)
                this.selectedSquare.classList.remove('selected');
                this.selectedSquare = null;
            }
        } else { // add square to selected class and wait for another click
            this.selectedSquare = square;
            this.selectedSquare.classList.add('selected');
        }
    }

    // function to update board handling promotions
    updateBoard(w_coords, b_coords, turn, promotion) {
        if (promotion) {
            console.log("promotion not none");
            this.promoteQueen(promotion);
        }
        console.log("board updated");
        this.renderBoard(w_coords, b_coords);
        this.updateTurnIndicator(turn);
        this.updateTimers(turn);
    }


    // input form: {'index': piece id, 'color': piece color, 'coord': piece position}
    promoteQueen(input) {
        let names = input.color ? this.names_b : this.names_w;
        names[input.index] = 'Q';
        console.log(names);
        const square = document.querySelector(`[data-coordinate='${input.coord}']`);
        if (square) {
            const img = square.querySelector('img');
            // only allowing promoting to queen for now
            img.src = this.getPieceImageUrl('Q', input.color); 
        }
    }


    // method to render the labels of rows/cols
    renderLabels() {
        // create column labels
        this.columnLabels.innerHTML = ''
        const columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        columns.forEach(letter => {
            const label = document.createElement('div');
            label.className = 'coordinate-label';
            label.innerText = letter;
            this.columnLabels.appendChild(label);
        });
        //this.gameContainerWrapper.appendChild(columnLabels);
        // create row labels
        this.rowLabels.innerHTML = ''
        const rows = ['8', '7', '6', '5', '4', '3', '2', '1'];
        rows.forEach(row => {
            const label = document.createElement('div');
            label.className = 'coordinate-label';
            label.innerText = row;
            this.rowLabels.appendChild(label);
        });
        //this.gameContainerWrapper.appendChild(rowLabels);
    }


    // render board given piece coords
    renderBoard(w_coords, b_coords) {
        this.gameContainer.innerHTML = '';
        // create hmtl elements for all 64 squares
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('div');
                // add square css and light/dark bg dependent on the diagonal (c1+c2)%2==0
                square.classList.add('square', (row + col) % 2 === 0 ? 'light' : 'dark');
                // 7-row adds white pieces at the bottom
                // want to dynamically change this to reflect color user is playing
                square.dataset.coordinate = `${7-row},${col}`;
                this.gameContainer.appendChild(square);
            }
        }
        // update squares with piece images
        this.renderPieces(w_coords, 0);
        this.renderPieces(b_coords, 1);
    }


    // function to find all pieces of color and create image at their position
    renderPieces(coords, color) {
        const names = color ? this.names_b : this.names_w;
        coords.forEach((coord, index) => {
            // get the square with coordinate = coord
            const square = document.querySelector(`[data-coordinate='${coord[0]},${coord[1]}']`);
            if (square) { // safety
                const img = document.createElement('img');
                img.src = this.getPieceImageUrl(names[index], color); 
                img.classList.add('piece');
                square.appendChild(img);
            }
        });
    }


    // params: piece type, piece color, returns: filename of piece image
    getPieceImageUrl(type, color) {
        switch (type) {
            case 'Q':
                return color ? '/static/images/Qb.png' : '/static/images/Qw.png';
            case 'K':
                return color ? '/static/images/Kb.png' : '/static/images/Kw.png';
            case 'R':
                return color ? '/static/images/Rb.png' : '/static/images/Rw.png';
            case 'B':
                return color ? '/static/images/Bb.png' : '/static/images/Bw.png';
            case 'N':
                return color ? '/static/images/Nb.png' : '/static/images/Nw.png';
            case 'P':
                return color ? '/static/images/Pb.png' : '/static/images/Pw.png';
            default:
                return '/static/images/empty.png';
        }
    }


    // params: int id of game ending, returns: string corresponding to ending
    getEnding(input) {
        // Determine ending based on the input
        switch(input) {
                case 2:
                    return "White checkmated Black. White wins. Game over.";
                case 3:
                    return "White stalemated Black. It's a draw. Game over.";
                case 4:
                    return "Black checkmated White. Black wins. Game over.";
                case 5:
                    return "Black stalemated White. It's a draw. Game over.";
            }
    }


    // Update the turn indicator based on the current turn
    updateTurnIndicator(turn) {
        this.turnIndicator.style.background = turn === true ? "black" : "white";
        this.turnIndicator.style.color = turn === true ? "white" : "black";
        this.turnIndicator.innerText = turn === true ? "Black to move" : "White to move";
    }


    updateTimers(turn) {
        if (turn === true) {
            clearInterval(this.timerIntervals.white);
            this.startTimer('black');
        } else {
            clearInterval(this.timerIntervals.black);
            this.startTimer('white');
        }
    }


    // method to start timers and check if timer reached 0
    startTimer(color) {
        const timerElement = color === 'white' ? this.whiteTimer : this.blackTimer;
        this.timerIntervals[color] = setInterval(() => {
            // get time in seconds
            let time = this.parseTime(timerElement.innerText);
            time--;
            if (time <= 0) {
                clearInterval(this.timerIntervals[color]);
                timerElement.innerText = '00:00';
            } else {
                // show user time in MM:SS
                timerElement.innerText = this.formatTime(time);
            }
        }, 1000); // delay set to 1 second
    }


    // method to get time in seconds
    parseTime(timeStr) {
        const [minutes, seconds] = timeStr.split(':').map(Number);
        return minutes * 60 + seconds;
    }


    // method to get time in MM:SS
    formatTime(time) {
        const minutes = Math.floor(time / 60).toString().padStart(1, '0');
        const seconds = (time % 60).toString().padStart(2, '0');
        return `${minutes}:${seconds}`;
    }


    // method to flash squares red for invalid move
    flashInvalidMove(square1, square2) {
        console.log('Flashing squares:', square1, square2); 
        if (square1) { square1.classList.add('invalid-move'); }
        if (square2) { square2.classList.add('invalid-move'); }
        setTimeout(() => {
            if (square1) { square1.classList.remove('invalid-move'); }
            if (square2) { square2.classList.remove('invalid-move'); }
        }, 100); 
        setTimeout(() => {
            if (square1) square1.classList.add('invalid-move');
            if (square2) square2.classList.add('invalid-move');
        }, 200);
        setTimeout(() => {
            if (square1) square1.classList.remove('invalid-move');
            if (square2) square2.classList.remove('invalid-move');
        }, 300);
    }
}


// make ChessBoard object when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChessBoard();
});