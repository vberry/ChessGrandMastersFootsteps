import os
import uuid
from flask import Blueprint, render_template, request, jsonify, make_response
from app.controllers.game_controller import GameController
from app.utils.pgn_utils import get_pgn_games, load_pgn_file
from app.models.game_model import ChessGame
from app.models.game_modelNormal import ChessGameNormal
from app.models.game_modelEasy import ChessGameEasy
from app.models.game_model1min import ChessGame1Min
from app.models.game_model3min import ChessGame3Min  
from app.models.game_model30sec import ChessGame30sec

game_bp = Blueprint("game", __name__)

# Stockage des parties en cours
games = {}

# Définir le dossier contenant les fichiers PGN
pgn_dir = os.path.join(os.path.dirname(__file__), "..", "dossierPgn")  # 📂 Adapte ce chemin si nécessaire

# ✅ Route pour la page d'accueil
@game_bp.route("/", methods=["GET"])
def home():
    """
    Route principale de l'application — Affiche la page d'accueil.

    Cette fonction est liée à la route « `/` » de l'application Flask, et elle est appelée
    lorsqu'un utilisateur accède à la page d’accueil.

    Elle sert à récupérer et afficher la liste des parties d’échecs disponibles (au format PGN)
    en les passant à un template HTML.

    ###Étapes effectuées par la fonction :

    1. **Appel à `get_pgn_games()`** : Cette fonction récupère tous les fichiers PGN disponibles dans un répertoire.
    2. **Affichage du menu** : La fonction utilise `render_template()` pour afficher la page `menu.html`
       en lui passant la variable `pgn_games`.

    ###Paramètres :

        Aucun paramètre direct, mais fonctionne en réponse à une requête HTTP GET.

    ###Retourne :

        flask.Response : Le rendu HTML de la page `menu.html`, incluant la liste des parties PGN.

    ###Utilité :

        - Sert de point d’entrée principal à l'application.
        - Permet à l'utilisateur de choisir une partie PGN à analyser ou à jouer.
        - Interface intuitive pour démarrer une session de jeu ou d’apprentissage.
    """
    pgn_games = get_pgn_games() 
    return render_template("menu.html", pgn_games=pgn_games)


@game_bp.route("/start-game", methods=["POST"])
def start_game():
    """
    Démarre une nouvelle partie d'échecs à partir d'un fichier PGN et des préférences de l'utilisateur.

    Cette route est appelée lorsqu'un utilisateur soumet le formulaire de sélection de partie et de couleur
    via la méthode POST (depuis la page d’accueil, par exemple).

    Elle permet d'initialiser une nouvelle instance de partie, de configurer le contrôleur de jeu, et
    de charger l'état initial sur l’interface `deviner_prochain_coup.html`.

    ###Étapes effectuées par la fonction :

    1. **Récupération des paramètres du formulaire** :

        - `game_file` : Le fichier PGN choisi par l'utilisateur.
        - `user_side` : La couleur sélectionnée (`white` ou `black`).
    2. **Création d'un identifiant unique de partie** : Basé sur la taille actuelle du dictionnaire `games`.
    3. **Chargement du fichier PGN** : Le fichier PGN est lu et transformé en objet jeu.
    4. **Initialisation du contrôleur de jeu** : Une instance `GameController` est créée pour gérer la logique.
    5. **Démarrage de la partie** : La méthode `start_game()` du contrôleur est appelée.
    6. **Stockage de l'instance du jeu** : Une instance de `ChessGame` est enregistrée dans le dictionnaire global `games`.
    7. **Rendu HTML** : La vue `deviner_prochain_coup.html` est rendue avec l’état initial du jeu.

    ###Paramètres :

        Aucun en paramètre direct Python, mais récupère deux champs via `request.form` :
        - **game_file** (str) : Nom du fichier PGN sélectionné.
        - **user_side** (str) : Couleur choisie par l’utilisateur (`white` ou `black`).

    ###Retourne :

        flask.Response : La page HTML `deviner_prochain_coup.html` affichant le premier état de la partie.

    ###Utilité :

        - Initialise dynamiquement une nouvelle session de jeu selon le choix utilisateur.
        - Relie les composants du backend (fichier PGN, logique de partie, interface utilisateur).
        - Point de départ interactif du jeu où le joueur va commencer à deviner les coups.
    """
    game_file = request.form.get("game_file")
    user_side = request.form.get("user_side")
    game_mode = request.form.get("game_mode", "lives")  # Mode par défaut: vies
    # Création d'un identifiant unique pour la partie
    # game_id = str(len(games) + 1)
    game_id = str(uuid.uuid4())


    game = load_pgn_file(os.path.join(pgn_dir, game_file))
    
    # Initialiser le contrôleur de jeu
    game_controller = GameController(game, user_side)
    game_controller.start_game()
    print(user_side)
    
    # Sélectionner la classe de jeu et le template en fonction du mode et de la difficulté
    if game_mode == "lives":
        difficulty = request.form.get("difficulty", "normal")  # Difficulté pour le mode vies
        if difficulty == "easy":
            games[game_id] = ChessGameEasy(game, user_side, game_id=game_id)
            template = "deviner_prochain_coup_easy.html"
        elif difficulty == "normal":
            games[game_id] = ChessGameNormal(game, user_side, game_id=game_id)
            template = "deviner_prochain_coup.html"  # Use the "hard" template for normal difficulty
        else:  # "hard" by default
            games[game_id] = ChessGame(game, user_side, game_id=game_id)
            template = "deviner_prochain_coup.html"
    elif game_mode == "timer":
        timer_difficulty = request.form.get("timer_difficulty", "normal")  # Difficulté pour le mode timer
        if timer_difficulty == "easy":
            games[game_id] = ChessGame3Min(game, user_side, game_id=game_id)  # Nouveau mode 3 minutes
            template = "game_timer_3min.html"
        elif timer_difficulty == "normal":
            games[game_id] = ChessGame1Min(game, user_side, game_id=game_id)  # Classe de jeu avec timer de 1 minute
            template = "game_timer_1min.html"
        else:  # "hard" par défaut (30 secondes)
            games[game_id] = ChessGame30sec(game, user_side, game_id=game_id)  # Classe de jeu avec timer de 30 secondes
            template = "game_timer_hard.html"
    # Si le mode n'est pas reconnu, utilisez le mode vies par défaut
    else:
        games[game_id] = ChessGameNormal(game, user_side, game_id=game_id)
        template = "game_lives.html"
    
    # À la fin, utilisez cette approche simplifiée
    rendered_template = render_template(template, game_id=game_id, game_state=games[game_id].get_game_state())
    resp = make_response(rendered_template)
    resp.set_cookie('current_game_id', game_id, max_age=3600)
    return resp


@game_bp.route("/submit-move", methods=["POST"])
def submit_move():

    """
    Soumet un coup joué par l'utilisateur et retourne le résultat au format JSON.

    Cette route est déclenchée lorsqu’un joueur entre un coup sur l’interface 
    (par exemple dans un champ de texte ou en cliquant sur une case).  
    Elle va appeler la logique du jeu pour valider et traiter ce coup, 
    puis renvoyer les informations actualisées de la partie à afficher dans l’interface.

    ###Étapes effectuées par la fonction :
    
    1. **Récupération des données POST** :
        - `game_id` : identifiant de la partie en cours.
        - `move` : le coup soumis par le joueur (au format UCI ou personnalisé selon ton système).
    
    2. **Vérification de l'existence de la partie** :
        - On tente de retrouver l'objet `ChessGame` associé à `game_id` dans le dictionnaire `games`.
        - Si aucun jeu n’est trouvé, on retourne une erreur JSON.

    3. **Soumission du coup** :
        - Le coup est passé à la méthode `submit_move()` de la classe `ChessGame`, 
          qui renvoie un dictionnaire de résultats : validité, points, messages, FEN, etc.

    4. **Compatibilité frontend** :
        - Si le résultat contient la clé `attempts_left`, elle est renommée en `remaining_attempts` 
          pour s’adapter au nom utilisé côté JavaScript.

    ###Retourne :

        `jsonify(result)` : Un objet JSON contenant :
        - `is_correct` : si le coup est bon.
        - `score`, `board_fen`, `move_quality`, etc.
        - `error` : message d'erreur en cas de problème.
        - `remaining_attempts` : tentatives restantes si applicable.

    ###Utilité :

    - Cœur de l’interaction utilisateur → permet d’évaluer et réagir au coup soumis.
    - Gère la logique de feedback pédagogique (qualité du coup, aide, points...).
    - Gère la continuité de la partie (évolution de l’échiquier et passage au coup suivant).
    """

    game_id = request.form.get('game_id')
    move = request.form.get('move')
    
    # Récupérer le jeu depuis la session
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Jeu non trouvé'})
    
    # Soumettre le coup
    result = game.submit_move(move)
    
    # Transformer attempts_left en remaining_attempts pour la cohérence avec le frontend
    if 'attempts_left' in result:
        result['remaining_attempts'] = result['attempts_left']
        del result['attempts_left']
    
    return jsonify(result)