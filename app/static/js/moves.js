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
                    lastMoveRow.cells[2].innerHTML += `<br><small>(Coup du maître: ${correctMove})</small>`;
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
            whiteMoveCell.innerHTML += `<br><small>(Coup du maître: ${correctMove})</small>`;
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
            blackMoveCell.innerHTML += `<br><small>(Coup du maître: ${correctMove})</small>`;
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

// Fonctions pour verrouiller/déverrouiller le plateau
let boardLocked = false;

function lockBoard() {
    boardLocked = true;
    
    // Ajout visuel pour indiquer que le plateau est verrouillé
    const boardElement = document.getElementById('board');
    if (boardElement) {
        // Créer un overlay s'il n'existe pas déjà
        let overlay = document.getElementById('board-lock-overlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'board-lock-overlay';
            overlay.style.position = 'absolute';
            overlay.style.top = '0';
            overlay.style.left = '0';
            overlay.style.width = '100%';
            overlay.style.height = '100%';
            overlay.style.backgroundColor = 'rgba(0, 0, 0, 0.1)';
            overlay.style.display = 'flex';
            overlay.style.justifyContent = 'center';
            overlay.style.alignItems = 'center';
            overlay.style.zIndex = '1000';
            
            // Ajout d'un indicateur de chargement
            const spinner = document.createElement('div');
            spinner.className = 'spinner';
            spinner.style.border = '4px solid rgba(0, 0, 0, 0.1)';
            spinner.style.borderLeft = '4px solid #8a2be2';
            spinner.style.borderRadius = '50%';
            spinner.style.width = '30px';
            spinner.style.height = '30px';
            spinner.style.animation = 'spin 1s linear infinite';
            overlay.appendChild(spinner);
            
            // Ajouter l'animation CSS si elle n'existe pas déjà
            if (!document.getElementById('spinner-animation')) {
                const style = document.createElement('style');
                style.id = 'spinner-animation';
                style.textContent = `
                    @keyframes spin {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
            
            boardElement.style.position = 'relative';
            boardElement.appendChild(overlay);
        } else {
            overlay.style.display = 'flex';
        }
    }
    
    console.log('Plateau verrouillé');
}

function unlockBoard() {
    boardLocked = false;
    
    // Retirer l'overlay visuel
    const overlay = document.getElementById('board-lock-overlay');
    if (overlay) {
        overlay.style.display = 'none';
    }
    
    console.log('Plateau déverrouillé');
}

// Modifier la fonction handleMove pour inclure le verrouillage
function handleMove(source, target) {
    // Si le plateau est déjà verrouillé, ignorer la demande de mouvement
    if (boardLocked) {
        console.log("Le plateau est verrouillé, mouvement ignoré");
        return false;
    }
    
    // Verrouiller le plateau immédiatement
    lockBoard();
    
    let moveToSubmit = source + target;
    const previousPosition = board.fen();

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
            
            // Déverrouiller le plateau
            unlockBoard();
            return;
        }

        // Afficher les coups alternatifs pour la position précédente
        if (data.previous_position_best_moves && data.previous_position_best_moves.length > 0) {
            displayAlternativeMoves(data.previous_position_best_moves, moveToSubmit);
        }

        // Mise à jour du score
        if (data.score !== undefined) {
            document.getElementById("score").textContent = data.score;
            if (data.score_percentage !== undefined) {
                document.getElementById("score-percentage").textContent = data.score_percentage + "%";
            }
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
                
                // Effet de tremblement sur la pièce
                if (typeof animateShakePiece === 'function') {
                    animateShakePiece(source);
                }
                
                // 2. Après 1 seconde, jouer le coup correct (sans la réponse de l'adversaire)
                setTimeout(() => {
                    // On a besoin d'une position intermédiaire avec uniquement le coup correct
                    const correctMoveFen = data.correct_move_fen || data.board_fen;
                    board.position(correctMoveFen);
                    
                    // 3. Après 3 secondes supplémentaires, jouer la réponse de l'adversaire
                    setTimeout(() => {
                        // Position finale avec la réponse de l'adversaire
                        board.position(data.board_fen);
                        
                        // Mettre à jour l'historique des coups
                        if (userSide === 'black') {
                            updateMoveHistory(
                                data.submitted_move,
                                data.correct_move,
                                null,
                                data.comment,
                                null,
                                data.move_evaluation
                            );
                            
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
                                window.stopTimer();
                            }
                        } else {
                            if (data.move_start_time && typeof window.resetTimer === 'function') {
                                window.resetTimer(data.move_start_time);
                            }
                            
                            const event = new CustomEvent('moveSubmitted', { 
                                detail: { result: data } 
                            });
                            document.dispatchEvent(event);
                        }
                        
                        // Déverrouiller le plateau seulement à la fin de toutes les animations
                        unlockBoard();
                    }, 1000);
                }, 500);
            }, 100);
        } else {
            // Si le coup est correct, simplement mettre à jour le plateau
            board.position(data.board_fen);
            
            // Mettre à jour l'historique des coups
            if (userSide === 'black') {
                updateMoveHistory(
                    data.submitted_move,
                    data.correct_move,
                    null,
                    data.comment,
                    null,
                    data.move_evaluation
                );
                
                if (data.opponent_move) {
                    setTimeout(() => {
                        updateMoveHistory(
                            null,
                            null,
                            data.opponent_move,
                            null,
                            data.opponent_comment
                        );
                        // Déverrouiller le plateau après l'affichage de la réponse de l'adversaire
                        unlockBoard();
                    }, 500);
                } else {
                    // Déverrouiller le plateau si pas de coup de l'adversaire
                    unlockBoard();
                }
            } else {
                updateMoveHistory(
                    data.submitted_move,
                    data.correct_move,
                    data.opponent_move,
                    data.comment,
                    data.opponent_comment,
                    data.move_evaluation
                );
                
                // Déverrouiller le plateau après traitement complet
                unlockBoard();
            }
            
            // Vérifier si la partie est terminée
            if (data.game_over) {
                document.getElementById("status").textContent = "🎉 Partie terminée !";
                if (typeof window.stopTimer === 'function') {
                    window.stopTimer();
                }
            } else {
                if (data.move_start_time && typeof window.resetTimer === 'function') {
                    window.resetTimer(data.move_start_time);
                }
                
                const event = new CustomEvent('moveSubmitted', { 
                    detail: { result: data } 
                });
                document.dispatchEvent(event);
            }
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showMessage("Une erreur est survenue: " + error.message, false);

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
        
        // Déverrouiller le plateau en cas d'erreur
        unlockBoard();
    });

    return false;
}