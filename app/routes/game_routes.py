import os
from flask import Blueprint, render_template, request, jsonify
from app.controllers.game_controller import GameController
from app.utils.pgn_utils import get_pgn_games, load_pgn_file
from app.models.game_model import ChessGame
from app.models.game_modelNormal import ChessGameNormal
from app.models.game_modelEasy import ChessGameEasy
#from app.models.game_modelEasy import ChessGameEasy
game_bp = Blueprint("game", __name__)

# Stockage des parties en cours
games = {}

# Définir le dossier contenant les fichiers PGN
pgn_dir = os.path.join(os.path.dirname(__file__), "..", "dossierPgn")  # 📂 Adapte ce chemin si nécessaire

# ✅ Route pour la page d'accueil
@game_bp.route("/", methods=["GET"])
def home():
    pgn_games = get_pgn_games() 
    return render_template("menu.html", pgn_games=pgn_games)


# ✅ Route pour démarrer une partie
@game_bp.route("/start-game", methods=["POST"])
def start_game():
    game_file = request.form.get("game_file")
    user_side = request.form.get("user_side")
    game_mode = request.form.get("game_mode", "lives")  # Mode par défaut: vies
    
    # Création d'un identifiant unique pour la partie
    game_id = str(len(games) + 1)
    game = load_pgn_file(os.path.join(pgn_dir, game_file))
    
    # Sélectionner la classe de jeu et le template en fonction du mode et de la difficulté
    if game_mode == "lives":
        difficulty = request.form.get("difficulty", "normal")  # Difficulté pour le mode vies
        
        if difficulty == "easy":
            games[game_id] = ChessGameEasy(game, user_side)
            template = "deviner_prochain_coup.html"
        elif difficulty == "normal":
            games[game_id] = ChessGameNormal(game, user_side)
            template = "deviner_prochain_coup.html"  # Use the "hard" template for normal difficulty
        else:  # "hard" by default
            games[game_id] = ChessGame(game, user_side)
            template = "deviner_prochain_coup.html"
            
    elif game_mode == "timer":
        timer_difficulty = request.form.get("timer_difficulty", "normal")  # Difficulté pour le mode timer
        
        if timer_difficulty == "easy":
            games[game_id] = ChessGame(game, user_side)  # Classe de jeu avec timer de 3 minutes
            template = "game_timer.html"
        elif timer_difficulty == "normal":
            games[game_id] = ChessGame(game, user_side)  # Classe de jeu avec timer de 1 minute
            template = "game_timer.html"
        else:  # "hard" par défaut (30 secondes)
            games[game_id] = ChessGame(game, user_side)  # Classe de jeu avec timer de 30 secondes
            template = "game_timer_hard.html"
    
    # Si le mode n'est pas reconnu, utilisez le mode vies par défaut
    else:
        games[game_id] = ChessGameNormal(game, user_side)
        template = "game_lives.html"
    
    return render_template(template, game_id=game_id, game_state=games[game_id].get_game_state())

# ✅ Route pour soumettre un coup
@game_bp.route("/submit-move", methods=["POST"])
def submit_move():
    game_id = request.form.get('game_id')
    move = request.form.get('move')
    
    # Récupérer le jeu depuis la session
    game = games.get(game_id)  # Changed from active_games to games
    if not game:
        return jsonify({'error': 'Jeu non trouvé'})
    
    # Soumettre le coup
    result = game.submit_move(move)
    
    # Transformer attempts_left en remaining_attempts pour la cohérence avec le frontend
    if 'attempts_left' in result:
        result['remaining_attempts'] = result['attempts_left']
        del result['attempts_left']
    
    return jsonify(result)