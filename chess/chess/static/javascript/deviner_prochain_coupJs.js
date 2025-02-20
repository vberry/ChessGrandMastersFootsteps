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
        draggable: true,  // Permet de déplacer les pièces avec la souris
        orientation: userSide,
        onDrop: handleMove  // Fonction appelée quand une pièce est déplacée
    });

    window.addEventListener('resize', board.resize);
}


function handleMove(source, target) {
    let moveToSubmit = source + target;  // Envoie simplement le coup en UCI
    const previousPosition = board.fen(); // Sauvegarde la position avant le coup

    console.log("Coup à soumettre:", moveToSubmit);

    var formData = new FormData();
    formData.append("game_id", gameId);
    formData.append("move", moveToSubmit);

    fetch('/submit-move', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showMessage(data.error, false);

            // 🔴 Annuler immédiatement le coup illégal
            setTimeout(() => board.position(previousPosition), 100);

            // 🔥 Ajouter effet de tremblement sur la pièce
            animateShakePiece(source);
            return;
        }

        // Afficher les coups alternatifs pour la position précédente
        if (data.previous_position_best_moves && data.previous_position_best_moves.length > 0) {
            displayAlternativeMoves(data.previous_position_best_moves, moveToSubmit);
        }

        // ✅ Mise à jour du score
        if (data.score !== undefined) {
            document.getElementById("score").textContent = data.score;
        }

        // ✅ Mise à jour du plateau avec le coup joué
        board.position(data.board_fen);

        updateMoveHistory(
            data.submitted_move,  
            data.correct_move, 
            data.opponent_move, 
            data.comment, 
            data.opponent_comment,
            data.is_correct  
        );

        // ✅ Vérifier si la partie est terminée
        if (data.game_over) {
            document.getElementById("status").textContent = "🎉 Partie terminée !";
        }
    })
    .catch(error => {
        console.error('Erreur complète:', error);
        showMessage("Une erreur est survenue", false);

        // 🔴 Annuler immédiatement le coup illégal
        setTimeout(() => board.position(previousPosition), 100);

        animateShakePiece(source);
    });

    return false;
}



// 🔥 Effet de tremblement sur la pièce en cas d'erreur
function animateShakePiece(square) {
    const pieceElement = document.querySelector(`.square-${square} img`);
    if (pieceElement) {
        pieceElement.style.transition = "transform 0.1s";
        pieceElement.style.transform = "translateX(-5px)";
        setTimeout(() => {
            pieceElement.style.transform = "translateX(5px)";
        }, 100);
        setTimeout(() => {
            pieceElement.style.transform = "translateX(0)";
        }, 200);
    }
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
        // Afficher les coups alternatifs pour la position précédente
        if (data.previous_position_best_moves && data.previous_position_best_moves.length > 0) {
            displayAlternativeMoves(data.previous_position_best_moves, move);
        }

        document.getElementById("score").textContent = data.score;

        updateMoveHistory(
            data.submitted_move,  // ✅ Le coup soumis est bien en notation SAN
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

// Ajoutez cette fonction dans deviner_prochain_coupJs.js
function displayAlternativeMoves(alternativeMoves, playerMove) {
    const alternativeMovesContainer = document.getElementById('alternative-moves-container');
    
    // Si le conteneur n'existe pas encore, créez-le
    if (!alternativeMovesContainer) {
        const gameInfo = document.querySelector('.game-info');
        const newContainer = document.createElement('div');
        newContainer.id = 'alternative-moves-container';
        newContainer.className = 'alternative-moves-section';
        newContainer.innerHTML = '<h3>Coups alternatifs pour la position précédente:</h3><div class="alternative-moves-list"></div>';
        gameInfo.appendChild(newContainer);
    }
    
    const alternativeMovesList = document.querySelector('.alternative-moves-list');
    alternativeMovesList.innerHTML = '';
    
    if (!alternativeMoves || alternativeMoves.length === 0) {
        alternativeMovesList.innerHTML = '<p>Aucune analyse disponible</p>';
        return;
    }
    
    // Trouver le coup joué par le joueur parmi les alternatives
    const playerMoveInfo = alternativeMoves.find(move => 
        move.uci.toLowerCase() === playerMove.toLowerCase() || 
        move.san.toLowerCase() === playerMove.toLowerCase()
    );
    
    // Afficher le coup du joueur en premier avec une indication
    if (playerMoveInfo) {
        const moveElement = document.createElement('div');
        moveElement.className = 'alternative-move-item player-move';
        
        moveElement.innerHTML = `
            <div class="move-indicator">✓</div>
            <div class="move-uci">${playerMoveInfo.uci}</div>
            <div class="move-san">(${playerMoveInfo.san})</div>
            <div class="move-score">${playerMoveInfo.display_score}</div>
            <div class="move-comment">Votre coup</div>
        `;
        alternativeMovesList.appendChild(moveElement);
    }
    
    // Afficher les autres alternatives
    alternativeMoves.forEach((move) => {
        // Ne pas réafficher le coup du joueur
        if (playerMoveInfo && move.uci === playerMoveInfo.uci) {
            return;
        }
        
        const moveElement = document.createElement('div');
        moveElement.className = 'alternative-move-item';
        
        moveElement.innerHTML = `
            <div class="move-indicator"></div>
            <div class="move-uci">${move.uci}</div>
            <div class="move-san">(${move.san})</div>
            <div class="move-score">${move.display_score}</div>
            <div class="move-strength">
                <div class="strength-bar" style="width: ${move.relative_strength}%"></div>
                <span>${move.relative_strength}%</span>
            </div>
        `;
        alternativeMovesList.appendChild(moveElement);
    });
}

document.getElementById("move-input").addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        event.preventDefault();
        submitMove();
    }
});
