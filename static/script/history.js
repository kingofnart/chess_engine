const chessBoards = {};
const moveCounters = {};
const coords = {};

class ChessBoardHistory {

    constructor(init_gameID, init_moves) {
        this.gameMoves = init_moves;
        console.log("Moves found: ", this.gameMoves, " via id: ", init_gameID);
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
        this.renderBoard(
            [[0,4], [0,3], [0,0], [0,7], [0,1],
            [0,6], [0,2], [0,5], [1,0], [1,1], 
            [1,2], [1,3], [1,4], [1,5], [1,6], [1,7]],
            [[7,4], [7,3], [7,0], [7,7], [7,1], 
            [7,6], [7,2], [7,5], [6,0], [6,1], 
            [6,2], [6,3], [6,4], [6,5], [6,6], [6,7]],
            init_gameID
        );
    }


    async makeMove(gameID, move) {
        try {
            console.log("sending move: ", move, " and id: ", gameID)
            const response = await fetch(`/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ move, gameID })
            });
            const result = await response.json();
            if (result.status === 'move applied') {
                this.updateBoard(result.w_coords, result.b_coords, result.promotion, gameID);
                console.log("returning: ", [result.w_coords, result.b_coords])
                return [result.w_coords, result.b_coords];
            } else {
                alert("Error in response from makeMove");
                console.log("Backend didn't apply move: ");
            }
        } catch (error) {
            console.error("Error during makeMove: ", error);
        }
    }


    async fetchAndRender(fetch_gameID) {
        const response = await fetch(`/state`);
        const state = await response.json();
        this.renderBoard(state.w_coords, state.b_coords, fetch_gameID);
    }


    async fetchCoordinates() {
        const response = await fetch(`/state`);
        const state = await response.json();
        return [state.w_coords, state.b_coords];
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
                square.classList.add('square', (row + col) % 2 === 0 ? 'light' : 'dark');
                square.dataset.coordinate = `${7 - row},${col},${render_gameID}`;
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
                img.classList.add('piece');
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
        console.log("moveLEFT found chessboard with moves: ", chessBoard.gameMoves, " with id ", left_gameID)
        if (chessBoard) {
            const gameCoords = coords[left_gameID];
            console.log("coordinates list: ", gameCoords);
            if (gameCoords.length > 1) {
                gameCoords.pop();
                console.log("coordinates list after pop: ", gameCoords);
                const [w_coords, b_coords] = gameCoords[gameCoords.length - 1];
                console.log("current board state: (white): ", w_coords, "(black):", b_coords)
                const left_move = ["revert", w_coords, b_coords];
                const result = await this.makeMove(left_gameID, left_move);
                console.log("result: " , result, ", rendering board with coordinates: (white): ", w_coords, ", (black):", b_coords);
                chessBoard.renderBoard(w_coords, b_coords, left_gameID);
                moveCounters[left_gameID] -= 1;
            }
        } else {
            console.error(`No ChessBoard instance found for game ${left_gameID}`);
        }
    }

    async moveRight(right_gameID) {
        const chessBoard = chessBoards[right_gameID];
        console.log("moveRIGHT found chessboard with moves: ", chessBoard.gameMoves, " with id ", right_gameID)
        if (chessBoard) {
            if (moveCounters[right_gameID] < this.gameMoves.length && this.gameMoves[0].length > 0) {
                console.log("Moves list: ", this.gameMoves, ", index of move: ", moveCounters[right_gameID]);
                let right_move = this.gameMoves[moveCounters[right_gameID]];
                if (right_move.length === 2) { right_move.push("nothingtoseehere") }
                console.log("Move to be applied: ", right_move);
                const [w_coords, b_coords] = await chessBoard.makeMove(right_gameID, right_move);
                console.log("Coordinates received: (white): ", w_coords, "(black):", b_coords);
                coords[right_gameID].push([w_coords, b_coords]);
                console.log("updated to coords: ", coords[right_gameID]);
                moveCounters[right_gameID] += 1;
            }
        } else {
            console.error(`No ChessBoard instance found for game ${right_gameID}`);
        }
    }
}


function getMovesById(gamesList, get_gameID) {
    const foundGame = gamesList.find(searchGame => searchGame.id === parseInt(get_gameID));
    let movesInJSON = foundGame.moves.replace(/{{/g, '[').replace(/}}/g, ']').replace(/{/g, '[').replace(/}/g, ']').replace(/"/g, '"');
    movesInJSON = `[${movesInJSON}]`;
    const res = JSON.parse(movesInJSON);
    return res;
}


document.addEventListener('DOMContentLoaded', () => {
    const boards = document.querySelectorAll('.game-history-container');
    boards.forEach(boardElement => {
        const ID = boardElement.id.split('-')[2];
        const mv_lst = getMovesById(games2js, ID)
        const chessBoard = new ChessBoardHistory(ID, mv_lst);
        chessBoards[ID] = chessBoard;
        moveCounters[ID] = 0;
        // need to use .then because of async => not save the promise but the resolved value
        chessBoard.fetchCoordinates().then(coordinates => {
            coords[ID] = [coordinates];
        });
    });
    const gameTimes = document.querySelectorAll('.game-time');
    gameTimes.forEach(function(element) {
        const rawTime = element.getAttribute('data-time');
        const date = new Date(rawTime);
        const options = { year: 'numeric', month: 'long', day: 'numeric', 
            hour: 'numeric', minute: 'numeric', hour12: true, timeZoneName: 'short' };
        element.textContent = date.toLocaleString('en-US', options);
    });
});
