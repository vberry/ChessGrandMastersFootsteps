// Script pour basculer entre les modes
document.addEventListener('DOMContentLoaded', function() {
  // Éléments du mode de jeu
  const livesMode = document.getElementById('lives-mode');
  const timerMode = document.getElementById('timer-mode');
  const livesDifficulty = document.getElementById('lives-difficulty');
  const timerDifficulty = document.getElementById('timer-difficulty');
  const gameModeInput = document.getElementById('game_mode');
  
  // Éléments du mode d'affichage
  const display2D = document.getElementById('display-2D');
  const display3D = document.getElementById('display-3D');
  const displayModeInput = document.getElementById('display_mode');
  
  // Vérifier si nous sommes sur la page de menu (avec les éléments de difficulté)
  const isMenuPage = livesDifficulty && timerDifficulty;
  
  // Fonction pour activer un mode de jeu
  function activateGameMode(mode) {
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
  
  // Fonction pour activer un mode d'affichage
  function activateDisplayMode(mode) {
    // Si on n'est pas sur la page du menu, ne pas essayer de manipuler les éléments manquants
    if (!isMenuPage) return;
    
    // Réinitialiser les classes actives
    display2D.classList.remove('active');
    display3D.classList.remove('active');
    
    // Activer le mode d'affichage sélectionné
    if (mode === '2D') {
      display2D.classList.add('active');
      displayModeInput.value = '2D';
    } else if (mode === '3D') {
      display3D.classList.add('active');
      displayModeInput.value = '3D';
    }
  }
  
  // Configurer les gestionnaires d'événements uniquement si les éléments existent
  if (isMenuPage) {
    // Gestionnaires pour les modes de jeu
    if (livesMode && timerMode) {
      livesMode.addEventListener('click', function(e) {
        e.preventDefault();
        activateGameMode('lives');
        // Conserver le mode d'affichage actuel en récupérant sa valeur
        const currentDisplay = displayModeInput ? displayModeInput.value : '2D';
        // Mettre à jour l'URL sans recharger la page
        history.replaceState(null, null, `?mode=lives&display=${currentDisplay}`);
      });
      
      timerMode.addEventListener('click', function(e) {
        e.preventDefault();
        activateGameMode('timer');
        // Conserver le mode d'affichage actuel
        const currentDisplay = displayModeInput ? displayModeInput.value : '2D';
        // Mettre à jour l'URL sans recharger la page
        history.replaceState(null, null, `?mode=timer&display=${currentDisplay}`);
      });
    }
    
    // Gestionnaires pour les modes d'affichage
    if (display2D && display3D) {
      display2D.addEventListener('click', function(e) {
        e.preventDefault();
        activateDisplayMode('2D');
        // Conserver le mode de jeu actuel
        const currentMode = gameModeInput ? gameModeInput.value : 'lives';
        // Mettre à jour l'URL sans recharger la page
        history.replaceState(null, null, `?mode=${currentMode}&display=2D`);
      });
      
      display3D.addEventListener('click', function(e) {
        e.preventDefault();
        activateDisplayMode('3D');
        // Conserver le mode de jeu actuel
        const currentMode = gameModeInput ? gameModeInput.value : 'lives';
        // Mettre à jour l'URL sans recharger la page
        history.replaceState(null, null, `?mode=${currentMode}&display=3D`);
      });
    }
  }
  
  // Vérifier les paramètres d'URL pour définir les modes actifs
  const urlParams = new URLSearchParams(window.location.search);
  const modeParam = urlParams.get('mode');
  const displayParam = urlParams.get('display');
  
  // Sur la page du menu, initialiser les modes selon les paramètres d'URL
  if (isMenuPage) {
    // Mode de jeu par défaut si aucun paramètre n'est spécifié
    if (modeParam === 'timer') {
      activateGameMode('timer');
    } else {
      // Par défaut ou explicitement 'lives'
      activateGameMode('lives');
    }
    
    // Mode d'affichage par défaut si aucun paramètre n'est spécifié
    if (displayParam === '3D') {
      activateDisplayMode('3D');
    } else {
      // Par défaut ou explicitement '2D'
      activateDisplayMode('2D');
    }
  } else {
    // Sur la page des règles, réinitialiser les classes actives
    if (livesMode && timerMode) {
      livesMode.classList.remove('active');
      timerMode.classList.remove('active');
    }
    if (display2D && display3D) {
      display2D.classList.remove('active');
      display3D.classList.remove('active');
    }
  }
});