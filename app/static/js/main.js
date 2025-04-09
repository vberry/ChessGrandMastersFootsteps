function submitMove(move) {
    console.log("Soumission du coup:", move);
    
    // Arrêter le minuteur lorsqu'un coup est soumis
    stopTimer();
    
    // Capturer le temps pris pour jouer le coup
    const timeTaken = 60 - timeRemaining;
    console.log("Temps pris:", timeTaken);

    var formData = new FormData();
    formData.append("game_id", gameId);
    formData.append("move", move);
    formData.append("time_taken", timeTaken);

    fetch('/submit-move', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Réponse du serveur:", data);
        
        if (data.error) {
            showMessage(data.error, false);
            // Redémarrer le minuteur si le coup est invalide
            resetTimerAfterMove();
            return;
        }
        
        // Mettre à jour l'échiquier avec la nouvelle position
        if (data.board_fen) {
            setPosition(data.board_fen);
        }
        
        // Mettre à jour le score
        if (data.score !== undefined) {
            document.getElementById('score').textContent = data.score;
        }
        
        // Afficher un message selon que le coup est correct ou non
        let message = data.is_correct ? 
            "✅ Bravo ! Coup correct." : 
            `❌ Incorrect. Le bon coup était : ${data.correct_move}`;
            
        if (data.time_bonus !== undefined) {
            const timeMsg = data.time_bonus > 0 ? 
                `\nBonus de temps: +${data.time_bonus} points` : 
                data.time_bonus < 0 ? 
                `\nPénalité de temps: ${data.time_bonus} points` : 
                `\nPas de bonus/malus de temps`;
            message += timeMsg;
        }
        
        showMessage(message, data.is_correct);
        
        // Vérifier si le jeu est terminé
        if (data.game_over) {
            document.getElementById('status').textContent = "🎉 Partie terminée !";
        } else {
            // Redémarrer le minuteur pour le prochain coup
            resetTimerAfterMove();
        }
    })
    .catch(error => {
        console.error('Erreur:', error);
        showMessage("Une erreur est survenue", false);
        // Redémarrer le minuteur en cas d'erreur
        resetTimerAfterMove();
    });
}

// Ajout de la fonction handleMoveResponse pour le coup automatiquement soumis en cas de timeout
function handleMoveResponse(response) {
    if (response.error) {
        showMessage(response.error, false);
        return;
    }
    
    // Mettre à jour le score
    document.getElementById("score").textContent = response.score;
    
    // Mettre à jour l'historique des coups
    updateMoveHistory(
        response.submitted_move,
        response.correct_move,
        response.opponent_move,
        response.comment,
        response.opponent_comment
    );
    
    // Mettre à jour la position de l'échiquier
    board.position(response.board_fen);
    
    // Afficher un message sur le timeout
    let message = "⏰ Temps écoulé! Le coup correct était: " + response.correct_move;
    if (response.timeout_penalty) {
        message += `\nPénalité: ${response.timeout_penalty} points`;
    }
    showMessage(message, false);
    
    // Si le jeu n'est pas terminé, redémarrer le minuteur
    if (!response.game_over) {
        resetTimerAfterMove();
    } else {
        document.getElementById("status").textContent = "🎉 Partie terminée !";
        document.getElementById("submit-btn").disabled = true;
        document.getElementById("move-input").disabled = true;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeBoard(boardFen, userSide);
});