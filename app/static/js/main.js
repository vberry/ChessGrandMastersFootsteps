function submitMove() {
    const moveInput = document.getElementById("move-input");
    const submitBtn = document.getElementById("submit-btn");
    const scoreEl = document.getElementById("score");
    const scorePctEl = document.getElementById("score-percentage");
    const attemptsLeftEl = document.getElementById("attempts-left");
    const statusEl = document.getElementById("status");
    const lastMoveEl = document.getElementById("last-move");

    const move = moveInput.value.trim();
    if (!move) {
        showMessage("Veuillez entrer un coup", false);
        return;
    }

    submitBtn.disabled = true;

    const formData = new FormData();
    formData.append("game_id", gameId);
    formData.append("move", move);

    fetch('/submit-move', { method: 'POST', body: formData })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            showMessage(data.error, false);
            if (data.is_valid_format === false) {
                moveInput.value = '';
            }
            return;
        }

        // Coups alternatifs
        if (Array.isArray(data.previous_position_best_moves) && data.previous_position_best_moves.length) {
            displayAlternativeMoves(data.previous_position_best_moves, move);
        }

        // Score
        scoreEl.textContent = data.score;

        // % seulement si le backend l’a envoyé
        if (data.score_percentage !== undefined) {
            scorePctEl.textContent = data.score_percentage + "%";
        }

        // Essais restants
        if (data.attempts_left !== undefined) {
            attemptsLeftEl.textContent = data.attempts_left;
        }

        // Échiquier
        board.position(data.board_fen);

        // Historique
        updateMoveHistory(
            data.submitted_move,
            data.correct_move,
            data.opponent_move,
            data.comment,
            data.opponent_comment
        );

        // Message de feedback
        let msg = data.is_correct
            ? "✅ Bravo ! Coup correct."
            : `❌ Incorrect. Le bon coup était : ${data.correct_move}`;

        if (!data.is_correct && data.hint) {
            msg += `\n💡 ${data.hint}`;
        }
        showMessage(msg, data.is_correct);

        // Dernier coup adverse (avec délai pour l’animation)
        if (data.last_opponent_move) {
            setTimeout(() => {
                if (lastMoveEl) {
                    lastMoveEl.textContent = "Dernier coup joué : " + data.last_opponent_move;
                }
            }, 500);
        }

        // Remise à zéro de l’input
        moveInput.value = '';

        // Fin de partie
        if (data.game_over) {
            statusEl.textContent = "🎉 Partie terminée !";
            submitBtn.disabled = true;
            moveInput.disabled = true;
        }
    })
    .catch(err => {
        console.error('Erreur fetch submit-move :', err);
        showMessage("Une erreur est survenue (réseau ou serveur).", false);
    })
    .finally(() => {
        // Réactive le bouton si la partie n’est pas finie
        if (!statusEl.textContent.includes("terminée")) {
            submitBtn.disabled = false;
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initializeBoard();
    initializeHistory();
    document.getElementById("submit-btn")
        .addEventListener("click", e => {
            e.preventDefault();
            submitMove();
        });
});
