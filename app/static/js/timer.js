// Variables du minuteur
var timeRemaining = 60;
var timerInterval = null;

// Initialisation du minuteur
function initTimer() {
    console.log("Initialisation du minuteur");
    timeRemaining = 60;
    updateTimerDisplay();
    startTimer();
}

// Démarrage du minuteur
function startTimer() {
    console.log("Démarrage du minuteur");
    
    // Effacer l'intervalle existant s'il y en a un
    if (timerInterval) {
        clearInterval(timerInterval);
    }
    
    // Définir un nouvel intervalle
    timerInterval = setInterval(function() {
        timeRemaining--;
        updateTimerDisplay();
        
        if (timeRemaining <= 0) {
            stopTimer();
            handleTimeout();
        }
    }, 1000);
}

// Mise à jour de l'affichage du minuteur
function updateTimerDisplay() {
    const timerElement = document.getElementById('timer');
    if (timerElement) {
        const minutes = Math.floor(timeRemaining / 60);
        const seconds = timeRemaining % 60;
        timerElement.textContent = minutes + ':' + (seconds < 10 ? '0' : '') + seconds;
        console.log("Minuteur mis à jour:", timerElement.textContent);
    } else {
        console.error("Élément timer non trouvé!");
    }
}

// Arrêt du minuteur
function stopTimer() {
    console.log("Arrêt du minuteur");
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

// Réinitialisation du minuteur après un coup
function resetTimerAfterMove() {
    console.log("Réinitialisation du minuteur après un coup");
    timeRemaining = 60;
    updateTimerDisplay();
    startTimer();
}

// Gestion du timeout
function handleTimeout() {
    console.log("Timeout déclenché");
    
    // Créer les données à envoyer
    var formData = new FormData();
    formData.append("game_id", gameId);
    formData.append("time_taken", 60);
    
    // Envoyer la requête au serveur
    fetch('/timeout-move', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log("Réponse du serveur pour timeout:", data);
        
        // Mise à jour de l'échiquier avec la nouvelle position
        if (data.board_fen) {
            setPosition(data.board_fen);
        }
        
        // Afficher un message
        if (data.message) {
            showMessage(data.message, false);
        }
        
        // Mettre à jour le score
        if (data.score !== undefined) {
            document.getElementById('score').textContent = data.score;
        }
        
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
        showMessage("Une erreur est survenue lors du traitement du timeout", false);
        resetTimerAfterMove();
    });
}