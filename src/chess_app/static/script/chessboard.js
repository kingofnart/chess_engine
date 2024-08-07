class ChessBoard {

    constructor() {
        this.gameID = 0
        this.gameContainer = document.getElementById('game-container');
        this.gameContainerWrapper = document.getElementById('game-container-wrapper');
        this.opponent_displayed = document.getElementById('opponent-displayed');
        this.turnIndicator = document.getElementById('turn-indicator');
        this.topTimer = document.getElementById('top-timer');
        this.bottomTimer = document.getElementById('bottom-timer');
        this.rowLabels = document.getElementById('row-labels');
        this.columnLabels = document.getElementById('column-labels');
        this.startButton = document.getElementById('start-button');
        this.resignButton = document.getElementById('resign-button');
        this.color_button = document.getElementById('color-button');
        this.opponent_button = document.getElementById('opponent-button');
        this.time_control_button = document.getElementById('time-control-button');
        this.top_mat_cnt = document.getElementById('top-mat-cnt')
        this.bot_mat_cnt = document.getElementById('bot-mat-cnt')
        this.offset = 7;
        this.direction = -1;
        this.opponent = "pnp";
        this.selectedSquare = null;
        this.gameRunning = true;
        this.names_w = {
            0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
            8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
        };
        this.names_b = {
            0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
            8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
        };
        // used as handles for (set/clear)Interval
        this.timerHandles = { white: null, black: null };
        // used to increment timers each move
        this.increment = 0;
        // Event listener to handle user input and make move
        this.gameContainer.addEventListener('click', (event) => this.handleClick(event));
        // Assigning event listener
        this.startButton.addEventListener('click', () => this.startGame());
        this.resignButton.addEventListener('click', () => this.endGame(7));
        this.resignButton.disabled = true;
        this.color_button.addEventListener('click', () => this.toggleDropdown("color-drop-cont", this.color_button));
        this.opponent_button.addEventListener('click', () => this.toggleDropdown("opp-drop-cont", this.opponent_button));
        this.time_control_button.addEventListener('click', () => this.toggleDropdown("time-drop-cont", this.time_control_button));
        document.querySelectorAll('.time-option').forEach(button => {
            button.addEventListener('click', (event) => this.setTimeControl(event));
        });
        document.querySelectorAll('.color-option').forEach(button => {
            button.addEventListener('click', (event) => this.setColor(event));
        });
        document.querySelectorAll('.opp-option').forEach(button => {
            button.addEventListener('click', (event) => this.setOpponent(event));
        });
        // reset if necessary and fetch initial game state
        this.resetGame();
    }


    // method to reset the board state and clocks
    async resetGame() {
        this.names_w = {
            0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
            8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
        };
        this.names_b = {
            0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
            8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
        };
        this.topTimer.innerText = "5:00";
        this.bottomTimer.innerText = "5:00";
        this.topTimer.classList.remove('time-trouble');
        this.bottomTimer.classList.remove('time-trouble');
        const end_message = document.querySelector(".end-message");
        if (end_message != null) {
            end_message.remove();
        }
        const reset_button = document.querySelector(".reset-button");
        if (reset_button != null) {
            reset_button.remove();
        }
        this.startButton.style.display = 'block';
        this.color_button.style.display = 'block';
        this.opponent_button.style.display = 'block';
        this.time_control_button.style.display = 'block';
        this.turnIndicator.hidden = true;
        this.update_material_diff(0);
        this.offset = 7;
        this.direction = -1;
        this.time_control_button.disabled = false;
        this.color_button.disabled = false;
        this.opponent_button.disabled = false;
        this.resignButton.disabled = true;
        await this.makeMove(this.gameID, ["reset"]);
        await this.fetchGameState();
        this.setColor({ target: { getAttribute: () => 'white' } });
        this.renderLabels("white");
        this.toggleDropdown("color-drop-cont", this.color_button);
    }


    // function to send user input (move) to backend to proccess
    // frontend -> backend (but also backend->frontend via returns i.e. response)
    async makeMove(gameID, move) {
        try {
            const response = await fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                // convert move list to json to send to backend
                body: JSON.stringify({ move, gameID })
            });
            // response contains the result of backend attempting to apply move
            const result = await response.json();
            if (result.status === 'reset' || result.status === 'game saved') {
                // pass
            } else {
                if (result.error) {
                    if (result.error === "invalid") {
                        this.flashInvalidMove(document.querySelector(`[data-coordinate='${move[0]}']`),
                            document.querySelector(`[data-coordinate='${move[1]}']`));
                    } else if (result.error === "king safety") {
                        this.flashInvalidMove(document.querySelector(`[data-coordinate='${result.coords[0]}']`),
                            document.querySelector(`[data-coordinate='${result.coords[0]}']`));
                    }
                } else if (result.status === 'end') { // game over
                    if (result.promotion) {
                        this.promoteQueen(result.promotion);
                    }
                    this.fetchGameState();
                    this.endGame(result.end_result);
                } else if (result.status === 'move applied') { // proceed with game
                    this.addIncrement(result.turn);
                    this.updateBoard(result.w_coords, result.b_coords, result.turn, result.promotion);
                    this.update_material_diff(result.material_diff);
                    return 1;
                } else {
                    alert("Error in response from makeMove");
                }
            }
        } catch (error) {
            console.error("Error during makeMove: ", error);
        }
    }


    // method to get initial game state
    // backend -> frontend
    async fetchGameState() {
        const response = await fetch('/state');
        const state = await response.json();
        this.renderBoard(state.w_coords, state.b_coords);
        this.updateTurnIndicator(state.turn);
    }


    // method to handle user clicking on squares
    // waits for two different squares to be slected then sends them to makeMove
    async handleClick(event) {
        if (this.turnIndicator.hidden === false) {
            const square = event.target.closest('.square');
            if (!square) return;
            // check if user has already selected a square
            if (this.selectedSquare) {
                if (this.selectedSquare != square) {
                    const move = [this.selectedSquare.dataset.coordinate, square.dataset.coordinate];
                    const res = await this.makeMove(this.gameID, move);
                    this.selectedSquare.classList.remove('selected');
                    this.selectedSquare = null;

                    // call makemove again if bot is playing
                    if (res === 1 && this.opponent !== "pnp") {
                        const res2 = await this.makeMove(this.gameID, [this.opponent]);
                        if (res2 === 1) {
                            console.log("Bot move applied successfully.")
                        } else {
                            console.log("Bot move failed.")
                        }
                    }

                } else {
                    this.flashInvalidMove(this.selectedSquare, this.selectedSquare);
                    this.selectedSquare.classList.remove('selected');
                    this.selectedSquare = null;
                }

            } else { // add square to selected class and wait for another click
                this.selectedSquare = square;
                this.selectedSquare.classList.add('selected');
            }
        }
    }


    // Handle drag start event
    handleDragStart(event) {
        if (this.turnIndicator.hidden === false) {
            const square = event.target.closest('.square');
            if (square) {
                event.dataTransfer.setData('text/plain', square.dataset.coordinate);
                event.dataTransfer.effectAllowed = 'move';
                square.classList.add('dragging');
            }
        }
    }

    // Handle drag over event
    handleDragOver(event) {
        if (this.turnIndicator.hidden === false) {
            event.preventDefault();
        }
    }

    // Handle drop event
    async handleDrop(event) {
        if (this.turnIndicator.hidden === false) {
            event.preventDefault();
            const fromCoord = event.dataTransfer.getData('text/plain');
            const square = event.target.closest('.square');
            if (square) {
                const toCoord = square.dataset.coordinate;
                const move = [fromCoord, toCoord];
                const res = await this.makeMove(this.gameID, move);

                if (res === 1 && this.opponent !== "pnp") {
                    const res2 = await this.makeMove(this.gameID, [this.opponent]);
                    if (res2 === 1) {
                        console.log("Bot move applied successfully.");
                    } else {
                        console.log("Bot move failed.");
                    }
                }
            }
        }
    }

    // Handle drag end event
    handleDragEnd(event) {
        if (this.turnIndicator.hidden === false) {
            const square = event.target.closest('.square');
            if (square) {
                square.classList.remove('dragging');
            }
        }
    }


    // function to update board handling promotions
    updateBoard(w_coords, b_coords, turn, promotion) {
        if (promotion) {
            this.promoteQueen(promotion)
        }
        this.renderBoard(w_coords, b_coords);
        this.updateTurnIndicator(turn);
        this.toggleTimers(turn);

    }


    // render board given piece coords
    renderBoard(w_coords, b_coords) {
        this.gameContainer.innerHTML = '';
        // create hmtl elements for all 64 squares
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('button');
                // add square css and light/dark bg dependent on the diagonal (c1+c2)%2==0
                square.classList.add('square', (row + col) % 2 === 0 ? 'light' : 'dark');
                // 7-row adds white pieces at the bottom
                // want to dynamically change this to reflect color user is playing
                square.dataset.coordinate = `${this.offset + this.direction*row},${col}`;
                // `${7 - row},${col}` ~= "7-row,col"
                // add dragover and drop event listeners
                square.addEventListener('dragover', (event) => this.handleDragOver(event));
                square.addEventListener('drop', (event) => this.handleDrop(event));
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
            if (square) { // coord of captured piece is [-1,-1] => no square at [-1,-1]
                const img = document.createElement('img');
                img.src = this.getPieceImageUrl(names[index], color);
                img.classList.add('piece');
                img.setAttribute('draggable', true);
                img.addEventListener('dragstart', (event) => this.handleDragStart(event));
                img.addEventListener('dragend', (event) => this.handleDragEnd(event));
                square.appendChild(img);
            }
        });
    }


    // method to render the labels of rows/cols
    renderLabels(color) {
        // create column labels
        this.columnLabels.innerHTML = '';  
        const columns = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
        columns.forEach(letter => {
            const label = document.createElement('div');
            label.className = 'coordinate-label';
            label.innerText = letter;
            this.columnLabels.appendChild(label);
        });
        // create row labels
        this.rowLabels.innerHTML = '';
        if (color === 'black') {
            var rows = ['1', '2', '3', '4', '5', '6', '7', '8'];
        } else {
            var rows = ['8', '7', '6', '5', '4', '3', '2', '1'];
        }
        rows.forEach(row => {
            const label = document.createElement('div');
            label.className = 'coordinate-label';
            label.innerText = row;
            this.rowLabels.appendChild(label);
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


    // method to start game and create turn indicator text
    async startGame() {
        this.startButton.style.display = 'none';
        this.color_button.style.display = 'none';
        this.opponent_button.style.display = 'none';
        this.time_control_button.style.display = 'none';
        this.turnIndicator.hidden = false;
        this.startTimer("white");
        this.time_control_button.disabled = true;
        this.color_button.disabled = true;
        this.opponent_button.disabled = true;
        this.resignButton.disabled = false;
        if (this.opponent !== "pnp" && this.offset === 0) { // bot is white
            console.log("Bot is playing...", this.opponent, "random: ", this.opponent === "random", "minimax: ", this.opponent === "minimax")
            const res2 = await this.makeMove(this.gameID, [this.opponent]);
            if (res2 === 1) {
                console.log("Bot move applied successfully.")
            } else {
                console.log("Bot move failed.")
            }
        }
    }

    
    // method to stop clocks, show game ending message and reset button
    async endGame(input) {
        clearInterval(this.timerHandles.white);
        clearInterval(this.timerHandles.black);
        const message_row = document.getElementById("message-row");
        const txt = this.getEnding(input);
        const message = document.createElement('div');
        message.innerText = txt;
        message.classList.add('end-message');
        message_row.appendChild(message);
        const reset_row = document.getElementById("reset-row")
        const button = document.createElement('button');
        button.addEventListener('click', () => this.resetGame());
        button.classList.add('reset-button', 'button');
        button.textContent = "Reset";
        reset_row.appendChild(button);
        if (this.opponent === "pnp") {
            var opp_save = "Pass and Play";
        } else if (this.opponent === "random") {
            var opp_save = "Random Bot";
        } else if (this.opponent === "minimax") {
            var opp_save = "Minimax Bot";
        } else {
            console.error("Error in endGame: invalid opponent");
        }
        if (this.direction === -1) {
            var color_save = "White";
        } else {
            var color_save = "Black";
        }
        await this.makeMove(this.gameID, ["save game", opp_save, color_save]);
        this.resignButton.disabled = true;
    }


    // params: int id of game ending, returns: string corresponding to ending
    getEnding(input) {
        // Determine ending based on the input
        switch (input) {
            case 0:
                return "White has flagged. Black wins. Game over.";
            case 1:
                return "Black has flagged. White wins. Game over.";
            case 2:
                return "White checkmated Black. White wins. Game over.";
            case 3:
                return "White stalemated Black. It's a draw. Game over.";
            case 4:
                return "Black checkmated White. Black wins. Game over.";
            case 5:
                return "Black stalemated White. It's a draw. Game over.";
            case 6:
                return "Threefold repetition reached. It's a draw. Game over.";
            case 7:
                return "Player has resigned. Bot wins.";
            default:
                return "Game ended in error.";
        }
    }


    // method to show/hide dropdown menu
    toggleDropdown(dropdownId, button) {
        // hide other dropdowns
        document.querySelectorAll('.dropdown-content').forEach((content) => {
            if (content.id !== dropdownId) {
                content.classList.remove('show');
                content.previousElementSibling.classList.remove('active');
            }
        });

        const dropdownContent = document.getElementById(dropdownId);
        dropdownContent.classList.toggle('show');
        button.classList.toggle('active');
    }


    // method to change the time control
    setTimeControl(event) {
        const time = event.target.getAttribute('data-time');
        var time_arr = JSON.parse(time);
        this.topTimer.innerText = time_arr[0] + ":00";
        this.bottomTimer.innerText = time_arr[0] + ":00";
        this.increment = time_arr[1];
        this.toggleDropdown("time-drop-cont", this.time_control_button); // hide dropdown after selection
    }


    // switches color of pieces user is playing as
    setColor(event) {
        const color = event.target.getAttribute('data-color');
        this.color_button.innerText = "Playing as " + color;
        this.offset = color === 'white' ? 7 : 0;
        this.direction = color === 'white' ? -1 : 1;
        if (color === 'white') {
            this.topTimer.classList.remove('white-timer');
            this.topTimer.classList.add('black-timer');
            this.bottomTimer.classList.remove('black-timer');
            this.bottomTimer.classList.add('white-timer');
        } else {
            this.topTimer.classList.remove('black-timer');
            this.topTimer.classList.add('white-timer');
            this.bottomTimer.classList.remove('white-timer');
            this.bottomTimer.classList.add('black-timer');
        }
        this.fetchGameState();  //re-render board
        this.renderLabels(color);
        this.toggleDropdown("color-drop-cont", this.color_button); // hide dropdown after selection
    }


    // changes the opponent
    setOpponent(event) {
        // get opponent name from button data-opp attribute
        this.opponent = event.target.getAttribute('data-opp');
        if (this.opponent === "pnp") {
            this.opponent_displayed.innerText = "Pass and Play";
        } else {
            this.opponent_displayed.innerText = "Opponent: " + this.opponent;
        }
        this.toggleDropdown("opp-drop-cont", this.opponent_button);
    }


    // method to update the turn indicator based on the current turn
    updateTurnIndicator(turn) {
        this.turnIndicator.style.background = turn === 1 ? "black" : "white";
        this.turnIndicator.style.color = turn === 1 ? "white" : "black";
        this.turnIndicator.innerText = turn === 1 ? "Black to move" : "White to move";
    }


    // toggle the timers
    toggleTimers(turn) {
        if (turn === 1) {
            clearInterval(this.timerHandles.white);
            this.startTimer('black');
        } else {
            clearInterval(this.timerHandles.black);
            this.startTimer('white');
        }
    }


    // method to start timers and check if timer reached 0
    startTimer(color) {
        const timerElement = color === 'white' ? document.getElementsByClassName('white-timer')[0] : document.getElementsByClassName('black-timer')[0];
        clearInterval(this.timerHandles[color]);
        this.timerHandles[color] = setInterval(() => {
            // get time in seconds
            let time = this.parseTime(timerElement.innerText);
            time--;
            // need to inform backend a timer ran out
            if (time <= 0 && this.gameRunning) {
                clearInterval(this.timerHandles[color]);
                timerElement.innerText = '00:00';
                this.makeMove(this.gameID, [null, color]);
                this.gameRunning = false;
            } else {
                // show user they're running out of time
                if (time <= 20) {
                    if (!timerElement.classList.contains('timer-trouble')) {
                        timerElement.classList.add('time-trouble');
                    }
                }
                // show user time in MM:SS
                timerElement.innerText = this.formatTime(time);
            }
        }, 1000); // delay set to 1 second
    }


    // method to add increment to turn's timer
    addIncrement(turn) {
        // if turn=1, color=black
        const timerElement = turn === 1 ? this.topTimer : this.bottomTimer;
        let time = this.parseTime(timerElement.innerText);
        time += this.increment;
        timerElement.innerText = this.formatTime(time);
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


    // input form: {'index': piece id, 'color': piece color, 'coord': piece position}
    promoteQueen(input) {
        // only need to update letter in names array
        // render board will update the image
        let names = input.color ? this.names_b : this.names_w;
        names[input.index] = 'Q';
    }


    // method to flash squares red for invalid move
    flashInvalidMove(square1, square2) {
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


    // method to update the material counters
    update_material_diff(diff) {
        if (diff > 0) {
            this.bot_mat_cnt.innerText = '+' + diff
            this.bot_mat_cnt.hidden = false
            this.top_mat_cnt.hidden = true
        } else if (diff < 0) {
            this.top_mat_cnt.innerText = '+' + Math.abs(diff)
            this.top_mat_cnt.hidden = false
            this.bot_mat_cnt.hidden = true
        } else {
            this.top_mat_cnt.hidden = true
            this.bot_mat_cnt.hidden = true
        }
    }
}


// make ChessBoard object when page loads
document.addEventListener('DOMContentLoaded', () => {
    new ChessBoard();
});

// Close the dropdown if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        document.querySelectorAll('.dropdown-content').forEach((content) => {
            content.classList.remove('show');
            content.previousElementSibling.classList.remove('active');
        });
    }
}
