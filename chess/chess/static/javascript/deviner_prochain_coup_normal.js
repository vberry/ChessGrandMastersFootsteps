document.addEventListener("DOMContentLoaded", function() {
    var board = null;
    var game = new Chess(boardFen);
    var $status = $('#status');
    var $message = $('#message');
    var $score = $('#score');
    var $attempts = $('#attempts');
    var $moveHistory = $('#move-history .history-content');
    var moveNumber = 1;
    
    function onDragStart(source, piece, position, orientation) {
        // N'autoriser le déplacement que des pièces de la couleur du joueur
        if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
            (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
            return false;
        }
        
        // Autoriser seulement les pièces de la couleur du joueur
        if ((userSide === 'white' && piece.search(/^b/) !== -1) ||
            (userSide === 'black' && piece.search(/^w/) !== -1)) {
            return false;
        }
    }

    function onDrop(source, target) {
        // Vérifier si le déplacement est valide dans le jeu local
        var move = game.move({
            from: source,
            to: target,
            promotion: 'q' // Promouvoir toujours en Dame
        });

        // Annuler le déplacement (car on ne veut pas modifier l'état du jeu localement)
        if (move) game.undo();
        
        // Si le déplacement est valide, on le soumet au serveur
        if (move !== null) {
            var uciMove = source + target;
            
            // Stocker temporairement le FEN actuel pour pouvoir revenir à cette position si nécessaire
            var currentFen = game.fen();
            
            $.ajax({
                url: '/submit-move',
                method: 'POST',
                data: {
                    'game_id': gameId,
                    'move': uciMove
                },
                // Mise à jour de la partie de gestion des réponses du serveur dans onDrop et submitMove
// Dans la fonction onDrop, modifiez la partie success comme suit:

                success: function(response) {
                    if (response.error) {
                        displayMessage(response.error, true);
                        board.position(currentFen); // Remettre l'échiquier à sa position d'origine
                        return;
                    }
                    
                    $attempts.text(response.remaining_attempts);
                    
                    if (response.is_correct) {
                        $score.text(response.score);
                        displayMessage('Correct ! +10 points');
                        
                        // Convertir le coup UCI en notation SAN pour l'historique
                        var tempGame = new Chess(currentFen);
                        var tempMove = tempGame.move({
                            from: source,
                            to: target,
                            promotion: 'q'
                        });
                        var sanMove = tempMove ? tempMove.san : uciMove;
                        
                        addMoveToHistory(sanMove, sanMove, true);
                        
                        // Mettre à jour l'échiquier avec la nouvelle position du serveur
                        if (response.board_fen) {
                            updateBoard(response.board_fen);
                        }
                    } else {
                        if (response.remaining_attempts === 0) {
                            displayMessage(`Incorrect. Le coup correct était: ${response.correct_move}`, true);
                            
                            // Convertir le coup UCI en notation SAN pour l'historique
                            var tempGame = new Chess(currentFen);
                            var tempMove = tempGame.move({
                                from: source,
                                to: target,
                                promotion: 'q'
                            });
                            var sanMove = tempMove ? tempMove.san : uciMove;
                            
                            addMoveToHistory(sanMove, response.correct_move, false);
                            
                            // Mettre à jour l'échiquier avec la nouvelle position du serveur
                            if (response.board_fen) {
                                updateBoard(response.board_fen);
                            }
                        } else {
                            displayMessage(`Incorrect. Il vous reste ${response.remaining_attempts} essai(s).`, true);
                            // Remettre l'échiquier à sa position d'origine
                            board.position(currentFen);
                        }
                    }
                },
                error: function() {
                    displayMessage("Erreur lors de la soumission du coup", true);
                    board.position(currentFen); // Remettre l'échiquier à sa position d'origine en cas d'erreur
                }
            });
            
            return; // Permettre le déplacement visuellement pour l'instant
        }
        
        // Si le coup est invalide selon chess.js, annuler immédiatement
        return 'snapback';
    }

    function updateBoard(fen) {
        board.position(fen);
        game = new Chess(fen);
    }

    function displayMessage(message, isError = false) {
        $message.text(message);
        $message.removeClass('error success');
        if (isError) {
            $message.addClass('error');
        } else {
            $message.addClass('success');
        }
        $message.show();
        setTimeout(function() {
            $message.fadeOut();
        }, 5000);
    }

    function addMoveToHistory(playerMove, correctMove, isCorrect) {
        var moveItem = $('<div class="move-item"></div>');
        moveItem.append(`<span class="move-number">${moveNumber}.</span>`);
        
        if (isCorrect) {
            moveItem.append(`<span class="player-move correct">${playerMove}</span>`);
        } else {
            moveItem.append(`<span class="player-move incorrect">${playerMove}</span>`);
            moveItem.append(`<span class="correct-move">(${correctMove})</span>`);
        }
        
        $moveHistory.append(moveItem);
        moveNumber++;
        
        // Scroll to the bottom of the history
        $moveHistory.scrollTop($moveHistory[0].scrollHeight);
    }

    function submitMove(move) {
        // Stocker la position actuelle
        var currentFen = game.fen();
        
        $.ajax({
            url: '/submit-move',
            method: 'POST',
            data: {
                'game_id': gameId,
                'move': move
            },
            success: function(response) {
                if (response.error) {
                    displayMessage(response.error, true);
                    return;
                }
                
                $attempts.text(response.remaining_attempts);
                
                if (response.is_correct) {
                    $score.text(response.score);
                    displayMessage('Correct ! +10 points');
                    
                    // Convertir le coup UCI en notation SAN pour l'historique
                    var tempGame = new Chess(currentFen);
                    var tempMove = tempGame.move({
                        from: move.substring(0, 2),
                        to: move.substring(2, 4),
                        promotion: 'q'
                    });
                    var sanMove = tempMove ? tempMove.san : move;
                    
                    addMoveToHistory(sanMove, sanMove, true);
                    
                    // Mettre à jour l'échiquier
                    if (response.board_fen) {
                        updateBoard(response.board_fen);
                    }
                } else {
                    if (response.remaining_attempts === 0) {
                        displayMessage(`Incorrect. Le coup correct était: ${response.correct_move}`, true);
                        
                        // Convertir le coup UCI en notation SAN pour l'historique
                        var tempGame = new Chess(currentFen);
                        var tempMove = tempGame.move({
                            from: move.substring(0, 2),
                            to: move.substring(2, 4),
                            promotion: 'q'
                        });
                        var sanMove = tempMove ? tempMove.san : move;
                        
                        addMoveToHistory(sanMove, response.correct_move, false);
                        
                        // Mettre à jour l'échiquier
                        if (response.board_fen) {
                            updateBoard(response.board_fen);
                        }
                    } else {
                        displayMessage(`Incorrect. Il vous reste ${response.remaining_attempts} essai(s).`, true);
                        // Remettre l'échiquier à sa position d'origine
                        board.position(currentFen);
                    }
                }
            },
            error: function() {
                displayMessage("Erreur lors de la soumission du coup", true);
                // Remettre l'échiquier à sa position d'origine en cas d'erreur
                board.position(currentFen);
            }
        });
    }

    // Initialisation du plateau
    var config = {
        position: boardFen,
        draggable: true,
        orientation: userSide === 'white' ? 'white' : 'black',
        onDragStart: onDragStart,
        onDrop: onDrop,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
    };
    board = Chessboard('board', config);

   
});