import os
import chess
import chess.pgn
from modes.guessMove import (
    load_pgn_games,
    get_game_from_file,
    convertir_notation_francais_en_anglais,
    evaluate_move_strength,
    get_best_moves_from_fen
)

class ChessGameNormal:
    def __init__(self, game, user_side):
        self.board = game.board()
        self.game = game  # Référence au jeu PGN complet
        self.all_moves = list(game.mainline_moves())
        self.user_side = user_side
        self.attempts_per_move = 3  
        
        # Récupérer les commentaires du PGN
        self.comments = []
        node = game
        while node.variations:
            next_node = node.variation(0)
            comment = next_node.comment.strip() if next_node.comment else ""
            self.comments.append(comment)
            node = next_node
        
        self.white_moves = self.all_moves[::2]
        self.black_moves = self.all_moves[1::2]
        
        self.moves = self.white_moves if user_side == 'white' else self.black_moves
        self.opponent_moves = self.black_moves if user_side == 'white' else self.white_moves
        
        self.current_move_index = 0
        self.score = 0
        self.total_moves = len(self.moves)
        
        if user_side == 'black' and len(self.white_moves) > 0:
            first_move = self.white_moves[0]
            self.last_opponent_move = self.board.san(first_move)
            self.board.push(first_move)
        else:
            self.last_opponent_move = None
        
        self.save_board_fen()
        # Obtenir les meilleurs coups dès le début
        self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))

    def get_game_state(self):
        return {
            'board_fen': self.board.fen(),
            'user_side': self.user_side,
            'current_move_index': self.current_move_index,
            'score': self.score,
            'total_moves': self.total_moves,
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move,
            'attempts_left': self.attempts_per_move
        }

    def get_comment_for_current_move(self):
        """Récupère le commentaire pour le coup actuel."""
        move_number = self.current_move_index * 2 if self.user_side == 'white' else self.current_move_index * 2 + 1
        if move_number < len(self.comments):
            return self.comments[move_number]
        return ""

    def get_comment_for_opponent_move(self):
        """Récupère le commentaire pour le coup de l'adversaire."""
        if self.user_side == 'white':
            move_number = self.current_move_index * 2 + 1
        else:
            move_number = self.current_move_index * 2
        if move_number < len(self.comments):
            return self.comments[move_number]
        return ""

    def is_pawn_move(self, move_san):
        """Détermine si un coup est un coup de pion."""
        return not (move_san[0].isupper() or 'O' in move_san)

    def validate_input(self, move):
        """Valide le format UCI des coups."""
        move = move.strip().lower()

        try:
            chess_move = chess.Move.from_uci(move)  # Convertir UCI
            if chess_move in self.board.legal_moves:
                return True, move, None  # Coup valide
            else:
                return False, None, "Coup illégal sur l'échiquier"
        except ValueError:
            return False, None, "Format UCI invalide"

    def save_board_fen(self):
        """Sauvegarde l'état actuel du plateau sous forme de FEN dans un fichier."""
        try:
            # Sauvegarde dans le dossier de l'utilisateur ou le dossier du projet
            file_path = os.path.join(os.getcwd(), "fichierFenAjour.fen")  # Sauvegarde dans le dossier du projet
            
            with open(file_path, "w") as f:
                f.write(self.board.fen())  # Écrit la FEN actuelle
            print(f"FEN sauvegardée : {file_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde FEN : {e}")

    def calculate_points(self, submitted_move, correct_move, attempt_number):
        """
        Calcule les points selon la qualité du coup et le nombre d'essais utilisés.
        Le maximum de points est obtenu au premier essai, puis diminue.
        """
        # Évaluer le coup correct
        correct_eval = evaluate_move_strength(self.board, correct_move)
        
        # Évaluer le coup soumis
        submitted_chess_move = self.board.parse_uci(submitted_move)
        submitted_eval = evaluate_move_strength(self.board, submitted_chess_move)
        
        # Coup exact du maître
        is_correct = submitted_chess_move == correct_move
        
        # Facteur de réduction des points basé sur le nombre d'essais
        attempt_factor = 1.0
        if attempt_number == 2:  # Deuxième essai
            attempt_factor = 0.7
        elif attempt_number == 3:  # Troisième essai
            attempt_factor = 0.4
        
        points = 0
        move_quality_message = ""
        checkmate_bonus = 0
        
        if is_correct:
            # C'est exactement le même coup que le maître
            base_points = 10
            points = round(base_points * attempt_factor)
            move_quality_message = f"C'est le coup historique ! (+{points} points)"
            
            # Bonus si c'est un coup de très haute qualité selon Stockfish
            if correct_eval["type"] == "mate":
                bonus = round(10 * attempt_factor)
                points += bonus
                move_quality_message += f" Et c'est un mat en {abs(correct_eval['value'])} ! (+{bonus} points bonus)"
            elif correct_eval["type"] == "cp" and correct_eval["value"] >= 200:  # Avantage significatif
                bonus = round(5 * attempt_factor)
                points += bonus
                move_quality_message += f" Et c'est un excellent coup selon Stockfish ! (+{bonus} points bonus)"
        else:
            # Le coup n'est pas celui du maître, on compare les évaluations Stockfish
            if submitted_eval["type"] == "mate" and correct_eval["type"] != "mate":
                # Le joueur a trouvé un mat que le maître n'a pas vu
                base_points = 20
                points = round(base_points * attempt_factor)
                move_quality_message = f"Vous avez trouvé un mat en {abs(submitted_eval['value'])} que le maître n'a pas vu ! (+{points} points)"
            elif submitted_eval["type"] == "mate" and correct_eval["type"] == "mate":
                # Les deux sont des mats, comparer la rapidité
                if abs(submitted_eval["value"]) <= abs(correct_eval["value"]):
                    base_points = 15
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Vous avez trouvé un mat plus rapide ou égal au maître ! (+{points} points)"
                else:
                    base_points = 5
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Vous avez trouvé un mat, mais plus lent que celui du maître. (+{points} points)"
            elif correct_eval["type"] == "mate":
                # Le maître a trouvé un mat mais pas le joueur
                base_points = -5
                points = round(base_points * attempt_factor)
                move_quality_message = f"Le maître a trouvé un mat que vous n'avez pas vu. ({points} points)"
            else:
                # Comparer les évaluations en centipawns
                diff = submitted_eval["value"] - correct_eval["value"]
                
                if diff >= 10:  # Le coup du joueur est meilleur
                    base_points = 20
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Votre coup est meilleur que celui du maître selon Stockfish ! (+{points} points)"
                elif diff >= -10:  # Différence négligeable (0.1 pawn)
                    base_points = 15
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Votre coup est pratiquement aussi bon que celui du maître ! (+{points} points)"
                elif diff >= -50:  # Bonne alternative (0.5 pawn)
                    base_points = 10
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Votre coup est une bonne alternative ! (+{points} points)"
                elif diff >= -100:  # Alternative acceptable (1 pawn)
                    base_points = 5
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Votre coup est une alternative acceptable. (+{points} points)"
                elif diff >= -200:  # Alternative inférieure (2 pawns)
                    points = 0
                    move_quality_message = f"Votre coup est inférieur à celui du maître. (+0 points)"
                else:  # Erreur significative
                    base_points = -10
                    points = round(base_points * attempt_factor)
                    move_quality_message = f"Votre coup est significativement plus faible que celui du maître. ({points} points)"
        
        # Vérifier si le coup est un échec et mat immédiat
        temp_board = chess.Board(self.board.fen())
        temp_board.push(self.board.parse_uci(submitted_move))
        if temp_board.is_checkmate():
            checkmate_base_bonus = 20
            checkmate_bonus = round(checkmate_base_bonus * attempt_factor)
            points += checkmate_bonus
            move_quality_message += f" ÉCHEC ET MAT ! (Bonus +{checkmate_bonus} points)"

        return points, move_quality_message, checkmate_bonus

    def submit_move(self, move, current_attempt=1):
        """
        Traite un coup soumis par le joueur.
        current_attempt: 1, 2 ou 3 selon l'essai actuel
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
                'last_opponent_move': self.last_opponent_move,
                'attempts_left': self.attempts_per_move - current_attempt + 1,  # Assurez-vous que cette ligne est présente
                'attempts_used': current_attempt  # Ajoutez cette ligne
            }
        correct_move = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move)
        current_comment = self.get_comment_for_current_move()
        
        is_pawn = self.is_pawn_move(correct_move_san)
        submitted_move = validated_move

        # Vérifier si le coup soumis est le même que le coup historique
        submitted_chess_move = self.board.parse_uci(submitted_move)
        is_correct = (submitted_chess_move == correct_move)
        
        # Pour l'affichage
        submitted_move_san = self.board.san(submitted_chess_move)
        
        if is_correct or current_attempt >= self.attempts_per_move:
            # Si coup correct ou dernier essai, calculer les points et passer au coup suivant
            points, move_quality_message, checkmate_bonus = self.calculate_points(
                submitted_move, correct_move, current_attempt
            )
            self.score = round(self.score + points)
            
            # Jouer le coup correct (pas celui du joueur s'il est incorrect)
            move_to_play = correct_move
            self.board.push(move_to_play)
            
            # Flag pour vérifier si c'est un échec et mat
            is_checkmate = checkmate_bonus > 0
            
            opponent_move = None
            opponent_move_san = None
            opponent_comment = None
            
            # Jouer le coup de l'adversaire
            if self.user_side == 'white' and self.current_move_index < len(self.black_moves):
                opponent_move = self.black_moves[self.current_move_index]
                opponent_move_san = self.board.san(opponent_move)
                opponent_comment = self.get_comment_for_opponent_move()
                self.board.push(opponent_move)
                self.save_board_fen()
                self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))
                self.last_opponent_move = opponent_move_san
            elif self.user_side == 'black' and (self.current_move_index + 1) < len(self.white_moves):
                opponent_move = self.white_moves[self.current_move_index + 1]
                opponent_move_san = self.board.san(opponent_move)
                opponent_comment = self.get_comment_for_opponent_move()
                self.board.push(opponent_move)
                self.save_board_fen()
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
                'previous_position_best_moves': current_position_best_moves,  # Coups alternatifs pour la position précédente
                'attempts_used': current_attempt,
                'attempts_left': 0  # Plus d'essais car on a avancé
            }
        else:
            # Coup incorrect mais il reste des essais
            return {
                'is_correct': False,
                'is_valid_format': True,
                'board_fen': self.board.fen(),
                'score': self.score,
                'game_over': False,
                'is_player_turn': True,
                'submitted_move': submitted_move_san,
                'correct_move': None,  # Ne pas révéler le coup correct tant qu'il reste des essais
                'attempts_used': current_attempt,
                'attempts_left': self.attempts_per_move - current_attempt,
                'best_moves': self.best_moves,
                'previous_position_best_moves': current_position_best_moves
            }


    def validate_input(self, move):
        """Valide le format UCI des coups."""
        move = move.strip().lower()

        try:
            chess_move = chess.Move.from_uci(move)  # Convertir UCI
            if chess_move in self.board.legal_moves:
                return True, move, None  # Coup valide
            else:
                return False, None, "Coup illégal sur l'échiquier"
        except ValueError:
            return False, None, "Format UCI invalide"

    def replay_game(game, user_side):
        """Fonction pour démarrer le jeu avec 3 essais par coup."""
        chess_game = ChessGameNormal(game, user_side)
        
        print(f"\nModes de jeu : Normal (3 essais par coup)")
        print(f"Vous jouez les {user_side.capitalize()}")
        
        while True:
            state = chess_game.get_game_state()
            
            if state['game_over'] if 'game_over' in state else chess_game.current_move_index >= chess_game.total_moves:
                print("\nPartie terminée!")
                print(f"Score final: {chess_game.score} points")
                break
            
            # Afficher l'état actuel de l'échiquier
            print("\nPosition actuelle:")
            print(chess_game.board)
            
            # Afficher le dernier coup de l'adversaire s'il existe
            if chess_game.last_opponent_move:
                print(f"\nDernier coup de l'adversaire: {chess_game.last_opponent_move}")
                
            # Afficher les meilleurs coups proposés par Stockfish
            print("\n🔍 Meilleurs coups proposés par Stockfish pour cette position:")
            for i, move in enumerate(chess_game.best_moves[:3], 1):  # Afficher les 3 meilleurs coups
                print(f"➡ {i}. {move['san']} : {move['display_score']}")
                
            # Gérer les essais
            attempt = 1
            while attempt <= chess_game.attempts_per_move:
                print(f"\nEssai {attempt}/{chess_game.attempts_per_move}")
                user_input = input("Votre coup (notation UCI, ex: e2e4) : ")
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("Partie abandonnée.")
                    return
                    
                result = chess_game.submit_move(user_input, attempt)
                print(f"DEBUG - Résultat complet: {result}")  # Ajout pour déboguer
                
                if 'error' in result:
                    print(f"Erreur: {result['error']}")
                    # Afficher explicitement la valeur attempts_left pour déboguer
                    print(f"DEBUG - attempts_left: {result.get('attempts_left', 'non défini')}")
                    continue
                    
                if result.get('is_correct', False):
                    print(f"✓ Correct! {result.get('move_quality', '')}")
                    if 'opponent_move' in result and result['opponent_move']:
                        print(f"Réponse de l'adversaire: {result['opponent_move']}")
                    break
                elif result.get('attempts_left', 0) > 0:
                    # Il reste des essais
                    print(f"✗ Incorrect. Votre coup: {result.get('submitted_move', '')}")
                    print(f"Il vous reste {result.get('attempts_left', 0)} essai(s).")
                    attempt += 1
                else:
                    # Plus d'essais, afficher le coup correct
                    print(f"✗ Incorrect après {chess_game.attempts_per_move} essais.")
                    if 'correct_move' in result:
                        print(f"Le coup correct était: {result['correct_move']}")
                        if 'opponent_move' in result and result['opponent_move']:
                            print(f"Réponse de l'adversaire: {result['opponent_move']}")
                    break


if __name__ == "__main__":
    # Définir le dossier contenant les fichiers PGN
    PGN_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dossierPgn")
    
    # Charger les parties PGN disponibles
    pgn_games = load_pgn_games(PGN_FOLDER)
    
    if not pgn_games:
        print("Aucun fichier PGN trouvé dans le dossier.")
        exit()
    
    print("\nParties disponibles :")
    for i, game in enumerate(pgn_games):
        print(f"{i + 1}. {game['event']} - {game['white']} vs {game['black']} (Résultat: {game['result']})")
    
    while True:
        try:
            choice = int(input("\nEntrez le numéro de la partie que vous voulez jouer : ")) - 1
            if 0 <= choice < len(pgn_games):
                selected_file = os.path.join(PGN_FOLDER, pgn_games[choice]["file"])
                break
            else:
                print("Numéro invalide, veuillez essayer encore.")
        except ValueError:
            print("Entrée invalide, veuillez entrer un numéro.")
    
    game = get_game_from_file(selected_file)
    
    if game is None:
        print("Le fichier PGN est vide ou corrompu.")
        exit()
    
    # Afficher les informations du jeu
    print("\nInformations sur la partie :")
    print(f"Event: {game.headers['Event']}")
    print(f"Site: {game.headers['Site']}")
    print(f"Date: {game.headers['Date']}")
    print(f"Round: {game.headers['Round']}")
    print(f"White: {game.headers['White']}")
    print(f"Black: {game.headers['Black']}")
    print(f"Result: {game.headers['Result']}")
    
    user_side = input("\nQuel joueur voulez-vous être ? (White ou Black) : ").strip().lower()
    while user_side not in ["white", "black"]:
        user_side = input("Choix invalide. Veuillez entrer 'White' ou 'Black' : ").strip().lower()
    
    # Rejouer la partie avec 3 essais par coup
    replay_game(game, user_side)