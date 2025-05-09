import os
from app.models.game_model import ChessGame
from app.models.game_modelEasy import ChessGameEasy
from app.models.game_modelNormal import ChessGameNormal

# Dossier contenant les fichiers PGN
PGN_FOLDER = os.path.join(os.path.dirname(__file__), "../../dossierPgn")

def load_pgn_games():

    """
    Charge les fichiers PGN disponibles et extrait les informations essentielles sur chaque partie.

    Cette fonction parcourt tous les fichiers `.pgn` présents dans le dossier défini par `PGN_FOLDER`,
    lit leur contenu, et en extrait les métadonnées importantes (événement, noms des joueurs, résultat...).
    
    Elle est utilisée pour afficher dynamiquement la liste des parties disponibles dans le menu de l’application.

    Étapes effectuées par la fonction :
    - **Parcours du dossier** :
        - Recherche tous les fichiers se terminant par `.pgn` dans le dossier `PGN_FOLDER`.
    
    - **Lecture du fichier** :

        - Ouvre chaque fichier en lecture (`utf-8`) et lit toutes les lignes.
    
    - **Extraction des métadonnées** :

        - Pour chaque ligne du fichier :
            - Si elle commence par `[Event` → extrait le nom de l’événement.
            - Si elle commence par `[White` → extrait le nom du joueur avec les blancs.
            - Si elle commence par `[Black` → extrait le nom du joueur avec les noirs.
            - Si elle commence par `[Result` → extrait le résultat de la partie.

    - **Stockage** :

        - Les informations sont stockées dans un dictionnaire de type :
            ```python
            {
                "file": "nom_du_fichier.pgn",
                "event": "Nom de l'événement",
                "white": "Nom du joueur blanc",
                "black": "Nom du joueur noir",
                "result": "1-0 / 0-1 / 1/2-1/2"
            }
            ```
        - Chaque dictionnaire est ajouté à une liste `games`.

    ###Retourne :

        list : Une liste de dictionnaires, chacun contenant les informations d’une partie PGN.
        Cette liste peut ensuite être utilisée pour construire dynamiquement un menu de sélection.

    ###Exemple d’utilisation :

    - Affichage dans le menu HTML pour permettre à l’utilisateur de choisir une partie à rejouer ou deviner.
    """
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
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return None

def initialize_game(game_file, user_side, difficulty, games):
    """
    Initialise une nouvelle partie d’échecs à partir d’un fichier PGN et des paramètres choisis.

    Cette fonction permet de lancer une partie en fonction :

    - Du **fichier PGN sélectionné** par l'utilisateur.
    - De la **couleur des pièces** choisie (blanc ou noir).
    - Du **niveau de difficulté** demandé.

    Elle prépare ensuite une instance de jeu correspondante et choisit le bon template HTML à afficher.

    ### Paramètres :

    - **game_file (str)** : Nom du fichier PGN à charger.
    - **user_side (str)** : 'white' ou 'black', selon le choix du joueur.
    - **difficulty (str)** : Niveau de difficulté souhaité ('easy', 'normal', ou 'default').
    - **games (dict)** : Dictionnaire contenant toutes les parties en cours, identifié par `game_id`.

    ### Étapes effectuées par la fonction :

    1. **Chargement du fichier PGN** :

        - Utilise `get_game_from_file()` pour extraire les données de la partie.
        - Si aucune donnée n’est trouvée → retourne des valeurs nulles.
    
    2. **Création d’un identifiant de partie** :

        - Basé sur le nombre actuel de parties dans le dictionnaire `games`.
    
    3. **Sélection du mode de jeu selon la difficulté** :

        - `easy` → Initialise une instance de `ChessGameEasy` avec un template simplifié.
        - `normal` → Utilise `ChessGameNormal` avec un template plus exigeant.
        - Autre / par défaut → Initialise une partie standard avec la classe `ChessGame`.

    4. **Stockage et retour** :

        - La partie est enregistrée dans le dictionnaire `games` avec son identifiant unique.
        - Retourne trois éléments :
            - L’identifiant de la partie (`game_id`)
            - L’état actuel de la partie (`get_game_state()`)
            - Le nom du template HTML à rendre

    ### Retourne :

    ```python
    tuple[str, dict, str] :
        - game_id : identifiant unique de la partie
        - game_state : état initial de la partie
        - template : nom du fichier HTML à afficher selon la difficulté
    ```
    """
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

    """
    Traite le coup soumis par l'utilisateur pour une partie en cours.

    Cette fonction permet de gérer la logique lorsqu’un utilisateur propose un coup. Elle :
    - Vérifie si la partie identifiée par `game_id` existe.
    - Soumet le coup via la méthode `submit_move()` de l’objet `ChessGame`.
    - Harmonise les données retournées pour correspondre aux attentes du frontend.

    ### Paramètres :

    - **game_id (str)** : Identifiant unique de la partie concernée.
    - **move (str)** : Coup proposé par le joueur au format **UCI** (ex. `"e2e4"`).
    - **games (dict)** : Dictionnaire contenant les objets `ChessGame` pour toutes les parties en cours.

    ### Étapes effectuées par la fonction :

    1. **Vérification de l’existence du jeu** :
        - Si l’`game_id` n’est pas trouvé dans le dictionnaire, une erreur est retournée.

    2. **Soumission du coup** :
        - Utilise la méthode `submit_move()` de l’objet jeu pour traiter la logique du coup.

    3. **Adaptation des clés pour le frontend** :
        - Si la réponse contient `attempts_left`, elle est renommée en `remaining_attempts` pour rester cohérente avec les noms attendus par le frontend.

    ### Retourne :

    ```python
    dict :
        - Un dictionnaire contenant le résultat du traitement du coup, ou un message d’erreur si le jeu est introuvable.
    ```

    ### Exemple de retour possible :

    ```json
    {
        "correct": false,
        "message": "Votre coup est une bonne alternative ! (+10 points)",
        "points": 10,
        "remaining_attempts": 2
    }
    ```

    ### Exemple d’utilisation :
    
    ```python
    response = process_move("3", "e2e4", games)
    if "error" in response:
        handle_error(response["error"])
    else:
        update_ui(response)
    ```
    """
    game = games.get(game_id)
    if not game:
        return {"error": "Jeu non trouvé"}

    result = game.submit_move(move)

    # Renommer attempts_left en remaining_attempts pour correspondre au frontend
    if "attempts_left" in result:
        result["remaining_attempts"] = result.pop("attempts_left")

    return result
