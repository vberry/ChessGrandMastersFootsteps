function displayAlternativeMoves(alternativeMoves, playerMove) {
    // Chercher ou créer le conteneur principal
    let alternativeMovesContainer = document.getElementById('alternative-moves-container');
    
    if (!alternativeMovesContainer) {
        // Créer le conteneur et l'ajouter directement au body
        alternativeMovesContainer = document.createElement('div');
        alternativeMovesContainer.id = 'alternative-moves-container';
        alternativeMovesContainer.className = 'alternative-moves-section';
        alternativeMovesContainer.innerHTML = '<h3>Coups alternatifs pour la position précédente:</h3><div class="alternative-moves-list"></div>';
        document.body.appendChild(alternativeMovesContainer);
    }
    
    const alternativeMovesList = alternativeMovesContainer.querySelector('.alternative-moves-list');
    alternativeMovesList.innerHTML = '';
    
    if (!alternativeMoves || alternativeMoves.length === 0) {
        alternativeMovesList.innerHTML = '<p>Aucune analyse disponible</p>';
        return;
    }
    
    // Trouver le coup joué par le joueur parmi les alternatives
    const playerMoveInfo = alternativeMoves.find(move => 
        move.uci.toLowerCase() === playerMove.toLowerCase() || 
        move.san.toLowerCase() === playerMove.toLowerCase()
    );
    
    // Afficher le coup du joueur en premier avec une indication
    if (playerMoveInfo) {
        const moveElement = document.createElement('div');
        moveElement.className = 'alternative-move-item player-move';
        
        moveElement.innerHTML = `
            <div class="move-indicator">✓</div>
            <div class="move-uci">${playerMoveInfo.uci}</div>
            <div class="move-san">(${playerMoveInfo.san})</div>
            <div class="move-score">${playerMoveInfo.display_score}</div>
            <div class="move-comment">Votre coup</div>
        `;
        alternativeMovesList.appendChild(moveElement);
    }
    
    // Afficher les autres alternatives
    alternativeMoves.forEach((move) => {
        // Ne pas réafficher le coup du joueur
        if (playerMoveInfo && move.uci === playerMoveInfo.uci) {
            return;
        }
        
        const moveElement = document.createElement('div');
        moveElement.className = 'alternative-move-item';
        
        moveElement.innerHTML = `
            <div class="move-indicator"></div>
            <div class="move-uci">${move.uci}</div>
            <div class="move-san">(${move.san})</div>
            <div class="move-score">${move.display_score}</div>
            <div class="move-comment"></div>
        `;
        alternativeMovesList.appendChild(moveElement);
    });
}