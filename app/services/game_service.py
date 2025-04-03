import os
from app.models.game_model import ChessGame, ChessGameEasy
from app.models.game_modelNormal import ChessGameNormal

# Dossier contenant les fichiers PGN
PGN_FOLDER = os.path.join(os.path.dirname(__file__), "../../dossierPgn")

def load_pgn_games():
    """Charge la liste des fichiers PGN disponibles et extrait les informations des parties."""
    games = []
    for file_name in os.listdir(PGN_FOLDER):
        if file_name.endswith(".pgn"):
            file_path = os.path.join(PGN_FOLDER, file_name)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Extraire les infos du fichier PGN (événement, joueurs, résultat)
            game_info = {"file": file_name}
            for line in lines:
                if line.startswith("[Event"):
                    game_info["event"] = line.split('"')[1]
                elif line.startswith("[White"):
                    game_info["white"] = line.split('"')[1]
                elif line.startswith("[Black"):
                    game_info["black"] = line.split('"')[1]
                elif line.startswith("[Result"):
                    game_info["result"] = line.split('"')[1]
            
            games.append(game_info)
    
    return games

def get_game_from_file(file_path):
    """Récupère le contenu d'un fichier PGN."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None

def initialize_game(game_file, user_side, difficulty, games):
    """Initialise une partie en fonction de la difficulté et de la couleur du joueur."""
    game_data = get_game_from_file(os.path.join(PGN_FOLDER, game_file))
    if not game_data:
        return None, None, None  # Erreur si le fichier PGN est introuvable

    game_id = str(len(games) + 1)

    # Sélection du mode de jeu
    if difficulty == "easy":
        games[game_id] = ChessGameEasy(game_data, user_side)
        template = "deviner_prochain_coup_easy.html"
    elif difficulty == "normal":
        games[game_id] = ChessGameNormal(game_data, user_side)
        template = "deviner_prochain_coup_normal.html"
    else:
        games[game_id] = ChessGame(game_data, user_side)
        template = "deviner_prochain_coup.html"

    return game_id, games[game_id].get_game_state(), template

def process_move(game_id, move, games):
    """Vérifie un coup joué et met à jour l'état de la partie."""
    game = games.get(game_id)
    if not game:
        return {"error": "Jeu non trouvé"}

    result = game.submit_move(move)

    # Renommer attempts_left en remaining_attempts pour correspondre au frontend
    if "attempts_left" in result:
        result["remaining_attempts"] = result.pop("attempts_left")

    return result
