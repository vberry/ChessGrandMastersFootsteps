import chess
import chess.pgn
import os
from app.utils.engine_utils import evaluate_move_strength, get_best_moves_from_fen
from app.utils.utils import convertir_notation_francais_en_anglais
from app.utils.fen_utils import save_board_fen

class ChessGame:
    def __init__(self, game, user_side):
        """
            Initialise l'état du jeu d'échecs en fonction du jeu PGN et de la couleur choisie par l'utilisateur.

            ###Arguments:

            - game : Un objet représentant le jeu d'échecs en format PGN (Portable Game Notation).
            - user_side : Une chaîne de caractères indiquant la couleur que l'utilisateur joue ('white' ou 'black').

            ###Attributs de la classe :

            - self.board : L'objet représentant le plateau de jeu d'échecs.
            - self.game : Référence au jeu PGN complet.
            - self.all_moves : Liste de tous les mouvements du jeu sous forme de chaîne PGN.
            - self.user_side : La couleur choisie par l'utilisateur.
            - self.comments : Liste des commentaires associés à chaque mouvement du jeu.
            - self.white_moves, self.black_moves : Mouvements des blancs et des noirs séparés.
            - self.moves : Mouvements de l'utilisateur (en fonction de la couleur choisie).
            - self.opponent_moves : Mouvements de l'adversaire.
            - self.current_move_index : Index du mouvement actuel dans la liste des mouvements.
            - self.score : Score actuel du jeu (initialisé à 0).
            - self.total_moves : Nombre total de mouvements restant à jouer.
            - self.last_opponent_move : Le dernier mouvement de l'adversaire (si applicable).
            - self.best_moves : Liste des meilleurs coups calculés à partir du fichier FEN.
        """
        # Initialisation du plateau et des objets associés au jeu
        self.board = game.board() # Récupère l'état initial du plateau à partir du jeu PGN
        self.game = game  # Garder une référence au jeu PGN complet
        self.all_moves = list(game.mainline_moves()) # Liste tous les mouvements du jeu
        self.user_side = user_side # Définit la couleur de l'utilisateur ('white' ou 'black')
        
        # Initialisation des commentaires des mouvements dans le PGN
        self.comments = []
        node = game
        while node.variations: # Parcours les variations du PGN pour extraire les commentaires
            next_node = node.variation(0) # Sélectionne la première variation (les mouvements du jeu)
            comment = next_node.comment.strip() if next_node.comment else "" # Récupère le commentaire, s'il existe
            self.comments.append(comment) # Ajoute le commentaire à la liste des commentaires
            node = next_node # Passe au prochain nœud de variation
        
        # Séparation des mouvements blancs et noirs
        self.white_moves = self.all_moves[::2] # Récupère tous les mouvements des blancs (mouvements impairs)
        self.black_moves = self.all_moves[1::2] # Récupère tous les mouvements des noirs (mouvements pairs)
        
        # Détermine les mouvements de l'utilisateur et de son adversaire en fonction de la couleur choisie
        self.moves = self.white_moves if user_side == 'white' else self.black_moves
        self.opponent_moves = self.black_moves if user_side == 'white' else self.white_moves
        
        # Initialisation de l'index du mouvement actuel et du score
        self.current_move_index = 0 # Le jeu commence au premier mouvement
        self.score = 0 # Initialisation du score à 0
        self.total_moves = len(self.moves) # Nombre total de mouvements à jouer par l'utilisateur
        
        # Si l'utilisateur joue avec les pièces noires, on applique le premier coup des blancs
        if user_side == 'black' and len(self.white_moves) > 0:
            first_move = self.white_moves[0] # Récupère le premier mouvement des blancs
            self.last_opponent_move = self.board.san(first_move) # Sauvegarde le dernier mouvement de l'adversaire
            self.board.push(first_move)  # Applique ce mouvement au plateau
        else:
            self.last_opponent_move = None # Si l'utilisateur joue avec les blancs, il n'y a pas de dernier coup
        
        # Sauvegarde l'état du plateau dans un fichier FEN pour référence future
        save_board_fen(self.board)
        
        # Calcul des meilleurs coups possibles en utilisant un fichier FEN mis à jour
        self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))


    def submit_move(self, move):
        """
            Soumet un coup joué par le joueur et effectue les vérifications nécessaires avant de mettre à jour l'état du jeu.

            Cette fonction gère plusieurs aspects du jeu, y compris :

            - La validation du coup soumis par rapport au coup historique.
            - La mise à jour de l'échiquier avec les coups effectués.
            - Le calcul du score basé sur la qualité du coup joué.
            - La gestion des coups de l'adversaire, en fonction de la couleur du joueur (blanc ou noir).
            - Le contrôle du statut du jeu (si la partie est terminée, quel est le score, etc.).

            ### Étapes principales :
            
            1. **Vérification de la fin du jeu** : Si l'utilisateur a déjà joué tous ses coups, la partie est terminée.
            2. **Validation du coup de l'utilisateur** : Le coup soumis est validé en utilisant un format spécifique (par exemple, conversion de la notation française en notation anglaise).
            3. **Calcul des points et de la qualité du coup** : En fonction de la validité du coup, un score est attribué et la qualité du coup est déterminée (par exemple, un échec ou un échec et mat).
            4. **Mise à jour de l'échiquier** : Si le coup est valide, il est joué sur l'échiquier, et les coups de l'adversaire sont également gérés (en fonction de la couleur du joueur).
            5. **Retour de l'état du jeu** : La fonction retourne un dictionnaire détaillant l'état du jeu après avoir joué le coup, y compris des informations sur le statut du jeu, le score, et les coups effectués.

            ### Retourne :
            - `dict` : Un dictionnaire contenant l'état mis à jour du jeu avec les clés suivantes :
                - **'is_correct'** : Booléen indiquant si le coup soumis est correct.
                - **'correct_move'** : Le coup historique correct à jouer.
                - **'opponent_move'** : Le dernier coup joué par l'adversaire (si applicable).
                - **'board_fen'** : L'état actuel du plateau sous forme de notation FEN (Forsyth-Edwards Notation).
                - **'score'** : Le score actuel du joueur.
                - **'game_over'** : Booléen indiquant si la partie est terminée.
                - **'is_player_turn'** : Booléen indiquant si c'est le tour du joueur.
                - **'last_opponent_move'** : Le dernier coup effectué par l'adversaire.
                - **'hint'** : Un message d'astuce pour aider le joueur si le coup soumis est incorrect.
                - **'is_pawn_move'** : Booléen indiquant si le coup soumis est un coup de pion.
                - **'is_valid_format'** : Booléen indiquant si le coup soumis est au format valide.
                - **'comment'** : Le commentaire associé au coup joué (si disponible).
                - **'opponent_comment'** : Le commentaire associé au coup de l'adversaire (si disponible).
                - **'submitted_move'** : Le coup soumis par le joueur, formaté en notation SAN (Standard Algebraic Notation).
                - **'move_quality'** : Une évaluation de la qualité du coup joué.
                - **'points_earned'** : Le nombre de points obtenus pour le coup joué.
                - **'is_checkmate'** : Booléen indiquant si le coup soumis mène à un échec et mat.
                - **'checkmate_bonus'** : Le bonus de points attribué si le coup mène à un échec et mat.
                - **'best_moves'** : Liste des meilleurs coups pour la position actuelle après le coup joué.
                - **'previous_position_best_moves'** : Liste des meilleurs coups pour la position précédente.

            ### Utilité de la fonction :
            Cette fonction est essentielle pour la gestion de l'état du jeu en temps réel. Elle permet à l'utilisateur de soumettre un coup, qui est ensuite validé et joué. Elle assure également que le jeu reste cohérent en vérifiant si la partie est terminée, si les coups sont valides, et en attribuant un score en fonction de la qualité du coup joué. Elle gère aussi l'aspect stratégique du jeu en fournissant des suggestions pour les coups à venir et en tenant compte de l'adversaire.

            ### Exemple de retour :
            Si l'utilisateur soumet un coup valide, la fonction retourne un dictionnaire similaire à ceci :
            ```python
            {
                'is_correct': True,
                'correct_move': 'e2e4',
                'opponent_move': 'e7e5',
                'board_fen': 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1',
                'score': 10,
                'game_over': False,
                'is_player_turn': True,
                'last_opponent_move': 'e7e5',
                'hint': "",
                'is_pawn_move': False,
                'is_valid_format': True,
                'comment': "Excellente ouverture.",
                'opponent_comment': "Réponse standard.",
                'submitted_move': 'e2e4',
                'move_quality': "Très bon coup",
                'points_earned': 10,
                'is_checkmate': False,
                'checkmate_bonus': 0,
                'best_moves': ['e2e4', 'd2d4'],
                'previous_position_best_moves': ['e2e4', 'd2d4']
            }
            ```
        """
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}

        # Stocker les meilleurs coups avant que le joueur ne joue
        current_position_best_moves = self.best_moves.copy()

        is_valid, validated_move, error_message = self.validate_input(
            convertir_notation_francais_en_anglais(move.strip()).lower()
        )
        
        if not is_valid:
            return {
                'error': error_message,
                'is_valid_format': False,
                'board_fen': self.board.fen(),
                'score': self.score,
                'game_over': False,
                'is_player_turn': True,
                'last_opponent_move': self.last_opponent_move
            }

        correct_move = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move)
        current_comment = self.get_comment_for_current_move()
        
        is_pawn = self.is_pawn_move(correct_move_san)
        submitted_move = validated_move

        # Utiliser la nouvelle méthode de calcul des points
        points, move_quality_message, checkmate_bonus = self.calculate_points(submitted_move, correct_move)
        is_checkmate = checkmate_bonus > 0

        # Vérifier si le coup soumis est le même que le coup historique
        submitted_chess_move = self.board.parse_uci(submitted_move)
        is_correct = (submitted_chess_move == correct_move)
        
        # Pour l'affichage
        submitted_move_san = self.board.san(submitted_chess_move)

        self.score = round(self.score + points)
        
        # Jouer le coup correct (historique) sur l'échiquier
        self.board.push(correct_move)
        
        opponent_move = None
        opponent_move_san = None
        opponent_comment = None
        
        # Correction ici pour gérer correctement l'indexation des coups adverses
        if self.user_side == 'white':
            # Joueur est blanc, on doit jouer le coup noir correspondant
            if self.current_move_index < len(self.black_moves):
                opponent_move = self.black_moves[self.current_move_index]
                opponent_move_san = self.board.san(opponent_move)
                opponent_comment = self.get_comment_for_opponent_move()
                self.board.push(opponent_move)
                save_board_fen(self.board)
                self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))
                self.last_opponent_move = opponent_move_san
        else:  # user_side == 'black'
            # Joueur est noir, on doit jouer le coup blanc suivant
            if (self.current_move_index + 1) < len(self.white_moves):
                opponent_move = self.white_moves[self.current_move_index + 1]
                opponent_move_san = self.board.san(opponent_move)
                opponent_comment = self.get_comment_for_opponent_move()
                self.board.push(opponent_move)
                save_board_fen(self.board)
                self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))
                self.last_opponent_move = opponent_move_san

        self.current_move_index += 1

        hint_message = ""
        if not is_correct:
            if is_pawn:
                hint_message = "Pour les pions, entrez simplement la case d'arrivée (ex: e4)"
            else:
                hint_message = "Pour les pièces, entrez la pièce et la case d'arrivée (ex: Nf3)"

        return {
            'is_correct': is_correct,
            'correct_move': correct_move_san,
            'opponent_move': opponent_move_san,
            'board_fen': self.board.fen(),
            'score': self.score,
            'game_over': self.current_move_index >= len(self.moves),
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move,
            'hint': hint_message,
            'is_pawn_move': is_pawn,
            'is_valid_format': True,
            'comment': current_comment,
            'opponent_comment': opponent_comment,
            'submitted_move': submitted_move_san,
            'move_quality': move_quality_message,
            'points_earned': points,
            'is_checkmate': is_checkmate,
            'checkmate_bonus': checkmate_bonus,
            'best_moves': self.best_moves,  # Coups pour la position actuelle (après le coup)
            'previous_position_best_moves': current_position_best_moves  # Coups alternatifs pour la position précédente
    }

    def calculate_points(self, submitted_move, correct_move):
        """
            Cette fonction calcule le score du joueur en fonction du coup qu'il soumet et du coup historique attendu. 
            Elle évalue la qualité du coup soumis par rapport au coup "idéal" (coup du maître) en utilisant l'évaluation de 
            Stockfish et attribue des points en fonction de la précision du coup.

            La fonction prend en compte les facteurs suivants :
            - Si le coup soumis est exactement le même que celui du maître.
            - Si le joueur a trouvé un mat que le maître n'a pas vu.
            - La qualité du coup par rapport à l'évaluation de Stockfish.
            - Un bonus pour les mats.
            - Une évaluation de la position à l'aide de l'algorithme Stockfish.

            Les points sont attribués comme suit :
            - Si le joueur soumet le coup exact du maître, il obtient des points.
            - Des bonus supplémentaires sont attribués pour les coups de haute qualité (mat, avantage significatif).
            - Des pénalités peuvent être appliquées si le joueur fait un mauvais coup.

            ###Arguments :

                submitted_move (str): Le coup soumis par le joueur (notation UCI).
                correct_move (str): Le coup attendu du maître (notation UCI).

            ###Retourne :

                tuple : Un tuple contenant :

                    - points (int) : Le score attribué au joueur pour le coup soumis.
                    - move_quality_message (str) : Un message expliquant la qualité du coup soumis.
                    - checkmate_bonus (int) : Un bonus supplémentaire si le coup soumis a mené à un échec et mat.
        """
        # Évaluer le coup correct
        correct_eval = evaluate_move_strength(self.board, correct_move)
        
        # Évaluer le coup soumis
        submitted_chess_move = self.board.parse_uci(submitted_move)
        submitted_eval = evaluate_move_strength(self.board, submitted_chess_move)
        
        # Inversion des évaluations pour les noirs car Stockfish donne toujours 
        # l'évaluation du point de vue des blancs
        if self.user_side == 'black':
            # Pour les évaluations en centipawns, on inverse le signe
            if correct_eval["type"] == "cp":
                correct_eval["value"] = -correct_eval["value"]
            if submitted_eval["type"] == "cp":
                submitted_eval["value"] = -submitted_eval["value"]
        
        # Coup exact du maître
        is_correct = submitted_chess_move == correct_move
        
        points = 0
        move_quality_message = ""
        checkmate_bonus = 0
        
        if is_correct:
            # C'est exactement le même coup que le maître
            points = 10
            move_quality_message = f"C'est le coup historique ! (+10 points)"
            
            # Bonus si c'est un coup de très haute qualité selon Stockfish
            if correct_eval["type"] == "mate":
                points += 10
                move_quality_message += f" Et c'est un mat en {abs(correct_eval['value'])} ! (+10 points bonus)"
            elif correct_eval["type"] == "cp" and correct_eval["value"] >= 200:  # Avantage significatif
                points += 5
                move_quality_message += f" Et c'est un excellent coup selon Stockfish ! (+5 points bonus)"
        else:
            # Le coup n'est pas celui du maître, on compare les évaluations Stockfish
            if submitted_eval["type"] == "mate" and correct_eval["type"] != "mate":
                # Le joueur a trouvé un mat que le maître n'a pas vu
                points = 20
                move_quality_message = f"Vous avez trouvé un mat en {abs(submitted_eval['value'])} que le maître n'a pas vu ! (+20 points)"
            elif submitted_eval["type"] == "mate" and correct_eval["type"] == "mate":
                # Les deux sont des mats, comparer la rapidité
                if abs(submitted_eval["value"]) <= abs(correct_eval["value"]):
                    points = 15
                    move_quality_message = f"Vous avez trouvé un mat plus rapide ou égal au maître ! (+15 points)"
                else:
                    points = 5
                    move_quality_message = f"Vous avez trouvé un mat, mais plus lent que celui du maître. (+5 points)"
            elif correct_eval["type"] == "mate":
                # Le maître a trouvé un mat mais pas le joueur
                points = -5
                move_quality_message = f"Le maître a trouvé un mat que vous n'avez pas vu. (-5 points)"
            else:
                # Comparer les évaluations en centipawns
                diff = submitted_eval["value"] - correct_eval["value"]
                
                if diff >= 10:  # Le coup du joueur est meilleur
                    points = 20
                    move_quality_message = f"Votre coup est meilleur que celui du maître selon Stockfish ! (+20 points)"
                elif diff >= -10:  # Différence négligeable (0.1 pawn)
                    points = 15
                    move_quality_message = f"Votre coup est pratiquement aussi bon que celui du maître ! (+15 points)"
                elif diff >= -50:  # Bonne alternative (0.5 pawn)
                    points = 10
                    move_quality_message = f"Votre coup est une bonne alternative ! (+10 points)"
                elif diff >= -100:  # Alternative acceptable (1 pawn)
                    points = 5
                    move_quality_message = f"Votre coup est une alternative acceptable. (+5 points)"
                elif diff >= -200:  # Alternative inférieure (2 pawns)
                    points = 0
                    move_quality_message = f"Votre coup est inférieur à celui du maître. (+0 points)"
                else:  # Erreur significative
                    points = -10
                    move_quality_message = f"Votre coup est significativement plus faible que celui du maître. (-10 points)"
        
        # Vérifier si le coup est un échec et mat immédiat
        temp_board = chess.Board(self.board.fen())
        temp_board.push(self.board.parse_uci(submitted_move))
        if temp_board.is_checkmate():
            checkmate_bonus = 20
            points += checkmate_bonus
            move_quality_message += f" ÉCHEC ET MAT ! (Bonus +{checkmate_bonus} points)"

        return points, move_quality_message, checkmate_bonus
    
    
    def get_game_state(self):
        """
            Retourne l'état actuel du jeu sous forme de dictionnaire.

            Cette méthode extrait plusieurs informations clés liées au jeu d'échecs en cours, 
            telles que l'état actuel du plateau (au format FEN), la couleur de l'utilisateur, 
            le mouvement actuel, le score, et d'autres informations importantes pour gérer l'état du jeu.

            ### Retroune :

                dict : Un dictionnaire contenant l'état actuel du jeu avec les clés suivantes :
                    - 'board_fen' : L'état actuel du plateau sous forme de notation FEN.
                    - 'user_side' : La couleur de l'utilisateur ('white' ou 'black').
                    - 'current_move_index' : L'indice du mouvement actuel dans la liste des mouvements.
                    - 'score' : Le score actuel du jeu.
                    - 'total_moves' : Le nombre total de mouvements restant à jouer.
                    - 'is_player_turn' : Booléen indiquant si c'est le tour de l'utilisateur.
                    - 'last_opponent_move' : Le dernier mouvement effectué par l'adversaire (s'il y en a un).
        """
        return {
            'board_fen': self.board.fen(),  # Obtient l'état actuel du plateau au format FEN (Forsyth-Edwards Notation)
            'user_side': self.user_side,  # Retourne la couleur de l'utilisateur ('white' ou 'black')            
            'current_move_index': self.current_move_index,  # L'indice du mouvement actuel dans la séquence des mouvements           
            'score': self.score,  # Le score actuel du jeu (initialisé à 0 au départ)            
            'total_moves': self.total_moves,  # Nombre total de mouvements restants que l'utilisateur doit jouer            
            'is_player_turn': True,  # Indique si c'est actuellement le tour de l'utilisateur (ici fixé à True, peut être ajusté selon l'état du jeu)           
            'last_opponent_move': self.last_opponent_move  # Le dernier mouvement effectué par l'adversaire (si applicable)
        }

    def get_comment_for_current_move(self):
        """
            Récupère le commentaire associé au coup actuel du joueur.

            Cette fonction détermine quel coup est en train d'être joué en fonction de l'indice actuel 
            (`current_move_index`) et de la couleur de l'utilisateur (`user_side`), puis elle retourne 
            le commentaire associé à ce coup dans la liste des commentaires extraits du fichier PGN.

            La logique de cette fonction dépend de la couleur du joueur (blanc ou noir). 
            Si le joueur est blanc, elle accède aux coups aux indices pairs, tandis que si le joueur 
            est noir, elle accède aux indices impairs. Cela est dû à la façon dont les coups sont 
            organisés dans la liste `self.comments`.

            ###Retourne :

                str : Le commentaire associé au coup actuel du joueur, ou une chaîne vide si 
                aucun commentaire n'est disponible pour ce coup.
        """
        # Calcul de l'indice du coup actuel dans la liste des commentaires
        move_number = self.current_move_index * 2 if self.user_side == 'white' else self.current_move_index * 2 + 1

        # Vérifier si l'indice est valide et s'il y a un commentaire pour ce coup
        if move_number < len(self.comments):
            return self.comments[move_number]
        
        # Si aucun commentaire n'est disponible pour ce coup, retourner une chaîne vide
        return ""

    def get_comment_for_opponent_move(self):
        """
            Récupère le commentaire associé au coup de l'adversaire.

            Cette fonction détermine quel coup de l'adversaire est en train d'être joué en fonction 
            de l'indice actuel (`current_move_index`) et de la couleur de l'utilisateur (`user_side`), 
            puis elle retourne le commentaire associé à ce coup dans la liste des commentaires extraits 
            du fichier PGN.

            La logique de cette fonction dépend également de la couleur du joueur (blanc ou noir). 
            Si le joueur est blanc, elle accède aux coups adverses aux indices impairs (coup de l'adversaire après chaque coup blanc). 
            Si le joueur est noir, elle accède aux indices pairs (coup de l'adversaire après chaque coup noir).

            ###Retourne :

                str : Le commentaire associé au coup de l'adversaire, ou une chaîne vide si 
                aucun commentaire n'est disponible pour ce coup.
        """
        # Calcul de l'indice du coup de l'adversaire en fonction de la couleur du joueur
        if self.user_side == 'white':
            move_number = self.current_move_index * 2 + 1# Si l'utilisateur est blanc, on prend les indices impairs  
        else:
            move_number = self.current_move_index * 2 # Si l'utilisateur est noir, on prend les indices pairs
        
        # Vérifier si l'indice est valide et s'il y a un commentaire pour ce coup de l'adversaire
        if move_number < len(self.comments):
            return self.comments[move_number]
        
        # Si aucun commentaire n'est disponible pour ce coup, retourner une chaîne vide
        return ""

    def is_pawn_move(self, move_san):
        """
            Vérifie si le coup joué est un coup de pion.

            Cette fonction examine la notation **SAN (Standard Algebraic Notation)** d'un coup pour 
            déterminer s'il s'agit d'un **coup de pion**. Elle effectue cette vérification en analysant 
            la première lettre de la notation et en vérifiant s'il y a un roque ("O") dans le coup.

            ###Règles utilisées :

            - Un coup de pion est généralement une lettre minuscule, ce qui permet de distinguer les pions des autres pièces (qui sont représentées par des lettres majuscules, comme "N" pour un cavalier).
            - Un coup de roque (notation "O-O" ou "O-O-O") est également exclu, car il s'agit d'un mouvement spécial des pièces qui n'est pas un mouvement de pion.

            ###Retourne :

                bool : `True` si le coup est un coup de pion, sinon `False`.
        """
        return not (move_san[0].isupper() or 'O' in move_san)

    def validate_input(self, move):
        """
            Valide l'entrée du coup soumis en format UCI (Universal Chess Interface).

            Cette fonction permet de vérifier si un coup soumis par l'utilisateur est valide en utilisant la 
            notation **UCI** (Universal Chess Interface), qui est le format standard utilisé pour les coups d'échecs.
            Elle effectue deux vérifications principales :

            1. Si le format du coup est valide en UCI.
            2. Si le coup est légal sur l'échiquier actuel.

            ###Étapes effectuées par la fonction :

            - **Normalisation** : Le coup soumis est nettoyé et converti en minuscule pour garantir que la saisie soit uniforme.
            - **Conversion en UCI** : La chaîne de caractères est convertie en un objet `Move` de la bibliothèque `chess`, qui représente un coup au format UCI.
            - **Vérification de la légalité** : Le coup est vérifié pour s'assurer qu'il est légal sur l'échiquier actuel (il ne doit pas être un coup qui mettrait le roi en échec ou un coup interdit selon les règles du jeu).

            ###Retourne :

                tuple : Un tuple contenant trois éléments :
                    - **bool** : `True` si le coup est valide et légal, `False` sinon.
                    - **str** : Le coup soumis dans sa forme brute (si valide).
                    - **str** : Un message d'erreur expliquant pourquoi le coup est invalide ou illégal (si applicable).
        """
        move = move.strip().lower()

        try:
            chess_move = chess.Move.from_uci(move)  # Convertir UCI
            if chess_move in self.board.legal_moves:
                return True, move, None  # Coup valide
            else:
                return False, None, "Coup illégal sur l'échiquier"
        except ValueError:
            return False, None, "Format UCI invalide"
