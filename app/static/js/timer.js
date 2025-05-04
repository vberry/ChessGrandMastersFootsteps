// timer.js - Version encore plus robuste
let timerInterval = null;
let timeRemaining = 60;
let timerRunning = false;

// Fonction pour initialiser le timer
function initTimer() {
    // Récupérer les valeurs depuis l'élément DOM directement à chaque fois
    const gameDataElement = document.getElementById('game-data');
    if (!gameDataElement) {
        console.error("Élément game-data non trouvé");
        return;
    }
    
    const timeLimit = parseInt(gameDataElement.getAttribute('data-time-limit'), 10) || 60;
    const moveStartTime = parseInt(gameDataElement.getAttribute('data-move-start-time'), 10) || Math.floor(Date.now() / 1000);
    
    console.log("Initialisation du timer avec:", {timeLimit, moveStartTime});
    
    // Calculer le temps restant
    const currentTime = Math.floor(Date.now() / 1000);
    const elapsedTime = currentTime - moveStartTime;
    timeRemaining = Math.max(0, timeLimit - elapsedTime);
    
    // Mise à jour immédiate de l'affichage
    updateTimerDisplay();
    
    // Démarre le timer avec un délai pour s'assurer que tout est bien initialisé
    setTimeout(() => {
        startTimer();
    }, 100);
}

// Démarrer le timer
function startTimer() {
    // S'assurer qu'aucun timer existant n'est en cours
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    
    console.log("Démarrage du timer, temps restant:", timeRemaining);
    timerRunning = true;
    
    // Créer un nouveau timer
    timerInterval = setInterval(() => {
        timeRemaining--;
        console.log("Décrément du timer:", timeRemaining);
        
        if (timeRemaining <= 0) {
            timeRemaining = 0;
            updateTimerDisplay();
            showTimerExpiredMessage();
        } else {
            updateTimerDisplay();
        }
    }, 1000);
}

// Mettre à jour l'affichage du timer
function updateTimerDisplay() {
    const timerElement = document.getElementById('timer');
    if (!timerElement) {
        console.error("Élément timer non trouvé");
        return;
    }
    
    const minutes = Math.floor(timeRemaining / 60);
    const seconds = timeRemaining % 60;
    timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    
    // Classes pour le style
    timerElement.className = '';
    if (timeRemaining <= 10) {
        timerElement.classList.add('danger');
    } else if (timeRemaining <= 20) {
        timerElement.classList.add('warning');
    }
}

// Afficher un message lorsque le temps est écoulé
function showTimerExpiredMessage() {
    const statusElement = document.getElementById('status');
    if (statusElement) {
        statusElement.textContent = "⏰ Temps écoulé ! (-5 points de pénalité seront appliqués)";
        statusElement.className = 'time-expired';
    }
}

// Effacer le message d'expiration du timer
function clearTimerExpiredMessage() {
    const statusElement = document.getElementById('status');
    if (statusElement && statusElement.classList.contains('time-expired')) {
        statusElement.textContent = "";
        statusElement.className = '';
    }
}

// Arrêter le timer
function stopTimer() {
    console.log("Arrêt du timer");
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
    timerRunning = false;
}

// Réinitialiser le timer
function resetTimer(newStartTime) {
    console.log("Réinitialisation du timer avec:", newStartTime);
    stopTimer();
    
    // Effacer le message d'expiration lors de la réinitialisation du timer
    clearTimerExpiredMessage();
    
    // Récupérer le timeLimit à nouveau
    const gameDataElement = document.getElementById('game-data');
    const timeLimit = gameDataElement ? 
        (parseInt(gameDataElement.getAttribute('data-time-limit'), 10) || 60) : 60;
    
    timeRemaining = timeLimit;
    updateTimerDisplay();
    
    // Démarrer le timer avec un petit délai
    setTimeout(() => {
        startTimer();
    }, 100);
}

// S'assurer que le timer est initialisé quand la page est chargée
document.addEventListener('DOMContentLoaded', function() {
    console.log("DOM chargé, initialisation du timer");
    initTimer();
    
    // Écouter l'événement personnalisé 'moveSubmitted'
    document.addEventListener('moveSubmitted', function(e) {
        console.log("Événement moveSubmitted reçu:", e.detail);
        if (e.detail && e.detail.result && e.detail.result.move_start_time) {
            resetTimer(e.detail.result.move_start_time);
        }
    });
});

// Exposer les fonctions globalement
window.initTimer = initTimer;
window.startTimer = startTimer;
window.stopTimer = stopTimer;
window.resetTimer = resetTimer;
window.clearTimerExpiredMessage = clearTimerExpiredMessage;