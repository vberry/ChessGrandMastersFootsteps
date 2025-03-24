import os

def save_board_fen(board):
    """Sauvegarde l'état actuel du plateau sous forme de FEN dans un fichier."""
    try:
        file_path = os.path.join(os.getcwd(), "fichierFenAjour.fen")  
        with open(file_path, "w") as f:
            f.write(board.fen())  # On passe `board` directement
        print(f"FEN sauvegardée : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde FEN : {e}")

def get_fen_path(board):
        return os.path.join(os.getcwd(), "fichierFenAjour.fen")