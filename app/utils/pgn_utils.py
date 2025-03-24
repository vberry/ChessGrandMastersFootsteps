import os
import chess

def get_pgn_games():
    """Charge les parties PGN depuis le dossier et retourne la liste des parties disponibles."""
    pgn_dir = os.path.join(os.path.dirname(__file__), "..", "dossierPgn")  # 📂 Adapte ce chemin si nécessaire
    pgn_games = []
    for file in os.listdir(pgn_dir):
        if file.endswith(".pgn"):
            with open(os.path.join(pgn_dir, file)) as pgn:
                game = chess.pgn.read_game(pgn)
                if game:
                    pgn_games.append({
                        "event": game.headers.get("Event", "Inconnu"),
                        "white": game.headers.get("White", "Inconnu"),
                        "black": game.headers.get("Black", "Inconnu"),
                        "result": game.headers.get("Result", "Inconnu"),
                        "file": file
                    })
    return pgn_games

def load_pgn_file(file_path):
    """Lit un fichier PGN et retourne la partie de jeu correspondante."""
    with open(file_path) as pgn:
        game = chess.pgn.read_game(pgn)
        moves = list(game.mainline_moves())
        print(f"Moves loaded: {moves}")
        return game