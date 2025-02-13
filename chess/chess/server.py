from flask import Flask, render_template, request, jsonify
import os
from modes.guessMove import load_pgn_games, get_game_from_file, ChessGame

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
    """Démarre une nouvelle partie avec la partie et la couleur sélectionnée."""
    game_file = request.form.get("game_file")
    user_side = request.form.get("user_side")

    if not game_file or not user_side:
        return jsonify({"error": "Paramètres manquants"}), 400

    game = get_game_from_file(os.path.join(PGN_FOLDER, game_file))
    if not game:
        return jsonify({"error": "Fichier PGN invalide."}), 400

    # Création d'un identifiant unique pour la partie
    game_id = str(len(games) + 1)
    games[game_id] = ChessGame(game, user_side)

    return render_template("deviner_prochain_coup.html", game_id=game_id, game_state=games[game_id].get_game_state())

@app.route('/submit-move', methods=["POST"])
def submit_move():
    """Gère la soumission d'un coup par l'utilisateur et met à jour le jeu."""
    game_id = request.form.get("game_id")
    move = request.form.get("move")

    if game_id not in games:
        return jsonify({'error': 'Partie introuvable'}), 400

    # Vérifier si le coup est valide et mettre à jour la partie
    result = games[game_id].submit_move(move)

    # Si result est un tuple, on le transforme en dictionnaire
    if isinstance(result, tuple):
        result = {"valid": result[0], "message": result[1]}

    if result.get("game_over"):
        del games[game_id]  # Supprime la partie terminée

    return jsonify(result)




if __name__ == "__main__":
    print("🔄 Serveur Flask démarré sur http://127.0.0.1:5000/")
    app.run(debug=True)
