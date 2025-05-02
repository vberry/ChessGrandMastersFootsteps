let board = null;

function initializeBoard() {
    console.log('Initialisation du plateau...');

    board = Chessboard('board', {
        position: boardFen,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/alpha/{piece}.png',
        showNotation: true,
        draggable: true,
        orientation: userSide,
        onDrop: handleMove
    });

    window.addEventListener('resize', board.resize);
}

document.addEventListener('DOMContentLoaded', initializeBoard);
