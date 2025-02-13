let board = null;
        
function updateMoveHistory(playerMove, correctMove, opponentMove, comment, opponentComment) {
    const moveHistory = document.querySelector('#move-history .history-content');
    const moveEntry = document.createElement('div');
    
    let moveContent = `<div><em>Vous:</em> <strong>${playerMove}</strong>`;
    if (playerMove !== correctMove) {
        moveContent += ` (correct: ${correctMove})`;
    }
    if (comment) {
        moveContent += `<div class="comment">${comment}</div>`;
    }
    moveContent += '</div>';
    
    if (opponentMove) {
        moveContent += `<div><em>Adversaire:</em> <strong>${opponentMove}</strong>`;
        if (opponentComment) {
            moveContent += `<div class="comment">${opponentComment}</div>`;
        }
        moveContent += '</div>';
    }

    moveEntry.innerHTML = moveContent;
    moveHistory.appendChild(moveEntry);
    moveHistory.scrollTop = moveHistory.scrollHeight;
}

function initializeBoard() {
    console.log('Initialisation du plateau...');
    board = Chessboard('board', {
        position: boardFen, 
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png',
        showNotation: true,
        draggable: false,
        orientation: userSide
    });

    window.addEventListener('resize', board.resize);
}

function checkJQuery() {
    if (window.jQuery) {
        if (window.Chessboard) {
            initializeBoard();
        } else {
            console.log('En attente de Chessboard.js...');
            setTimeout(checkJQuery, 100);
        }
    } else {
        console.log('En attente de jQuery...');
        setTimeout(checkJQuery, 100);
    }
}

document.addEventListener('DOMContentLoaded', checkJQuery);

function showMessage(text, isSuccess) {
    const messageDiv = document.getElementById('message');
    messageDiv.className = 'message ' + (isSuccess ? 'success' : 'error');
    messageDiv.innerHTML = text.replace('\n', '<br>');
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function submitMove() {
    var moveInput = document.getElementById("move-input");
    var submitBtn = document.getElementById("submit-btn");
    var move = moveInput.value.trim();
    
    if (!move) {
        showMessage("Veuillez entrer un coup", false);
        return;
    }

    submitBtn.disabled = true;

    var formData = new FormData();
    formData.append("game_id", gameId);
    formData.append("move", move);

    fetch('/submit-move', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showMessage(data.error, false);
            if (!data.is_valid_format) {
                moveInput.value = '';
                submitBtn.disabled = false;
                return;
            }
            return;
        }

        document.getElementById("score").textContent = data.score;

        updateMoveHistory(
            move,
            data.correct_move,
            data.opponent_move,
            data.comment,
            data.opponent_comment
        );
        
        let message = data.is_correct ? 
            "✅ Bravo ! Coup correct." : 
            `❌ Incorrect. Le bon coup était : ${data.correct_move}`;
            
        if (!data.is_correct && data.hint) {
            message += `\n${data.hint}`;
        }
        
        showMessage(message, data.is_correct);

        board.position(data.board_fen);
        
        if (data.last_opponent_move) {
            setTimeout(() => {
                const lastMoveElement = document.getElementById("last-move");
                if (lastMoveElement) {
                    lastMoveElement.textContent = 
                        "Dernier coup joué : " + data.last_opponent_move;
                }
            }, 500);
        }

        moveInput.value = '';

        if (data.game_over) {
            document.getElementById("status").textContent = "🎉 Partie terminée !";
            submitBtn.disabled = true;
            moveInput.disabled = true;
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showMessage("Une erreur est survenue", false);
    })
    .finally(() => {
        if (!document.getElementById("status").textContent.includes("terminée")) {
            submitBtn.disabled = false;
        }
    });
}

document.getElementById("move-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        submitMove();
    }
});