function initializeBoard() {
    console.log('Initialisation du plateau...');
    
    // Créer l'échiquier
    board = Chessboard('board', {
      position: boardFen,
      pieceTheme: function(piece) {
        const color = piece.charAt(0);
        const type = piece.charAt(1).toLowerCase();
        return 'https://images.chesscomfiles.com/chess-themes/pieces/3d_staunton/150/' + color + type + '.png';
      },
      showNotation: true,
      draggable: true,
      orientation: userSide,
      onDrop: handleMove,
      onSnapEnd: function() {
        setTimeout(applyStaticPieceStyles, 100);
      }
    });
    
    // Ajouter les styles CSS qui corrigent le problème
    const style = document.createElement('style');
    style.innerHTML = `
      /* Empêcher le zoom des pièces pendant le drag */
      body > img.ui-draggable-dragging {
        width: 60px !important; /* Taille fixe - ajuster selon vos besoins */
        height: auto !important;
        cursor: grabbing !important;
      }
      
      /* Styles pour les pièces statiques */
      .piece-417db {
        position: absolute !important;
        filter: drop-shadow(1px 3px 2px rgba(0, 0, 0, 0.3)) !important;
        z-index: 5 !important;
      }
      
      /* Permettre le débordement des cases */
      .square-55d63 {
        overflow: visible !important;
        position: relative !important;
      }
    `;
    document.head.appendChild(style);
    
    // Appliquer les styles aux pièces statiques
    setTimeout(applyStaticPieceStyles, 300);
    
    // Réajuster lors du redimensionnement
    window.addEventListener('resize', function() {
      board.resize();
      setTimeout(applyStaticPieceStyles, 100);
    });
  }
  
  function applyStaticPieceStyles() {
    // Trouver toutes les pièces d'échecs statiques
    const pieces = document.querySelectorAll('.piece-417db');
    pieces.forEach(piece => {
      if (piece.src.includes('chess-themes/pieces')) {
        // Identifier si c'est un pion ou une autre pièce
        const isPawn = piece.src.includes('/wp.png') || piece.src.includes('/bp.png');
        
        if (isPawn) {
          // Styles pour les pions
          piece.style.width = '100%';
          piece.style.height = '100%';
          piece.style.top = '-7.5%';
        } else {
          // Styles pour les pièces majeures
          piece.style.width = '100%';
          piece.style.height = '122%';
          piece.style.top = '-15%';
        }
      }
    });
  }