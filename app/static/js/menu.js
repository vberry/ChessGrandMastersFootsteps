// Script pour basculer entre les modes
document.addEventListener('DOMContentLoaded', function() {
  const livesMode = document.getElementById('lives-mode');
  const timerMode = document.getElementById('timer-mode');
  const livesDifficulty = document.getElementById('lives-difficulty');
  const timerDifficulty = document.getElementById('timer-difficulty');
  const gameModeInput = document.getElementById('game_mode');
  
  // Vérifier si nous sommes sur la page de menu (avec les éléments de difficulté)
  const isMenuPage = livesDifficulty && timerDifficulty;
  
  // Fonction pour activer un mode
  function activateMode(mode) {
    // Si on n'est pas sur la page du menu, ne pas essayer de manipuler les éléments manquants
    if (!isMenuPage) return;
    
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
  
  // Configurer les gestionnaires d'événements uniquement si les éléments existent
  if (livesMode && timerMode) {
    // Sur la page menu uniquement, prévenir le comportement par défaut pour éviter les rechargements
    if (isMenuPage) {
      livesMode.addEventListener('click', function(e) {
        e.preventDefault();
        activateMode('lives');
        // Mettre à jour l'URL sans recharger la page
        history.replaceState(null, null, '?mode=lives');
      });
      
      timerMode.addEventListener('click', function(e) {
        e.preventDefault();
        activateMode('timer');
        // Mettre à jour l'URL sans recharger la page
        history.replaceState(null, null, '?mode=timer');
      });
    }
  }
  
  // Vérifier les paramètres d'URL pour définir le mode actif
  const urlParams = new URLSearchParams(window.location.search);
  const modeParam = urlParams.get('mode');
  
  // Sur la page du menu, initialiser le mode selon le paramètre d'URL
  if (isMenuPage) {
    // Mode par défaut si aucun paramètre n'est spécifié
    if (modeParam === 'timer') {
      activateMode('timer');
    } else {
      // Par défaut ou explicitement 'lives'
      activateMode('lives');
    }
  } else {
    // Sur la page des règles, mettre en surbrillance le bon élément du menu
    if (livesMode && timerMode) {
      livesMode.classList.remove('active');
      timerMode.classList.remove('active'); 
    }
  }
});