// Fonction pour initialiser le jeu
function initializeHistory() {
    // Si le joueur est noir, faire une requête pour obtenir le premier coup du bot
    if (userSide === 'black') {
        // Créer un FormData pour la requête
        var formData = new FormData();
        formData.append("game_id", gameId);
        
        // Demander au serveur le premier coup du bot
        fetch('/get-first-move', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (!data.error) {
                // Mettre à jour le plateau avec le premier coup du bot
                board.position(data.board_fen);
                
                // Mettre à jour l'historique avec le premier coup du bot
                updateMoveHistory(
                    null,           // Pas de coup soumis par le joueur
                    null,           // Pas de coup correct
                    data.opponent_move, // Le coup du bot
                    null,           // Pas de commentaire joueur
                    data.opponent_comment // Commentaire du bot s'il y en a un
                );
                
                // Mettre à jour l'affichage du dernier coup joué
                const lastMoveElement = document.getElementById("last-move");
                if (lastMoveElement) {
                    lastMoveElement.textContent = "Dernier coup joué : " + data.opponent_move;
                }
            }
        })
        .catch(error => {
            console.error('Erreur lors de la récupération du premier coup:', error);
        });
    }
}

function updateMoveHistory(playerMove, correctMove, opponentMove, comment, opponentComment, moveEval = null) {
    const moveHistoryBody = document.querySelector('#move-history tbody');
    
    // CAS SPÉCIAL: Premier coup du bot quand le joueur est noir
    if (userSide === 'black' && !playerMove && opponentMove && moveHistoryBody.children.length === 0) {
        const moveRow = document.createElement('tr');
        const commentRow = document.createElement('tr');
        
        const exchangeCell = document.createElement('td');
        exchangeCell.textContent = "1";
        moveRow.appendChild(exchangeCell);
        
        const whiteMoveCell = document.createElement('td');
        whiteMoveCell.textContent = opponentMove;
        moveRow.appendChild(whiteMoveCell);
        
        const blackMoveCell = document.createElement('td');
        moveRow.appendChild(blackMoveCell);
        
        const commentCell = document.createElement('td');
        commentCell.setAttribute('colspan', '3');
        commentCell.classList.add('move-comment');
        commentCell.textContent = opponentComment || '';
        commentRow.appendChild(commentCell);
        commentRow.style.display = opponentComment ? 'table-row' : 'none';
        
        moveHistoryBody.appendChild(moveRow);
        moveHistoryBody.appendChild(commentRow);
        return;
    }
    
    const isPlayerWhite = userSide === 'white';
    let exchangeNumber;
    
    if (isPlayerWhite) {
        exchangeNumber = Math.ceil((moveHistoryBody.children.length + 1) / 2);
    } else {
        if (playerMove && !opponentMove) {
            const lastMoveRow = moveHistoryBody.lastElementChild && moveHistoryBody.lastElementChild.previousElementSibling;
            
            if (lastMoveRow && lastMoveRow.cells[2].textContent === '') {
                lastMoveRow.cells[2].textContent = playerMove;

                if (playerMove !== correctMove && correctMove && moveEval?.isLastChance ) {
                    lastMoveRow.cells[2].innerHTML += `<br><small>(correct: ${correctMove})</small>`;
                }
                
                if (moveEval && moveEval.display && playerMove !== correctMove) {
                    lastMoveRow.cells[2].innerHTML += `<br><small>(${moveEval.display})</small>`;
                }
                
                const commentRow = lastMoveRow.nextElementSibling;
                if (commentRow) {
                    const commentCell = commentRow.cells[0];
                    if (comment) {
                        commentCell.textContent = comment;
                        commentRow.style.display = 'table-row';
                    }
                }
                
                const moveHistory = document.querySelector('#move-history .history-content');
                moveHistory.scrollTop = moveHistory.scrollHeight;
                
                return;
            }
        }
        exchangeNumber = Math.ceil((moveHistoryBody.children.length + 1) / 2);
    }
    
    const moveRow = document.createElement('tr');
    const commentRow = document.createElement('tr');
    
    const exchangeCell = document.createElement('td');
    exchangeCell.textContent = exchangeNumber;
    moveRow.appendChild(exchangeCell);
    
    const whiteMoveCell = document.createElement('td');
    if (isPlayerWhite && playerMove) {
        whiteMoveCell.textContent = playerMove;

        if (playerMove !== correctMove && correctMove && (moveEval?.isLastChance )) {
            whiteMoveCell.innerHTML += `<br><small>(correct: ${correctMove})</small>`;
            console.log(moveEval?.isLastChance)
        }
        
        if (moveEval && moveEval.display && playerMove !== correctMove) {
            whiteMoveCell.innerHTML += `<br><small>(${moveEval.display})</small>`;
        }

    } else if (!isPlayerWhite && opponentMove) {
        whiteMoveCell.textContent = opponentMove;
    } else {
        whiteMoveCell.textContent = '';
    }
    moveRow.appendChild(whiteMoveCell);
    
    const blackMoveCell = document.createElement('td');
    if (!isPlayerWhite && playerMove) {
        blackMoveCell.textContent = playerMove;

        if (playerMove !== correctMove && correctMove && (moveEval?.isLastChance )) {
            blackMoveCell.innerHTML += `<br><small>(correct: ${correctMove})</small>`;
        }
        
        if (moveEval && moveEval.display && playerMove !== correctMove) {
            blackMoveCell.innerHTML += `<br><small>(${moveEval.display})</small>`;
        }

    } else if (isPlayerWhite && opponentMove) {
        blackMoveCell.textContent = opponentMove;
    } else {
        blackMoveCell.textContent = '';
    }
    moveRow.appendChild(blackMoveCell);
    
    const commentCell = document.createElement('td');
    commentCell.setAttribute('colspan', '3');
    commentCell.classList.add('move-comment');
    
    const commentTexts = [];
    if (comment) commentTexts.push(comment);
    if (opponentComment) commentTexts.push(opponentComment);
    
    commentCell.textContent = commentTexts.join(' ');
    commentRow.appendChild(commentCell);
    commentRow.style.display = commentTexts.length ? 'table-row' : 'none';
    
    moveHistoryBody.appendChild(moveRow);
    moveHistoryBody.appendChild(commentRow);
    
    const moveHistory = document.querySelector('#move-history .history-content');
    moveHistory.scrollTop = moveHistory.scrollHeight;
}



function handleMove(source, target) {
    let moveToSubmit = source + target;  // Envoie simplement le coup en UCI
    const previousPosition = board.fen(); // Sauvegarde la position avant le coup

    console.log("Coup à soumettre:", moveToSubmit);

    // Stopper le timer pendant le traitement du coup
    if (typeof window.stopTimer === 'function') {
        window.stopTimer();
    } else {
        console.error("La fonction stopTimer n'est pas disponible");
    }

    var formData = new FormData();
    formData.append("game_id", gameId);
    formData.append("move", moveToSubmit);

    fetch('/submit-move', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erreur HTTP ${response.status}`); 
        }
        return response.json();
    })
    .then(data => {
        console.log("Réponse du serveur:", data);
        
        if (data.error) {
            showMessage(data.error, false);

            // Annuler immédiatement le coup illégal
            setTimeout(() => board.position(previousPosition), 100);

            // Ajouter effet de tremblement sur la pièce
            animateShakePiece(source);
            
            // Redémarrer le timer puisque le coup est invalide
            if (typeof window.startTimer === 'function') {
                window.startTimer();
            }
            return;
        }

        // Afficher les coups alternatifs pour la position précédente
        if (data.previous_position_best_moves && data.previous_position_best_moves.length > 0) {
            displayAlternativeMoves(data.previous_position_best_moves, moveToSubmit);
        }

        // Mise à jour du score
        if (data.score !== undefined) {
            document.getElementById("score").textContent = data.score;
        }

        if (data.move_evaluation) {
        data.move_evaluation.attemptsUsed = data.attempts_used || 0;
        data.move_evaluation.isLastChance = data.is_last_chance || false;
        }

        // Mise à jour du plateau avec le coup joué
        board.position(data.board_fen);

        // Mettre à jour l'historique des coups
        if (userSide === 'black') {
            // Si le joueur est noir, mettre à jour avec le coup du joueur seulement
            updateMoveHistory(
                data.submitted_move,
                data.correct_move,
                null,
                data.comment,
                null,
                data.move_evaluation
            );
        } else {
            // Si le joueur est blanc, mettre à jour avec le coup du joueur et la réponse du bot
            updateMoveHistory(
                data.submitted_move,
                data.correct_move,
                data.opponent_move,
                data.comment,
                data.opponent_comment,
                data.move_evaluation
            );
        }

        // Si le joueur est noir et que le bot (blanc) a joué un coup
        if (userSide === 'black' && data.opponent_move) {
            // Ajouter une nouvelle entrée pour le coup du bot blanc
            setTimeout(() => {
                updateMoveHistory(
                    null,
                    null,
                    data.opponent_move,
                    null,
                    data.opponent_comment
                );
            }, 500); // Petit délai pour que l'UI se mette à jour correctement
        }

        // Vérifier si la partie est terminée
        if (data.game_over) {
            document.getElementById("status").textContent = "🎉 Partie terminée !";
            if (typeof window.stopTimer === 'function') {
                window.stopTimer(); // Arrêter le timer définitivement
            }
        } else {
            // Réinitialiser le timer avec le nouveau temps de départ
            if (data.move_start_time && typeof window.resetTimer === 'function') {
                window.resetTimer(data.move_start_time);
            }
            
            // Émettre un événement personnalisé pour le timer
            const event = new CustomEvent('moveSubmitted', { 
                detail: { result: data } 
            });
            document.dispatchEvent(event);
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showMessage("Une erreur est survenue move.js: " + error.message, false);

        // Annuler immédiatement le coup illégal
        setTimeout(() => board.position(previousPosition), 100);

        if (typeof animateShakePiece === 'function') {
            animateShakePiece(source);
        }
        
        // Redémarrer le timer en cas d'erreur
        if (typeof window.startTimer === 'function') {
            window.startTimer();
        }
    });

    return false;
}