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
        
        # Si on joue les noirs, jouer d'abord le coup des blancs
        if self.user_side == 'black':
            white_move = self.white_moves[self.current_move_index]
            self.last_opponent_move = self.board.san(white_move)
            self.board.push(white_move)
        
        correct_move_uci = self.moves[self.current_move_index]
        correct_move_san = self.board.san(correct_move_uci)
        
        # Déterminer si c'est un coup de pion
        is_pawn_move = True
        if correct_move_san[0].isupper() or 'O' in correct_move_san:  # Si le coup commence par une majuscule ou est un roque
            is_pawn_move = False
        
        submitted_move = move.strip().lower()
        correct_san = correct_move_san.lower()
        correct_uci = str(correct_move_uci).lower()
        
        # Simplifier la notation pour les non-pions
        if not is_pawn_move:
            if self.user_side == 'black':
                correct_san = correct_san.replace('x', '').replace('+', '')
        
        # Pour les pions, on exige la notation UCI (ex: e2e4)
        is_correct = False
        if is_pawn_move:
            is_correct = submitted_move == correct_uci
            correct_move_display = correct_uci  # Pour l'affichage en cas d'erreur
        else:
            is_correct = (
                submitted_move == correct_san or
                submitted_move == correct_san.replace('x', '') or
                submitted_move == correct_uci
            )
            correct_move_display = correct_san
        
        if is_correct:
            self.score += 1
        
        # Jouer le coup
        if self.user_side == 'white':
            self.board.push(correct_move_uci)
            if self.current_move_index < len(self.black_moves):
                black_move = self.black_moves[self.current_move_index]
                self.last_opponent_move = self.board.san(black_move)
                self.board.push(black_move)
        else:
            self.board.push(correct_move_uci)
            
        self.current_move_index += 1
        
        # Préparer le message d'aide
        hint_message = ""
        if not is_correct:
            if is_pawn_move:
                hint_message = "Pour les pions, entrez la case de départ et d'arrivée (ex: e2e4)"
        
        return {
            'is_correct': is_correct,
            'correct_move': submitted_move if is_correct else correct_move_display,
            'board_fen': self.board.fen(),
            'score': self.score,
            'game_over': self.current_move_index >= len(self.moves),
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move,
            'hint': hint_message,
            'is_pawn_move': is_pawn_move
        }