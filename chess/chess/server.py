from flask import Flask, render_template, request, jsonify
import os
from modes.guessMove import load_pgn_games, get_game_from_file, ChessGame
from modes.guessMoveEasy import ChessGameEasy
from modes.guessMoveNormal import ChessGameNormal

app = Flask(__name__)

# Stockage des parties en cours
games = {}

# Définir le dossier contenant les fichiers PGN
PGN_FOLDER = os.path.join(os.path.dirname(__file__), "dossierPgn")

@app.route('/')
def home():
    """Affiche la page d'accueil avec la liste des parties disponibles."""
    pgn_games = load_pgn_games(PGN_FOLDER)
    return render_template("menu.html", pgn_games=pgn_games)

@app.route('/start-game', methods=["POST"])
def start_game():
    """Démarre une nouvelle partie avec la partie, la couleur et la difficulté sélectionnées."""
    game_file = request.form.get("game_file")
    user_side = request.form.get("user_side")
    difficulty = request.form.get("difficulty")

    if not game_file or not user_side or not difficulty:
        return jsonify({"error": "Paramètres manquants"}), 400

    game = get_game_from_file(os.path.join(PGN_FOLDER, game_file))
    if not game:
        return jsonify({"error": "Fichier PGN invalide."}), 400

    # Création d'un identifiant unique pour la partie
    game_id = str(len(games) + 1)
    
    # Créer le bon type de jeu selon la difficulté
    if difficulty == "easy":
        games[game_id] = ChessGameEasy(game, user_side)
        return render_template("deviner_prochain_coup_easy.html", game_id=game_id, game_state=games[game_id].get_game_state())
    elif difficulty == "normal":
        games[game_id] = ChessGameNormal(game, user_side)
        return render_template("deviner_prochain_coup_normal.html", game_id=game_id, game_state=games[game_id].get_game_state())
    else:  # default to hard
        games[game_id] = ChessGame(game, user_side)
        return render_template("deviner_prochain_coup.html", game_id=game_id, game_state=games[game_id].get_game_state())

@app.route('/submit-move', methods=['POST'])
def submit_move():
    game_id = request.form['game_id']
    move = request.form['move']
    
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

if __name__ == "__main__":
    print("🔄 Serveur Flask démarré sur http://127.0.0.1:5000/")
    app.run(debug=True)