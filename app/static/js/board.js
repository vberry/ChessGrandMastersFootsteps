function initializeBoard() {
  console.log('Initialisation du plateau...');
  
  // Créer l'échiquier avec draggable désactivé
  board = Chessboard('board', {
    position: boardFen,
    pieceTheme: function(piece) {
      const color = piece.charAt(0);
      const type = piece.charAt(1).toLowerCase();
      return 'https://images.chesscomfiles.com/chess-themes/pieces/3d_staunton/150/' + color + type + '.png';
    },
    showNotation: true,
    draggable: false, // Désactiver le drag natif
    orientation: userSide
  });
  
  // Styles CSS pour les pièces
  const style = document.createElement('style');
  style.innerHTML = `
    /* Styles pour les pièces statiques */
    .piece-417db {
      position: absolute !important;
      filter: drop-shadow(1px 3px 2px rgba(0, 0, 0, 0.3)) !important;
      z-index: 5 !important;
      cursor: grab !important;
      /* Désactiver toutes transformations potentielles */
      transform: none !important;
      transform-origin: center center !important;
      transition: opacity 0.1s ease !important;
      will-change: opacity !important;
    }
    
    /* Permettre le débordement des cases */
    .square-55d63 {
      overflow: visible !important;
      position: relative !important;
    }
    
    /* Style pour le conteneur de pièce en cours de déplacement - ne pas modifier sa taille */
    #dragging-piece-container {
      position: fixed !important;
      z-index: 9999 !important;
      pointer-events: none !important;
      width: auto !important;
      height: auto !important;
      transform: none !important;
    }
    
    /* Style pour l'image de la pièce en cours de déplacement - taille fixe */
    #dragging-piece-image {
      width: 80px !important;
      height: auto !important;
      transform: none !important;
      transform-origin: center center !important;
      filter: drop-shadow(2px 4px 3px rgba(0, 0, 0, 0.4)) !important;
      opacity: 0.95 !important;
      transition: none !important;
      animation: none !important;
    }
    
    /* Highlight des cases */
    .highlight-source {
      box-shadow: inset 0 0 3px 3px yellow !important;
    }
    .highlight-target {
      box-shadow: inset 0 0 3px 3px limegreen !important;
    }
    
    /* Style pour la pièce en cours d'animation */
    .animating-piece {
    position: fixed !important;
    z-index: 9000 !important;
    pointer-events: none !important;
    will-change: left, top !important;
  }
  `;
  document.head.appendChild(style);
  
  // Variables pour le drag & drop personnalisé
  let isDragging = false;
  let draggedPiece = null;
  let sourceSquare = null;
  let boardPosition = null;
  let squareSize = 0;
  
  // Créer un conteneur fixe pour la pièce en cours de déplacement
  let dragContainer = document.createElement('div');
  dragContainer.id = 'dragging-piece-container';
  
  let dragImage = document.createElement('img');
  dragImage.id = 'dragging-piece-image';
  
  dragContainer.appendChild(dragImage);
  // Ne pas ajouter le conteneur au DOM pour l'instant
  
  // Obtenir la position du plateau et la taille des cases
  function updateBoardMetrics() {
    const boardElement = document.getElementById('board');
    if (boardElement) {
      boardPosition = boardElement.getBoundingClientRect();
      squareSize = boardPosition.width / 8;
      return true;
    }
    return false;
  }
  
  // Appliquer les styles aux pièces statiques
  function applyStaticPieceStyles() {
    const pieces = document.querySelectorAll('.piece-417db');
    pieces.forEach(piece => {
      if (piece.src && piece.src.includes('chess-themes/pieces')) {
        // Identifier si c'est un pion ou une autre pièce
        const isPawn = piece.src.includes('/wp.png') || piece.src.includes('/bp.png');
        if (isPawn) {
          // Styles pour les pions
          piece.style.width = '100%';
          piece.style.height = '100%';
          piece.style.top = '-7.5%';
          piece.style.transform = 'none';
        } else {
          // Styles pour les pièces majeures
          piece.style.width = '100%';
          piece.style.height = '122%';
          piece.style.top = '-15%';
          piece.style.transform = 'none';
        }
      }
    });
  }
  
  // Trouver la case sous le pointeur
  function getSquareAtPosition(x, y) {
    if (!boardPosition) return null;
    
    const boardX = x - boardPosition.left;
    const boardY = y - boardPosition.top;
    
    // Vérifier si le pointeur est dans les limites du plateau
    if (boardX < 0 || boardX >= boardPosition.width || boardY < 0 || boardY >= boardPosition.height) {
      return null;
    }
    
    // Calculer la colonne et la ligne
    let col = Math.floor(boardX / squareSize);
    let row = Math.floor(boardY / squareSize);
    
    // Inverser si nécessaire en fonction de l'orientation
    if (userSide === 'black') {
      col = 7 - col;
      row = 7 - row;
    }
    
    // Convertir en notation d'échecs (a1, b2, etc.)
    const fileChar = String.fromCharCode('a'.charCodeAt(0) + col);
    const rankChar = 8 - row;
    
    return fileChar + rankChar;
  }
  
  // Gérer le début du drag
  function handleMouseDown(e) {
    if (isDragging) return;
    
    const target = e.target;
    // Vérifier si c'est une pièce d'échecs
    if (target.classList.contains('piece-417db')) {
      // Mettre à jour les métriques du plateau
      if (!updateBoardMetrics()) return;
      
      // Trouver la case source
      const square = target.closest('.square-55d63');
      if (square) {
        sourceSquare = square.dataset.square;
        square.classList.add('highlight-source');
        
        // Mémoriser la pièce d'origine
        draggedPiece = target;
        draggedPiece.style.opacity = '0.3';
        
        // Déterminer si c'est un pion ou une pièce majeure
        const isPawn = target.src.includes('/wp.png') || target.src.includes('/bp.png');
        
        // Configurer l'image de drag (taille fixe mais aspect visuel cohérent)
        dragImage.src = target.src;
        dragImage.alt = target.alt || 'Chess Piece';
        
        // Positionner le conteneur de drag
        const offsetX = 40; // Moitié de la largeur fixe
        const offsetY = isPawn ? 40 : 48; // Ajuster selon le type de pièce
        
        dragContainer.style.left = (e.clientX - offsetX) + 'px';
        dragContainer.style.top = (e.clientY - offsetY) + 'px';
        
        // Ajouter au DOM
        document.body.appendChild(dragContainer);
        
        isDragging = true;
        
        // Empêcher d'autres événements
        e.preventDefault();
      }
    }
  }
  
  // Gérer le déplacement de la souris pendant le drag
  function handleMouseMove(e) {
    if (!isDragging) return;
    
    // Déterminer si c'est un pion ou une pièce majeure pour l'offset
    const isPawn = dragImage.src.includes('/wp.png') || dragImage.src.includes('/bp.png');
    const offsetX = 40; // Moitié de la largeur fixe
    const offsetY = isPawn ? 40 : 48; // Ajuster selon le type de pièce
    
    // Mettre à jour la position du conteneur de drag
    dragContainer.style.left = (e.clientX - offsetX) + 'px';
    dragContainer.style.top = (e.clientY - offsetY) + 'px';
    
    // Trouver et mettre en surbrillance la case cible potentielle
    const targetSquare = getSquareAtPosition(e.clientX, e.clientY);
    
    // Enlever la surbrillance précédente
    const highlights = document.querySelectorAll('.highlight-target');
    highlights.forEach(el => el.classList.remove('highlight-target'));
    
    // Ajouter la surbrillance à la nouvelle case cible
    if (targetSquare) {
      const targetElement = document.querySelector(`.square-55d63[data-square="${targetSquare}"]`);
      if (targetElement) {
        targetElement.classList.add('highlight-target');
      }
    }
  }
  
  // Gérer la fin du drag
  function handleMouseUp(e) {
    if (!isDragging) return;
    
    // Restaurer l'opacité de la pièce originale
    if (draggedPiece) {
      draggedPiece.style.opacity = '1';
    }
    
    // Retirer le conteneur de drag du DOM
    if (dragContainer.parentNode) {
      dragContainer.parentNode.removeChild(dragContainer);
    }
    
    // Trouver la case cible
    const targetSquare = getSquareAtPosition(e.clientX, e.clientY);
    
    // Enlever toutes les surbrillances
    const highlights = document.querySelectorAll('.highlight-source, .highlight-target');
    highlights.forEach(el => el.classList.remove('highlight-source', 'highlight-target'));
    
    isDragging = false;
    
    // Si on a une case source et une case cible valides
    if (sourceSquare && targetSquare && sourceSquare !== targetSquare) {
      // Appeler la fonction de gestion de mouvement
      const moveResult = handleMove(sourceSquare, targetSquare);
      
      // Le plateau sera mis à jour via board.position()
      
      // Réappliquer immédiatement les styles aux pièces
      setTimeout(applyStaticPieceStyles, 10);
      setTimeout(applyStaticPieceStyles, 200);
    }
    
    // Réinitialiser les variables
    sourceSquare = null;
    draggedPiece = null;
  }
  
  // Ajouter les écouteurs d'événements pour notre drag & drop personnalisé
  const boardElement = document.getElementById('board');
  if (boardElement) {
    boardElement.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
  }
  
  // Observer les changements dans le DOM pour réappliquer les styles
  const observer = new MutationObserver(function(mutations) {
    applyStaticPieceStyles();
  });
  
  if (boardElement) {
    observer.observe(boardElement, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['style', 'class']
    });
  }
  
  // Appliquer les styles initiaux
  setTimeout(applyStaticPieceStyles, 300);
  
  // Réajuster lors du redimensionnement
  window.addEventListener('resize', function() {
    updateBoardMetrics();
    board.resize();
    setTimeout(applyStaticPieceStyles, 100);
  });
  
  // Surcharge de la fonction setPosition de chessboard.js
  if (board && board.position) {
    const originalPosition = board.position;
    board.position = function() {
      const result = originalPosition.apply(this, arguments);
      setTimeout(applyStaticPieceStyles, 10);
      return result;
    };
  }

  // Ajouter cette fonction pour gérer l'animation des mouvements
  function animateMove(fromSquare, toSquare, piece) {
    // Récupérer les éléments DOM
    const fromElement = document.querySelector(`.square-55d63[data-square="${fromSquare}"]`);
    const toElement = document.querySelector(`.square-55d63[data-square="${toSquare}"]`);
    
    if (!fromElement || !toElement) return false;
    
    // Créer une copie de la pièce pour l'animation
    const pieceCopy = document.createElement('img');
    pieceCopy.src = piece.src;
    pieceCopy.alt = 'Moving piece';
    pieceCopy.classList.add('animating-piece');
    
    // Appliquer un style à la pièce animée
    pieceCopy.style.position = 'absolute';
    pieceCopy.style.zIndex = '9000';
    pieceCopy.style.width = `${squareSize * 0.8}px`; // Taille réduite pour éviter le zoom excessif
    pieceCopy.style.height = 'auto';
    pieceCopy.style.filter = 'drop-shadow(1px 2px 2px rgba(0, 0, 0, 0.3))';
    pieceCopy.style.pointerEvents = 'none';
    
    // Calculer les positions de départ et d'arrivée
    const fromRect = fromElement.getBoundingClientRect();
    const toRect = toElement.getBoundingClientRect();
    
    // Positionner initialement à la position de départ
    pieceCopy.style.left = `${fromRect.left + window.scrollX}px`;
    pieceCopy.style.top = `${fromRect.top + window.scrollY}px`;
    
    // Ajouter au body pour l'animation
    document.body.appendChild(pieceCopy);
    
    // Cacher la pièce d'origine pendant l'animation
    if (piece) piece.style.opacity = '0';
    
    // Définir la transition
    pieceCopy.style.transition = 'left 0.2s ease, top 0.2s ease';
    
    // Déclencher l'animation après un court délai
    setTimeout(() => {
        pieceCopy.style.left = `${toRect.left + window.scrollX}px`;
        pieceCopy.style.top = `${toRect.top + window.scrollY}px`;
    }, 10);
    
    // Nettoyer après l'animation
    setTimeout(() => {
        if (pieceCopy.parentNode) {
            pieceCopy.parentNode.removeChild(pieceCopy);
        }
        
        // Restaurer l'opacité de la pièce d'origine si elle existe encore
        if (piece && piece.parentNode) {
            piece.style.opacity = '1';
        }
        
        // Mettre à jour le plateau avec la position FEN la plus récente
        if (boardFen) {
            board.position(boardFen, false);
        }
        
        // Réappliquer les styles des pièces
        setTimeout(applyStaticPieceStyles, 50);
    }, 220);
    
    return true;
}


}
