function displayAlternativeMoves(alternativeMoves, playerMove) {
    // Récupérer la liste existante dans le HTML
    const alternativeMovesList = document.querySelector('.alternative-moves-list');

    if (!alternativeMovesList) {
        console.error("Erreur : L'élément '.alternative-moves-list' est introuvable dans le HTML.");
        return;
    }

    // Vider la liste avant d’ajouter de nouveaux éléments
    alternativeMovesList.innerHTML = '';

    if (!alternativeMoves || alternativeMoves.length === 0) {
        alternativeMovesList.innerHTML = '<li>Aucune analyse disponible</li>';
        return;
    }

    // Trouver le coup joué par le joueur parmi les alternatives
    const playerMoveInfo = alternativeMoves.find(move => 
        move.uci.toLowerCase() === playerMove.toLowerCase() || 
        move.san.toLowerCase() === playerMove.toLowerCase()
    );

    // Afficher le coup du joueur en premier avec une indication
    if (playerMoveInfo) {
        const moveItem = document.createElement('li');
        moveItem.className = 'alternative-move-item player-move';
        moveItem.innerHTML = `
            <strong>${playerMoveInfo.san}</strong> (${playerMoveInfo.uci}) - ${playerMoveInfo.display_score} <em>(Votre coup)</em>
        `;
        alternativeMovesList.appendChild(moveItem);
    }

    // Ajouter les autres alternatives
    alternativeMoves.forEach((move) => {
        if (playerMoveInfo && move.uci === playerMoveInfo.uci) {
            return; // Ne pas réafficher le coup du joueur
        }

        const moveItem = document.createElement('li');
        moveItem.className = 'alternative-move-item';
        moveItem.innerHTML = `
            <strong>${move.san}</strong> (${move.uci}) - ${move.display_score}
        `;
        alternativeMovesList.appendChild(moveItem);
    });
}
