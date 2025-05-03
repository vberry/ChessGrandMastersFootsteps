import chess
import chess.pgn
import os
from app.utils.engine_utils import evaluate_move_strength, get_best_moves_from_fen, evaluate_played_move
from app.utils.utils import convertir_notation_francais_en_anglais
from app.utils.fen_utils import save_board_fen
from app.models.game_model import ChessGame
class ChessGameEasy(ChessGame):
    """Version à difficulté moyenne : le joueur a 5 essais pour deviner le coup correct."""
    
    def __init__(self, game, user_side, game_id=None, use_timer=False):
        super().__init__(game, user_side, game_id=game_id, use_timer=use_timer)
        self.attempts = 0
        self.max_attempts = 5
        self.last_submitted_move = None
        
    def submit_move(self, move):
        """
        Gère la soumission d'un coup avec plusieurs tentatives.
        On calcule et renvoie score_percentage seulement si le coup est correct
        ou si c'est le dernier essai.
        """
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'} 

        # Stocker l’état des meilleurs coups avant la soumission
        current_position_best_moves = self.best_moves.copy()

        # Stocker la position FEN actuelle avant de jouer le coup
        position_fen_before_move = self.board.fen()

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
                'attempts_left': self.max_attempts - self.attempts,
                'attempts_used': self.attempts,
                'game_over': False,
                'is_player_turn': True,
                'last_opponent_move': self.last_opponent_move
            }

        # Préparer la position courante
        correct_move = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move)
        current_comment = self.get_comment_for_current_move()
        submitted_move_obj = self.board.parse_uci(validated_move)
        submitted_move_san = self.board.san(submitted_move_obj)
        is_correct = (submitted_move_obj == correct_move)
        is_pawn = self.is_pawn_move(correct_move_san)

       # Évaluer le coup joué par le joueur avec Stockfish
        move_evaluation = evaluate_played_move(position_fen_before_move, validated_move)
        
        
        # Incrémenter le compteur d'essais
        self.attempts += 1
        self.last_submitted_move = validated_move
        print(self.attempts)

        if is_correct or self.attempts >= self.max_attempts:
            # Choix du coup à évaluer
            move_to_eval = validated_move if is_correct else self.last_submitted_move

            # Calcul des points et bonus
            points, move_quality_msg, checkmate_bonus = self.calculate_points(
                move_to_eval, correct_move
            )
            is_checkmate = (checkmate_bonus > 0)

            # Multiplicateur si coup correct en moins d’essais
            if is_correct:
                mult = (self.max_attempts - self.attempts + 1) / self.max_attempts
                points = round(points * mult)
                move_quality_msg += f" (x{mult:.1f} pour l'avoir trouvé en {self.attempts} essai{'s' if self.attempts>1 else ''})"

            # Mise à jour du score
            self.score = round(self.score + points)

            # Appliquer le coup correct pour faire avancer la partie
            self.board.push(correct_move)

            # Gérer le coup adverse
            opponent_move_san = None
            opponent_comment = None
            if self.user_side == 'white':
                if self.current_move_index < len(self.black_moves):
                    op = self.black_moves[self.current_move_index]
                    opponent_move_san = self.board.san(op)
                    opponent_comment = self.get_comment_for_opponent_move()
                    self.board.push(op)
            else:
                if self.current_move_index + 1 < len(self.white_moves):
                    op = self.white_moves[self.current_move_index + 1]
                    opponent_move_san = self.board.san(op)
                    opponent_comment = self.get_comment_for_opponent_move()
                    self.board.push(op)

            # Sauvegarde l'état du plateau dans un fichier FEN propre à cette partie
            fen_filename = f"{self.game_id}.fen" if self.game_id else "fichierFenAjour.fen"
            save_board_fen(self.board, filename=fen_filename)

            
            fen_path = os.path.join(os.getcwd(), "fen_saves", f"{self.game_id}.fen")
            self.best_moves = get_best_moves_from_fen(fen_path)
            self.last_opponent_move = opponent_move_san

            # Passer au coup suivant
            self.current_move_index += 1
            self.attempts = 0

            # Calcul du pourcentage de score **uniquement ici**
            self.score_percentage = round((self.score / self.max_score) * 100, 2)
            score_pct = self.score_percentage

            return {
                'is_correct': is_correct,
                'correct_move': correct_move_san,
                'opponent_move': opponent_move_san,
                'comment': current_comment,
                'opponent_comment': opponent_comment,
                'submitted_move': submitted_move_san,
                'move_quality': move_quality_msg,
                'points_earned': points,
                'is_checkmate': is_checkmate,
                'checkmate_bonus': checkmate_bonus,
                'score': self.score,
                'score_percentage': score_pct,
                'max_score': self.max_score,
                'board_fen': self.board.fen(),
                'game_over': self.current_move_index >= len(self.moves),
                'is_player_turn': True,
                'last_opponent_move': self.last_opponent_move,
                'is_pawn_move': is_pawn,
                'best_moves': self.best_moves,
                'previous_position_best_moves': current_position_best_moves,
                'attempts_used': self.attempts,
                'attempts_left': 0,
                'move_evaluation': move_evaluation,
                'is_last_chance': self.attempts == 0
            }

        # Branche "mauvais coup + essais restants" : on n'envoie PAS score_percentage
        else:
            return {
                'is_correct': False,
                'submitted_move': submitted_move_san,
                'move_quality': (
                    f"Ce n'est pas le coup correct. "
                    f"Vous avez encore {self.max_attempts - self.attempts} essai"
                    f"{'s' if self.max_attempts - self.attempts > 1 else ''}."
                ),
                'board_fen': self.board.fen(),
                'score': self.score,
                'attempts_used': self.attempts,
                'attempts_left': self.max_attempts - self.attempts,
                'is_valid_format': True,
                'game_over': False,
                'is_player_turn': True,
                'last_opponent_move': self.last_opponent_move,
                'move_evaluation': move_evaluation,
                'is_last_chance': self.attempts == 0
            }
