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

function displayAlternativeMoves(alternativeMoves, playerMove) {
    // Chercher ou créer le conteneur principal
    let alternativeMovesContainer = document.getElementById('alternative-moves-container');
    
    if (!alternativeMovesContainer) {
        // Créer le conteneur et l'ajouter directement au body
        alternativeMovesContainer = document.createElement('div');
        alternativeMovesContainer.id = 'alternative-moves-container';
        alternativeMovesContainer.className = 'alternative-moves-section';
        alternativeMovesContainer.innerHTML = '<h3>Coups alternatifs pour la position précédente:</h3><div class="alternative-moves-list"></div>';
        document.body.appendChild(alternativeMovesContainer);
    }
    
    const alternativeMovesList = alternativeMovesContainer.querySelector('.alternative-moves-list');
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
            <div class="move-comment"></div>
        `;
        alternativeMovesList.appendChild(moveElement);
    });
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