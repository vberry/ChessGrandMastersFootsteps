from app.models.game_model import ChessGame
from app.views.game_view import display_board, show_score, show_move_quality

class GameController:
    def __init__(self, pgn_file, user_side):
        self.chess_game = ChessGame(pgn_file, user_side)

    def start_game(self):
        display_board(self.chess_game.board.fen())

    def handle_user_move(self, move):
        result = self.chess_game.submit_move(move)
        if 'error' in result:
            print(f"Erreur : {result['error']}")
        else:
            display_board(result['board_fen'])
            show_score(result['score'])
            show_move_quality(result['move_quality'])
