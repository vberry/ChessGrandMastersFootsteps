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
        
        # Si le joueur est noir, jouer automatiquement le premier coup des blancs
        if user_side == 'black' and len(self.white_moves) > 0:
            first_move = self.white_moves[0]
            # D'abord obtenir la notation SAN
            self.last_opponent_move = self.board.san(first_move)
            # Puis jouer le coup
            self.board.push(first_move)
        else:
            self.last_opponent_move = None
    
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
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}
        
        # Si on joue les noirs
        if self.user_side == 'black':
            # Obtenir le coup des noirs à deviner
            black_move_uci = self.moves[self.current_move_index]
            black_move_san = self.board.san(black_move_uci)
            
            # Vérifier si le coup soumis est correct
            submitted_move = move.strip().lower()
            correct_san = black_move_san.lower().replace('x', '').replace('+', '')
            correct_uci = str(black_move_uci).lower()
            
            is_correct = (
                submitted_move == correct_san or
                submitted_move == correct_uci or
                submitted_move == correct_san.replace('x', '')
            )
            
            if is_correct:
                self.score += 1
            
            # Jouer le coup noir
            self.board.push(black_move_uci)
            
            # Si ce n'est pas le dernier coup, jouer le prochain coup blanc
            self.current_move_index += 1
            if self.current_move_index < len(self.moves):
                next_white_move = self.white_moves[self.current_move_index]
                # Sauvegarder la notation SAN avant de jouer le coup
                self.last_opponent_move = self.board.san(next_white_move)
                self.board.push(next_white_move)
            
        # Si on joue les blancs
        else:
            white_move_uci = self.moves[self.current_move_index]
            white_move_san = self.board.san(white_move_uci)
            
            submitted_move = move.strip().lower()
            correct_san = white_move_san.lower()
            correct_uci = str(white_move_uci).lower()
            
            is_correct = (
                submitted_move == correct_san or
                submitted_move == correct_uci or
                submitted_move == correct_san.replace('x', '')
            )
            
            if is_correct:
                self.score += 1
            
            # Jouer le coup blanc
            self.board.push(white_move_uci)
            
            # Jouer le coup noir correspondant
            if self.current_move_index < len(self.black_moves):
                black_move = self.black_moves[self.current_move_index]
                self.last_opponent_move = self.board.san(black_move)
                self.board.push(black_move)
            
            self.current_move_index += 1
        
        return {
            'is_correct': is_correct,
            'correct_move': submitted_move if is_correct else correct_san,
            'board_fen': self.board.fen(),
            'score': self.score,
            'game_over': self.current_move_index >= len(self.moves),
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move
        }