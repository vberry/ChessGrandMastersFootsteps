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

document.addEventListener('DOMContentLoaded', function() {
    initializeBoard();
});
