import os
import chess
import chess.pgn
import chess.engine
from stockfish import Stockfish
from modes.guessMove import load_pgn_games, get_game_from_file, convertir_notation_francais_en_anglais, evaluate_move_strength, get_best_moves_from_fen

# Chemin vers Stockfish
STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"

class ChessGameEasy:
    def __init__(self, game, user_side):
        self.board = game.board()
        self.game = game
        self.all_moves = list(game.mainline_moves())
        self.user_side = user_side
        
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
        self.remaining_attempts = 3
        
        if user_side == 'black' and len(self.white_moves) > 0:
            first_move = self.white_moves[0]
            self.last_opponent_move = self.board.san(first_move)
            self.board.push(first_move)
        else:
            self.last_opponent_move = None
        
        self.save_board_fen()
        self.best_moves = get_best_moves_from_fen(os.path.join(os.getcwd(), "fichierFenAjour.fen"))

    def submit_move(self, move):
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}

        is_valid, validated_move, error_message = self.validate_input(
            convertir_notation_francais_en_anglais(move.strip()).lower()
        )
        
        if not is_valid:
            return {
                'error': error_message,
                'remaining_attempts': self.remaining_attempts
            }

        correct_move = self.moves[self.current_move_index]
        is_correct = chess.Move.from_uci(validated_move) == correct_move

        if is_correct:
            self.score += 10
            self.board.push(correct_move)
            self.current_move_index += 1
            self.remaining_attempts = 3
            return {'is_correct': True, 'score': self.score}
        else:
            self.remaining_attempts -= 1
            if self.remaining_attempts == 0:
                self.board.push(correct_move)
                self.current_move_index += 1
                self.remaining_attempts = 3
                return {'is_correct': False, 'correct_move': self.board.san(correct_move), 'remaining_attempts': self.remaining_attempts}
            return {'is_correct': False, 'remaining_attempts': self.remaining_attempts}
