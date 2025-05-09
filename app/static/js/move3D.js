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

// Animation de tremblement pour une pièce (pour les coups illégaux)
function animateShakePiece(square) {
    const squareElement = document.querySelector(`.square-55d63[data-square="${square}"]`);
    if (!squareElement) return;
    
    const piece = squareElement.querySelector('.piece-417db');
    if (!piece) return;
    
    // Ajouter une classe pour l'animation
    piece.style.animation = 'shake 0.5s';
    
    // Style pour l'animation de tremblement si pas déjà défini
    if (!document.getElementById('shake-animation')) {
        const style = document.createElement('style');
        style.id = 'shake-animation';
        style.innerHTML = `
            @keyframes shake {
                0%, 100% { transform: translateX(0); }
                10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
                20%, 40%, 60%, 80% { transform: translateX(5px); }
            }
        `;
        document.head.appendChild(style);
    }
    
    // Supprimer l'animation après qu'elle soit terminée
    setTimeout(() => {
        piece.style.animation = '';
    }, 500);
}

// Gestion des coups avec animation
function handleMove(source, target) {
    // Récupérer la pièce à la position source
    const sourceElement = document.querySelector(`.square-55d63[data-square="${source}"]`);
    const piece = sourceElement ? sourceElement.querySelector('.piece-417db') : null;
    
    if (!piece) return false;
    
    // Sauvegarder la position précédente
    const previousPosition = board.fen();
    
    // Envoyer le coup au serveur
    let moveToSubmit = source + target;
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
    
    // Calculer la taille d'une case pour l'animation
    const boardElement = document.getElementById('board');
    const boardPosition = boardElement.getBoundingClientRect();
    const squareSize = boardPosition.width / 8;
    
    // Récupérer les éléments DOM des cases
    const toElement = document.querySelector(`.square-55d63[data-square="${target}"]`);
    
    if (!toElement) return false;
    
    // Calculer les positions de départ et d'arrivée
    const fromRect = sourceElement.getBoundingClientRect();
    const toRect = toElement.getBoundingClientRect();
    
    // Créer une copie de la pièce pour l'animation
    const pieceCopy = document.createElement('img');
    pieceCopy.src = piece.src;
    pieceCopy.alt = 'Moving piece';
    pieceCopy.classList.add('animating-piece');
    
    // Appliquer un style à la pièce animée
    pieceCopy.style.position = 'fixed';
    pieceCopy.style.zIndex = '9000';
    pieceCopy.style.width = `${squareSize}px`;
    pieceCopy.style.height = 'auto';
    pieceCopy.style.filter = 'drop-shadow(1px 2px 2px rgba(0, 0, 0, 0.3))';
    pieceCopy.style.pointerEvents = 'none';
    pieceCopy.style.willChange = 'transform';
    
    // Positionner initialement à la position de départ
    pieceCopy.style.left = `${fromRect.left}px`;
    pieceCopy.style.top = `${fromRect.top}px`;
    
    // Cacher la pièce d'origine immédiatement
    piece.style.opacity = '0';
    
    // Ajouter la pièce d'animation au body
    document.body.appendChild(pieceCopy);
    
    // Définir la transition pour un mouvement fluide
    pieceCopy.style.transition = 'left 0.3s ease-out, top 0.3s ease-out';
    
    // Variable pour suivre l'état de la réponse du serveur
    let serverResponseReceived = false;
    let newBoardFen = null;
    let moveSuccessful = false;
    
    // Déclencher immédiatement l'animation vers la position d'arrivée
    setTimeout(() => {
        pieceCopy.style.left = `${toRect.left}px`;
        pieceCopy.style.top = `${toRect.top}px`;
    }, 10);
    
    // Fetch en parallèle avec l'animation
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
        serverResponseReceived = true;
        
        if (data.error) {
            showMessage(data.error, false);
            
            // Inverser immédiatement l'animation pour montrer que le coup est illégal
            pieceCopy.style.transition = 'left 0.2s ease-in, top 0.2s ease-in';
            pieceCopy.style.left = `${fromRect.left}px`;
            pieceCopy.style.top = `${fromRect.top}px`;
            
            // Après l'animation inverse, restaurer la pièce originale
            setTimeout(() => {
                if (pieceCopy.parentNode) {
                    pieceCopy.parentNode.removeChild(pieceCopy);
                }
                
                // Restaurer l'opacité de la pièce d'origine
                if (piece && piece.parentNode) {
                    piece.style.opacity = '1';
                }
                
                // Annuler le coup illégal
                board.position(previousPosition, false);
                
                // S'assurer que les styles des pièces sont bien appliqués
                if (typeof applyStaticPieceStyles === 'function') {
                    window.startTimer();
                    setTimeout(applyStaticPieceStyles, 50);
                }
                
                // Ajouter effet de tremblement sur la pièce
                animateShakePiece(source);
            }, 220);
            return;
        }
        
        // Le coup est valide
        moveSuccessful = true;
        
        // Afficher les coups alternatifs pour la position précédente
        if (data.previous_position_best_moves && data.previous_position_best_moves.length > 0) {
            displayAlternativeMoves(data.previous_position_best_moves, moveToSubmit);
        }
        
        // Mise à jour du score
        if (data.score !== undefined) {
            document.getElementById("score").textContent = data.score;
        }
        
        // Stocker la nouvelle position FEN
        newBoardFen = data.board_fen;
        
        updateMoveHistory(
            data.submitted_move,  
            data.correct_move, 
            data.opponent_move, 
            data.comment, 
            data.opponent_comment,
            data.is_correct  
        );
        
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
        serverResponseReceived = true;
        console.error('Erreur complète:', error);
        showMessage("Une erreur est survenue", false);
        
        // Inverser l'animation pour revenir à la position initiale
        pieceCopy.style.transition = 'left 0.2s ease-in, top 0.2s ease-in';
        pieceCopy.style.left = `${fromRect.left}px`;
        pieceCopy.style.top = `${fromRect.top}px`;
        
        setTimeout(() => {
            if (pieceCopy.parentNode) {
                pieceCopy.parentNode.removeChild(pieceCopy);
            }
            
            // Restaurer l'opacité de la pièce d'origine
            if (piece && piece.parentNode) {
                piece.style.opacity = '1';
            }
            
            // Annuler le coup illégal
            board.position(previousPosition, false);
            
            // S'assurer que les styles des pièces sont bien appliqués
            if (typeof applyStaticPieceStyles === 'function') {
                window.startTimer();
                setTimeout(applyStaticPieceStyles, 50);
            }
            
            animateShakePiece(source);
        }, 220);
    })
    .finally(() => {
        // Après l'animation (300ms), supprimer la pièce d'animation et mettre à jour le plateau si nécessaire
        setTimeout(() => {
            // Supprimer la pièce d'animation
            if (pieceCopy.parentNode) {
                pieceCopy.parentNode.removeChild(pieceCopy);
            }
            
            // Si le coup est réussi et que la réponse du serveur est reçue
            if (moveSuccessful && serverResponseReceived && newBoardFen) {
                // Mettre à jour le plateau avec la nouvelle position
                board.position(newBoardFen, false);
                
                // S'assurer que les styles des pièces sont bien appliqués
                if (typeof applyStaticPieceStyles === 'function') {
                    setTimeout(applyStaticPieceStyles, 50);
                }
            } 
            // Si la réponse n'est pas encore reçue ou si le coup a échoué
            else if (!moveSuccessful) {
                // Restaurer l'opacité de la pièce d'origine
                if (piece && piece.parentNode) {
                    piece.style.opacity = '1';
                }
            }
        }, 320);
    });
    
    return false;
}