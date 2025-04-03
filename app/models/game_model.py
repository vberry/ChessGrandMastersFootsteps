import chess
import chess.pgn
import os
from app.utils.engine_utils import evaluate_move_strength, get_best_moves_from_fen
from app.utils.utils import convertir_notation_francais_en_anglais
from app.utils.fen_utils import save_board_fen

class ChessGame:
    def __init__(self, game, user_side):
        self.board = game.board()
        self.game = game  # Garder une référence au jeu PGN complet
        self.all_moves = list(game.mainline_moves())
        self.user_side = user_side
        
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
        
        save_board_fen(self.board)
        # ✅ Obtenir les meilleurs coups dès le début
        self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))

    def get_game_state(self):
        return {
            'board_fen': self.board.fen(),
            'user_side': self.user_side,
            'current_move_index': self.current_move_index,
            'score': self.score,
            'total_moves': self.total_moves,
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move
        }

    def submit_move(self, move):
        """
        Handles a move submitted by the player and updates the game state accordingly.
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
        Calcule les points selon la qualité du coup soumis par rapport au coup correct
        en utilisant Stockfish pour l'évaluation directe, en tenant compte de la couleur du joueur.
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
        return {
            'board_fen': self.board.fen(),
            'user_side': self.user_side,
            'current_move_index': self.current_move_index,
            'score': self.score,
            'total_moves': self.total_moves,
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move
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


        
class ChessGameEasy(ChessGame):
    """Version facile du jeu d'échecs avec des indices et des pénalités réduites."""
    
    def __init__(self, game, user_side):
        super().__init__(game, user_side)
        self.hints_used = 0
    
    def get_hint(self):
        """Fournit un indice pour le coup actuel."""
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}
        
        correct_move = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move)
        
        # Générer un indice en fonction du type de pièce
        if self.is_pawn_move(correct_move_san):
            hint = f"Le prochain coup est un coup de pion vers {correct_move_san[-2:]}"
        elif 'x' in correct_move_san:
            hint = "Le prochain coup est une prise"
        elif 'O-O' in correct_move_san:
            hint = "Pensez au roque"
        else:
            piece = correct_move_san[0]
            piece_names = {'K': 'Roi', 'Q': 'Dame', 'R': 'Tour', 'B': 'Fou', 'N': 'Cavalier'}
            piece_name = piece_names.get(piece, "pièce")
            hint = f"Le prochain coup implique un {piece_name}"
        
        self.hints_used += 1
        # Chaque indice coûte 2 points
        self.score -= 2
        
        return {
            'hint': hint,
            'points_deducted': 2,
            'current_score': self.score
        }
    
    def calculate_points(self, submitted_move, correct_move):
        """Version modifiée avec des pénalités réduites pour le mode facile."""
        # Appeler la méthode de base
        points, move_quality_message, checkmate_bonus = super().calculate_points(submitted_move, correct_move)
        
        # Réduire les pénalités de moitié
        if points < 0:
            points = points // 2
            move_quality_message += " (Pénalité réduite car mode facile)"
        
        # Bonus supplémentaire pour les bons coups
        if points > 0:
            bonus = 2
            points += bonus
            move_quality_message += f" (Bonus mode facile: +{bonus})"
        
        return points, move_quality_message, checkmate_bonus