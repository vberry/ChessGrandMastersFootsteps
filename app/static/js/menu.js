// Script pour basculer entre les modes
document.addEventListener('DOMContentLoaded', function() {
    const livesMode = document.getElementById('lives-mode');
    const timerMode = document.getElementById('timer-mode');
    const livesDifficulty = document.getElementById('lives-difficulty');
    const timerDifficulty = document.getElementById('timer-difficulty');
    const gameModeInput = document.getElementById('game_mode');
    
    // Fonction pour activer un mode
    function activateMode(mode) {
      // Réinitialiser les classes actives
      livesMode.classList.remove('active');
      timerMode.classList.remove('active');
      
      // Cacher tous les éléments de difficulté
      livesDifficulty.style.display = 'none';
      timerDifficulty.style.display = 'none';
      
      // Activer le mode sélectionné
      if (mode === 'lives') {
        livesMode.classList.add('active');
        livesDifficulty.style.display = 'block';
        gameModeInput.value = 'lives';
      } else if (mode === 'timer') {
        timerMode.classList.add('active');
        timerDifficulty.style.display = 'block';
        gameModeInput.value = 'timer';
      }
    }
    
    // Configurer les gestionnaires d'événements
    livesMode.addEventListener('click', function() {
      activateMode('lives');
    });
    
    timerMode.addEventListener('click', function() {
      activateMode('timer');
    });
    
    // Activer le mode par défaut (vies)
    activateMode('lives');
  });