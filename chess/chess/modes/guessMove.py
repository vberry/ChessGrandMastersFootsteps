import os
import chess
import chess.pgn

def load_pgn_games(pgn_folder):
    """Charge les parties PGN depuis le dossier et retourne la liste des parties disponibles."""
    pgn_games = []
    for file in os.listdir(pgn_folder):
        if file.endswith(".pgn"):
            with open(os.path.join(pgn_folder, file)) as pgn:
                game = chess.pgn.read_game(pgn)
                if game:
                    pgn_games.append({
                        "event": game.headers.get("Event", "Inconnu"),
                        "white": game.headers.get("White", "Inconnu"),
                        "black": game.headers.get("Black", "Inconnu"),
                        "result": game.headers.get("Result", "Inconnu"),
                        "file": file
                    })
    return pgn_games

def get_game_from_file(file_path):
    """Lit un fichier PGN et retourne la partie de jeu correspondante."""
    with open(file_path) as pgn:
        game = chess.pgn.read_game(pgn)
        # Ajoutez ce print pour déboguer
        moves = list(game.mainline_moves())
        print(f"Moves loaded: {moves}")
        return game

class ChessGame:
    def __init__(self, game, user_side):
        self.board = game.board()
        self.all_moves = list(game.mainline_moves())
        self.user_side = user_side
        
        self.white_moves = self.all_moves[::2]
        self.black_moves = self.all_moves[1::2]
        
        self.moves = self.white_moves if user_side == 'white' else self.black_moves
        
        self.current_move_index = 0
        self.score = 0
        self.total_moves = len(self.moves)
        
        # print(f"Debug: Total moves: {len(self.all_moves)}")
        # print(f"Debug: White moves: {len(self.white_moves)}")
        # print(f"Debug: Black moves: {len(self.black_moves)}")
        # print(f"Debug: Selected moves for {user_side}: {self.moves}")

    def is_player_turn(self):
        return True 
    
    
    def get_game_state(self):
        return {
            
            'board_fen': self.board.fen(),
            
            'user_side': self.user_side,
            'current_move_index': self.current_move_index,
            'score': self.score,
            'total_moves': self.total_moves,
            'is_player_turn': True  
    }

    def submit_move(self, move):
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}
        
        # Pour les noirs, jouer d'abord le coup des blancs
        if self.user_side == 'black' and self.current_move_index < len(self.white_moves):
            self.board.push(self.white_moves[self.current_move_index])
        
        correct_move_uci = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move_uci)
        
        submitted_move = move.strip().lower()
        correct_san = correct_move_san.lower()
        correct_uci = str(correct_move_uci).lower()
        
        if self.user_side == 'black':
            # Simplifier seulement en retirant les caractères spéciaux
            correct_san = correct_san.replace('x', '').replace('+', '')
        
        is_correct = (
            submitted_move == correct_san or
            submitted_move == correct_uci or
            submitted_move == correct_san.replace('x', '')
        )
        
        if is_correct:
            self.score += 1
        
        # Pour les blancs, appliquer le coup directement
        if self.user_side == 'white':
            self.board.push(correct_move_uci)
            # Jouer le coup des noirs après
            if self.current_move_index < len(self.black_moves):
                self.board.push(self.black_moves[self.current_move_index])
        else:
            # Pour les noirs, le coup des blancs est déjà joué, appliquer le coup des noirs
            self.board.push(correct_move_uci)
        
        self.current_move_index += 1
        
        return {
            'is_correct': is_correct,
            'correct_move': submitted_move if is_correct else correct_san,
            'board_fen': self.board.fen(),
            'score': self.score,
            'game_over': self.current_move_index >= len(self.moves),
            'is_player_turn': True
        }

    def generate_board_html(board):
        """Génère une représentation HTML du plateau d'échecs avec des pièces Unicode."""
        pieces_map = {
            chess.PAWN: {'w': '♙', 'b': '♟'},
            chess.KNIGHT: {'w': '♘', 'b': '♞'},
            chess.BISHOP: {'w': '♗', 'b': '♝'},
            chess.ROOK: {'w': '♖', 'b': '♜'},
            chess.QUEEN: {'w': '♕', 'b': '♛'},
            chess.KING: {'w': '♔', 'b': '♚'}
        }
        
        board_html = '<table class="chessboard">'
        for rank in range(7, -1, -1):  # Parcours les rangées de 8 à 1
            board_html += '<tr>'
            for file in range(8):  # Parcours les colonnes de a à h
                square = chess.square(file, rank)
                piece = board.piece_at(square)
                color_class = 'white-square' if (rank + file) % 2 == 0 else 'black-square'
                piece_symbol = pieces_map.get(piece.piece_type, {}).get(piece.color, '') if piece else ''
                board_html += f'<td class="{color_class}">{piece_symbol}</td>'
            board_html += '</tr>'
        board_html += '</table>'
        
        return board_html