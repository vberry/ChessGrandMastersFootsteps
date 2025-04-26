import chess
import chess.pgn
import os
from app.utils.engine_utils import evaluate_move_strength, get_best_moves_from_fen
from app.utils.utils import convertir_notation_francais_en_anglais
from app.utils.fen_utils import save_board_fen
from app.models.game_model import ChessGame


class ChessGameEasy(ChessGame):
    """Version facile du jeu d'échecs où le joueur a 5 essais pour deviner le coup correct et des pénalités réduites."""
    
    def __init__(self, game, user_side):
        super().__init__(game, user_side)
        self.attempts = 0  # Compteur d'essais pour le coup actuel
        self.max_attempts = 5  # Nombre maximum d'essais autorisés (5 au lieu de 3)
        self.last_submitted_move = None  # Dernier coup soumis

    def submit_move(self, move):
        """
        Gère la soumission d'un coup avec plusieurs tentatives.
        Retourne le résultat après 5 essais ou si le coup correct est trouvé.
        """
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}

        # Stocker les meilleurs coups avant que le joueur ne joue
        current_position_best_moves = self.best_moves.copy()

        # Valider le format du coup
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
                'attempts_left': self.max_attempts - self.attempts,
                'attempt': self.attempts + 1
            }

        # Récupérer le coup correct pour la position actuelle
        correct_move = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move)
        current_comment = self.get_comment_for_current_move()
        
        # Convertir le coup soumis en objet chess.Move
        submitted_chess_move = self.board.parse_uci(validated_move)
        submitted_move_san = self.board.san(submitted_chess_move)
        is_correct = (submitted_chess_move == correct_move)
        is_pawn = self.is_pawn_move(correct_move_san)
        
        # Incrémenter le compteur d'essais
        self.attempts += 1
        self.last_submitted_move = validated_move
        
        # Si c'est le coup correct ou le dernier essai, procéder à l'évaluation
        if is_correct or self.attempts >= self.max_attempts:
            # Utiliser le dernier coup soumis si nous atteignons le nombre max d'essais
            move_to_evaluate = validated_move if is_correct else self.last_submitted_move
            
            # Calculer les points
            points, move_quality_message, checkmate_bonus = self.calculate_points(move_to_evaluate, correct_move)
            is_checkmate = checkmate_bonus > 0
            
            # Appliquer un multiplicateur de points basé sur le nombre d'essais utilisés
            if is_correct:
                # Bonus pour avoir trouvé le coup correct rapidement
                attempt_multiplier = (self.max_attempts - self.attempts + 1) / self.max_attempts
                points = round(points * attempt_multiplier)
                move_quality_message += f" (x{attempt_multiplier:.1f} pour l'avoir trouvé en {self.attempts} essai{'s' if self.attempts > 1 else ''})"
            
            # Mettre à jour le score
            self.score = round(self.score + points)
            
            # Jouer le coup correct sur l'échiquier pour avancer la partie
            self.board.push(correct_move)
            
            # Gérer le coup adverse
            opponent_move = None
            opponent_move_san = None
            opponent_comment = None
            
            # Traitement du coup adverse selon la couleur du joueur
            if self.user_side == 'white':
                if self.current_move_index < len(self.black_moves):
                    opponent_move = self.black_moves[self.current_move_index]
                    opponent_move_san = self.board.san(opponent_move)
                    opponent_comment = self.get_comment_for_opponent_move()
                    self.board.push(opponent_move)
                    save_board_fen(self.board)
                    self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))
                    self.last_opponent_move = opponent_move_san
            else:  # user_side == 'black'
                if (self.current_move_index + 1) < len(self.white_moves):
                    opponent_move = self.white_moves[self.current_move_index + 1]
                    opponent_move_san = self.board.san(opponent_move)
                    opponent_comment = self.get_comment_for_opponent_move()
                    self.board.push(opponent_move)
                    save_board_fen(self.board)
                    self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))
                    self.last_opponent_move = opponent_move_san
            
            # Passer au coup suivant et réinitialiser le compteur d'essais
            self.current_move_index += 1
            self.attempts = 0
            
            # Message d'indice pour les coups de pièces vs pions
            hint_message = ""
            if not is_correct:
                if is_pawn:
                    hint_message = "Pour les pions, entrez simplement la case d'arrivée (ex: e4)"
                else:
                    hint_message = "Pour les pièces, entrez la pièce et la case d'arrivée (ex: Nf3)"
            
            # Construire la réponse complète
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
                'best_moves': self.best_moves,
                'previous_position_best_moves': current_position_best_moves,
                'attempts_used': self.attempts,
                'attempts_left': 0  # Réinitialisation pour le prochain coup
            }
        else:
            # Ce n'est pas le coup correct et il reste des essais
            # En mode facile, on donne un indice supplémentaire après le 3ème essai
            hint = ""
            if self.attempts >= 3:
                if is_pawn:
                    hint = f" Indice: le coup correct implique un pion qui se déplace vers {correct_move_san[-2:]}."
                else:
                    piece = correct_move_san[0]
                    piece_names = {'K': 'Roi', 'Q': 'Dame', 'R': 'Tour', 'B': 'Fou', 'N': 'Cavalier'}
                    piece_name = piece_names.get(piece, "une pièce")
                    hint = f" Indice: le coup correct implique {piece_name}."
            
            return {
                'is_correct': False,
                'submitted_move': submitted_move_san,
                'board_fen': self.board.fen(),
                'score': self.score,
                'attempts_left': self.max_attempts - self.attempts,
                'attempt': self.attempts,
                'is_valid_format': True,
                'game_over': False,
                'is_player_turn': True,
                'last_opponent_move': self.last_opponent_move,
                'move_quality': f"Ce n'est pas le coup correct. Vous avez encore {self.max_attempts - self.attempts} essai{'s' if self.max_attempts - self.attempts > 1 else ''}.{hint}"
            }
            
    def calculate_points(self, submitted_move, correct_move):
        """Version modifiée avec des pénalités réduites pour le mode facile."""
        # Appeler la méthode parent pour le calcul de base
        points, move_quality_message, checkmate_bonus = super().calculate_points(submitted_move, correct_move)
        
        # Réduire les pénalités de moitié en mode facile
        if points < 0:
            points = points // 2
            move_quality_message += " (Pénalité réduite en mode facile)"
        
        # Bonus supplémentaire pour les bons coups en mode facile
        if points > 0:
            bonus = 3
            points += bonus
            move_quality_message += f" (Bonus mode facile: +{bonus})"
        
        return points, move_quality_message, checkmate_bonus