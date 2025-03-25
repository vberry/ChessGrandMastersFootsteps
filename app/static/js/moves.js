function updateMoveHistory(playerMove, correctMove, opponentMove, comment, opponentComment) {
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
    if (playerMove !== correctMove) {
        whiteMoveCell.innerHTML += `<br><small>(correct: ${correctMove})</small>`;
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