import os

def save_board_fen(board, filename):
    """Sauvegarde l'état actuel du plateau sous forme de FEN dans un fichier situé dans le dossier 'fen_saves'."""
    try:
        save_dir = os.path.join(os.getcwd(), "fen_saves")
        os.makedirs(save_dir, exist_ok=True)  # Crée le dossier s'il n'existe pas

        file_path = os.path.join(save_dir, filename)
        with open(file_path, "w") as f:
            f.write(board.fen())
        print(f"FEN sauvegardée : {file_path}")
    except Exception as e:
        print(f"Erreur lors de la sauvegarde FEN : {e}")


def get_fen_path(board):
        return os.path.join(os.getcwd(), "fichierFenAjour.fen")