// Ajout du style CSS pour le surlignage rouge directement dans le script
(function() {
    // Créer un élément style
    const style = document.createElement('style');
    style.textContent = `
        /* Style pour surligner une case en rouge */
        .highlight-red {
            background-color: rgba(255, 0, 0, 0.6) !important;
            box-shadow: inset 0 0 0 3px rgba(255, 0, 0, 0.8);
            transition: background-color 0.3s ease;
        }
    `;
    // Ajouter le style au head du document
    document.head.appendChild(style);
})();

// Fonction pour surligner une case en rouge brièvement
function highlightSquareRed(square) {
    // Trouver l'élément de la case
    const squareElement = document.querySelector(`.square-${square}`);
    
    if (squareElement) {
        // Ajouter une classe pour le surlignage rouge
        squareElement.classList.add('highlight-red');
        
        // Retirer la classe après un court délai
        setTimeout(() => {
            squareElement.classList.remove('highlight-red');
        }, 200); // 500ms de surlignage
    }
}

// Fonction de défilement améliorée pour l'historique des coups
function scrollMoveHistoryToBottom() {
    const moveHistory = document.querySelector('#move-history .history-content');
    if (moveHistory) {
        // Utiliser requestAnimationFrame pour s'assurer que le défilement 
        // se fait après que le navigateur a rendu les changements
        requestAnimationFrame(() => {
            moveHistory.scrollTop = moveHistory.scrollHeight;
            
            // Parfois une seule Frame n'est pas suffisante, on en ajoute une seconde pour être sûr
            requestAnimationFrame(() => {
                moveHistory.scrollTop = moveHistory.scrollHeight;
            });
        });
    }
}

// Fonction pour mettre à jour l'historique des coups
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
        
        // Faire défiler après avoir ajouté les lignes
        scrollMoveHistoryToBottom();
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
                
                // Faire défiler après avoir modifié une ligne existante
                scrollMoveHistoryToBottom();
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
    
    // Faire défiler vers le bas après ajout de nouvelles lignes
    scrollMoveHistoryToBottom();
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

            // Annuler immédiatement le coup illégal
            setTimeout(() => board.position(previousPosition), 100);

            // Surligner la case de destination en rouge
            highlightSquareRed(target);

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
        // Mise à jour du score
        if (data.score !== undefined) {
            document.getElementById("score").textContent = data.score;
            // Vérifier si score_percentage est défini avant de l'afficher
            if (data.score_percentage !== undefined) {
                document.getElementById("score-percentage").textContent = data.score_percentage + "%";
            }
            // Ne pas mettre à jour score_percentage s'il n'est pas défini
        }

        if (data.move_evaluation) {
        data.move_evaluation.attemptsUsed = data.attempts_used || 0;
        data.move_evaluation.isLastChance = data.is_last_chance || false;
        }

        // Vérifier si le coup soumis est différent du coup correct
        if (data.submitted_move !== data.correct_move && data.correct_move) {
            // Surligner la case de destination en rouge
            highlightSquareRed(target);
            
            // 1. D'abord, annuler le coup incorrect et revenir à la position précédente
            setTimeout(() => {
                board.position(previousPosition);
                //showMessage("Coup incorrect. Le coup correct est: " + data.correct_move, false);
                
                // Effet de tremblement sur la pièce
                if (typeof animateShakePiece === 'function') {
                    animateShakePiece(source);
                }
                
                // 2. Après 1 seconde, jouer le coup correct (sans la réponse de l'adversaire)
                setTimeout(() => {
                    // On a besoin d'une position intermédiaire avec uniquement le coup correct
                    // Si le serveur la fournit, utiliser cette position, sinon utiliser board_fen
                    const correctMoveFen = data.correct_move_fen || data.board_fen;
                    board.position(correctMoveFen);
                    
                    // 3. Après 3 secondes supplémentaires, jouer la réponse de l'adversaire
                    setTimeout(() => {
                        // Position finale avec la réponse de l'adversaire
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
                            
                            // Si le bot (blanc) a joué un coup
                            if (data.opponent_move) {
                                updateMoveHistory(
                                    null,
                                    null,
                                    data.opponent_move,
                                    null,
                                    data.opponent_comment
                                );
                            }
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
                    }, 1000); // 3 secondes de délai avant de montrer la réponse de l'adversaire
                }, 500); // 1 seconde de délai avant de jouer le coup correct
            }, 100); // Un court délai initial
        } else {
            // Si le coup est correct, simplement mettre à jour le plateau
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
                
                // Si le bot (blanc) a joué un coup
                if (data.opponent_move) {
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
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showMessage("Une erreur est survenue move.js: " + error.message, false);

        // Annuler immédiatement le coup illégal
        setTimeout(() => board.position(previousPosition), 100);

        // Surligner la case de destination en rouge
        highlightSquareRed(target);

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