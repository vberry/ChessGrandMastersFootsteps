// Déclaration de la variable board globale
var board = null;

function initializeBoard(fen, userSide) {
    // S'assurer que l'élément DOM est prêt
    if (!document.getElementById('board')) {
        console.error("L'élément #board n'existe pas!");
        return;
    }

    console.log("Initialisation de l'échiquier avec FEN:", fen);
    console.log("Côté utilisateur:", userSide);

    const config = {
        position: fen,
        orientation: userSide,
        draggable: true, // Activer le drag & drop
        onDragStart: onDragStart,
        onDrop: onDrop,
        onSnapEnd: onSnapEnd,
        pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png'
    };

    // Initialiser l'échiquier
    board = Chessboard('board', config);
    console.log("Échiquier initialisé:", board);

    // Initialiser le minuteur
    initTimer();
    
    // S'assurer que l'échiquier se redimensionne correctement
    $(window).resize(function() {
        board.resize();
    });
}

// Création d'un objet chess.js pour valider les coups
var game = new Chess();

function onDragStart(source, piece, position, orientation) {
    // Permettre uniquement au joueur de déplacer ses propres pièces
    const playerColor = userSide.charAt(0);
    
    // Si ce n'est pas le tour du joueur ou si la pièce n'est pas de sa couleur
    if (piece.search(playerColor) === -1) {
        return false;
    }
}

function onDrop(source, target) {
    // Essayer de faire le mouvement
    const move = source + target;
    console.log("Tentative de coup:", move);
    
    // Au lieu de valider avec chess.js, on envoie directement au serveur
    submitMove(move);
    
    // Toujours retourner 'snapback' car c'est le serveur qui validera le coup
    return 'snapback';
}

function onSnapEnd() {
    // Mise à jour de l'affichage de l'échiquier
    board.position(game.fen());
}

// Cette fonction permet de configurer l'échiquier avec une position particulière
function setPosition(fen) {
    if (board) {
        board.position(fen);
        console.log("Position mise à jour:", fen);
    } else {
        console.error("L'échiquier n'est pas initialisé!");
    }
}