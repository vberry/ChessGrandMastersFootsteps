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
    difficulty = request.form.get("difficulty", "normal")  # Par défaut: difficulté normale

    # Création d'un identifiant unique pour la partie
    game_id = str(len(games) + 1)

    game = load_pgn_file(os.path.join(pgn_dir, game_file))
    
    # Sélectionner la classe de jeu en fonction de la difficulté
    
    if difficulty == "easy":
        games[game_id] = ChessGameEasy(game, user_side)
        template = "deviner_prochain_coup_easy.html"
    elif difficulty == "normal":
        games[game_id] = ChessGameNormal(game, user_side)
        template = "deviner_prochain_coup.html"  # Use the "hard" template for normal difficulty
    else:  # "hard" by default
        games[game_id] = ChessGame(game, user_side)
        template = "deviner_prochain_coup.html"
    
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

# Route pour gérer un timeout
@game_bp.route("/timeout-move", methods=["POST"])
def timeout_move():
    game_id = request.form.get('game_id')
    time_taken = int(request.form.get('time_taken', 60))
    
    # Récupérer le jeu depuis la session
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Jeu non trouvé'})
    
    # Créer une copie temporaire de l'état du jeu
    current_score = game.score
    
    # Appliquer une pénalité pour le timeout
    game.score -= 5
    
    # Obtenir le coup correct qui aurait dû être joué
    if game.current_move_index < len(game.moves):
        correct_move = game.moves[game.current_move_index]
        correct_move_san = game.board.san(correct_move)
        
        # Avancer le jeu comme si un coup avait été soumis
        result = game.submit_move("e2e4", time_taken)  # On soumet un coup fictif
        
        # Ajouter les informations spécifiques au timeout
        result['timeout'] = True
        result['timeout_penalty'] = -5
        result['message'] = f"Temps écoulé! Le coup correct était: {correct_move_san}"
        
        return jsonify(result)
    else:
        return jsonify({
            'error': 'La partie est terminée',
            'game_over': True
        })