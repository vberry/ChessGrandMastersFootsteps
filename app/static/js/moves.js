function updateMoveHistory(playerMove, correctMove, opponentMove, comment, opponentComment, isCorrect) {
    const moveHistoryBody = document.querySelector('#move-history tbody');
    
    // Créer deux lignes : une pour les coups, une pour les commentaires
    const moveRow = document.createElement('tr');
    const commentRow = document.createElement('tr');
    
    // Numéro de l'échange
    const exchangeNumber = moveHistoryBody.children.length / 2 + 1;
    
    // Cellule pour le numéro de l'échange
    const exchangeCell = document.createElement('td');
    exchangeCell.textContent = exchangeNumber;
    moveRow.appendChild(exchangeCell);
    
    // Cellule pour le coup des Blancs
    const whiteMoveCell = document.createElement('td');
    whiteMoveCell.textContent = playerMove;
    if (correctMove === undefined) {
        whiteMoveCell.innerHTML += `<br><small>(incorrect)</small>`;
    } else if (playerMove !== correctMove) {
        whiteMoveCell.innerHTML += `<br><small>(correct: ${correctMove})</small>`;
    } else {
        whiteMoveCell.innerHTML += `<br><small>(correct)</small>`;
    }      
    moveRow.appendChild(whiteMoveCell);
    
    // Cellule pour le coup des Noirs
    const blackMoveCell = document.createElement('td');
    blackMoveCell.textContent = opponentMove || '';
    moveRow.appendChild(blackMoveCell);
    
    // Ligne de commentaire qui s'étend sur toute la largeur
    const commentCell = document.createElement('td');
    commentCell.setAttribute('colspan', '3');
    commentCell.classList.add('move-comment');
    
    // Ajouter les commentaires s'ils existent
    const commentTexts = [];
    if (comment) commentTexts.push(comment);
    if (opponentComment) commentTexts.push(opponentComment);
    
    commentCell.textContent = commentTexts.join(' ');
    
    // Masquer la ligne de commentaire si aucun commentaire
    commentRow.appendChild(commentCell);
    commentRow.style.display = commentTexts.length ? 'table-row' : 'none';
    
    // Ajouter les lignes au tableau
    moveHistoryBody.appendChild(moveRow);
    moveHistoryBody.appendChild(commentRow);
    
    // Scroller automatiquement vers le bas
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

            // 🔴 Annuler immédiatement le coup illégal
            setTimeout(() => board.position(previousPosition), 100);

            // 🔥 Ajouter effet de tremblement sur la pièce
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
        showMessage("Une erreur est survenue: " + error.message, false);

        // 🔴 Annuler immédiatement le coup illégal
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