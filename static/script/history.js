const chessBoards = {};

class ChessBoardHistory {

    constructor(init_gameID, init_moves, init_color) {
        this.gameMoves = init_moves;
        this.gameContainer = document.getElementById(`game-container-${init_gameID}`);
        this.gameContainerWrapper = document.getElementById(`game-container-wrapper-${init_gameID}`);
        this.rowLabels = document.getElementById(`row-labels-${init_gameID}`);
        this.columnLabels = document.getElementById(`column-labels-${init_gameID}`);
        this.leftButton = document.getElementById(`left-${init_gameID}`);
        this.rightButton = document.getElementById(`right-${init_gameID}`);
        this.leftButton.addEventListener('click', () => this.moveLeft(init_gameID));
        this.rightButton.addEventListener('click', () => this.moveRight(init_gameID));
        this.names_w = {
            0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
            8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
        };
        this.names_b = {
            0: "K", 1: "Q", 2: "R", 3: "R", 4: "N", 5: "N", 6: "B", 7: "B",
            8: "P", 9: "P", 10: "P", 11: "P", 12: "P", 13: "P", 14: "P", 15: "P"
        };
        this.starting_coords = [
            [[0,4], [0,3], [0,0], [0,7], [0,1],[0,6], [0,2], [0,5], 
            [1,0], [1,1], [1,2], [1,3], [1,4], [1,5], [1,6], [1,7]],
            [[7,4], [7,3], [7,0], [7,7], [7,1], [7,6], [7,2], [7,5], 
            [6,0], [6,1], [6,2], [6,3], [6,4], [6,5], [6,6], [6,7]]
        ]
        if (init_color === 'White') {
            this.offset = 7;
            this.direction = -1;
        } else {
            this.offset = 0;
            this.direction = 1;
        }
        this.moveCounter = 0;
        this.coords = [this.starting_coords];
        this.renderBoard(this.starting_coords[0], this.starting_coords[1], init_gameID);
    }


    async makeMove(gameID, move) {
        try {
            console.log("history.js sending move: ", move);
            const response = await fetch(`/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ move, gameID })
            });
            const result = await response.json();
            console.log("history.js received response: ", result);
            if (result.status === 'move applied') {
                this.updateBoard(result.w_coords, result.b_coords, result.promotion, gameID);
                console.log("makeMove returning: ", [result.w_coords, result.b_coords]);
                return [result.w_coords, result.b_coords];
            } else {
                alert("Error in response from makeMove");
            }
        } catch (error) {
            console.error("Error during makeMove: ", error);
        }
    }


    updateBoard(w_coords, b_coords, promotion, update_gameID) {
        if (promotion) {
            this.promoteQueen(promotion);
        }
        this.renderBoard(w_coords, b_coords, update_gameID);
    }


    renderBoard(w_coords, b_coords, render_gameID) {
        this.gameContainer.innerHTML = '';
        for (let row = 0; row < 8; row++) {
            for (let col = 0; col < 8; col++) {
                const square = document.createElement('button');
                square.classList.add('square-hist', (row + col) % 2 === 0 ? 'light' : 'dark');
                square.dataset.coordinate = `${this.offset + this.direction*row},${col},${render_gameID}`;
                this.gameContainer.appendChild(square);
            }
        }
        this.renderPieces(w_coords, 0, render_gameID);
        this.renderPieces(b_coords, 1, render_gameID);
    }


    renderPieces(coords, color, renderP_gameID) {
        const names = color ? this.names_b : this.names_w;
        coords.forEach((coord, index) => {
            const square = document.querySelector(`[data-coordinate='${coord[0]},${coord[1]},${renderP_gameID}']`);
            if (square) {
                const img = document.createElement('img');
                img.src = this.getPieceImageUrl(names[index], color);
                img.classList.add('piece-hist');
                square.appendChild(img);
            }
        });
    }


    promoteQueen(input) {
        let names = input.color ? this.names_b : this.names_w;
        names[input.index] = 'Q';
        const square = document.querySelector(`[data-coordinate='${input.coord}']`);
        if (square) {
            const img = square.querySelector('img');
            img.src = this.getPieceImageUrl('Q', input.color);
        }
    }


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


    async moveLeft(left_gameID) {
        const chessBoard = chessBoards[left_gameID];
        if (chessBoard) {
            if (this.coords.length > 1) {
                this.coords.pop();
                const [w_coords, b_coords] = this.coords[this.coords.length - 1];
                const left_move = ["revert", w_coords, b_coords];
                const result = await this.makeMove(left_gameID, left_move);
                chessBoard.renderBoard(w_coords, b_coords, left_gameID);
                this.moveCounter -= 1;
            }
        } else {
            console.error(`No ChessBoard instance found for game ${left_gameID}`);
        }
    }

    async moveRight(right_gameID) {
        const chessBoard = chessBoards[right_gameID];
        if (chessBoard) {
            if (this.moveCounter < this.gameMoves.length && this.gameMoves[0].length > 0) {
                let right_move = this.gameMoves[this.moveCounter];
                console.log("move idx: ", this.moveCounter, "right_move: ", right_move);
                if (right_move.length === 2) { right_move.push("nothingtoseehere") }
                const [w_coords, b_coords] = await chessBoard.makeMove(right_gameID, right_move);
                this.coords.push([w_coords, b_coords]);
                this.moveCounter += 1;
            }
        } else {
            console.error(`No ChessBoard instance found for game ${right_gameID}`);
        }
    }
}


function getMovesById(gamesList, get_gameID) {
    const foundGame = gamesList.find(searchGame => searchGame.id === parseInt(get_gameID));
    let movesInJSON = foundGame.moves.replace(/{{/g, '[[').replace(/}}/g, ']]').replace(/{/g, '[').replace(/}/g, ']').replace(/"/g, '"');
    movesInJSON = `[${movesInJSON}]`;
    const mvs = JSON.parse(movesInJSON);
    const opp = foundGame.opponent;
    const color = foundGame.color;
    console.log("opp: ", opp, "color: ", color);
    return [mvs, opp, color];
}


document.addEventListener('DOMContentLoaded', () => {
    const boards = document.querySelectorAll('.game-history-container');
    boards.forEach(boardElement => {
        const ID = boardElement.id.split('-')[2];
        const game_info = getMovesById(games2js, ID)
        console.log("mv_lst: ", game_info[0], "opponent: ", game_info[1], "color played: ", game_info[2], "gameID: ", ID)
        const chessBoard = new ChessBoardHistory(ID, game_info[0][0], game_info[2]);
        chessBoards[ID] = chessBoard;
    });
    const gameTimes = document.querySelectorAll('.game-info');
    gameTimes.forEach(function(element) {
        const rawTime = element.getAttribute('data-time');
        const opponent = element.getAttribute('data-opponent');
        const date = new Date(rawTime);
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric', 
            hour: 'numeric', 
            minute: 'numeric', 
            hour12: true, 
            timeZoneName: 'short' 
        };
        const formattedTime = date.toLocaleString('en-US', options);
        element.innerHTML = `${formattedTime}<br>Opponent: ${opponent}`;
    });
});
