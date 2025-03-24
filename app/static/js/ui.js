function showMessage(text, isSuccess) {
    const messageDiv = document.getElementById('message');
    messageDiv.className = 'message ' + (isSuccess ? 'success' : 'error');
    messageDiv.innerHTML = text.replace('\n', '<br>');
    messageDiv.style.display = 'block';
    setTimeout(() => {
        messageDiv.style.display = 'none';
    }, 5000);
}

function animateShakePiece(square) {
    const pieceElement = document.querySelector(`.square-${square} img`);
    if (pieceElement) {
        pieceElement.style.transition = "transform 0.1s";
        pieceElement.style.transform = "translateX(-5px)";
        setTimeout(() => {
            pieceElement.style.transform = "translateX(5px)";
        }, 100);
        setTimeout(() => {
            pieceElement.style.transform = "translateX(0)";
        }, 200);
    }
}
