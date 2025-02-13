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
    
def convertir_notation_francais_en_anglais(move_fr):
        """
        Convertit une notation SAN française (ex: Cf3) en notation SAN anglaise (ex: Nf3).
        """
        conversion_pieces = {
            "C": "N",  # Cavalier -> Knight
            "F": "B",  # Fou -> Bishop
            "T": "R",  # Tour -> Rook
            "D": "Q",  # Dame -> Queen
            "R": "K",  # Roi -> King
        }
        
        # Remplace les lettres françaises par les lettres anglaises
        move_en = move_fr
        for fr, en in conversion_pieces.items():
            move_en = move_en.replace(fr, en)

        return move_en

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
        
        if user_side == 'black' and len(self.white_moves) > 0:
            first_move = self.white_moves[0]
            self.last_opponent_move = self.board.san(first_move)
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
    
    def is_pawn_move(self, move_san):
        """Détermine si un coup est un coup de pion."""
        return not (move_san[0].isupper() or 'O' in move_san)
    

    def validate_input(self, move):
        """Valide le format de l'entrée utilisateur."""
        move = move.strip().lower()
        
        # Cas spécial pour le roque
        if move in ['o-o', 'o-o-o']:
            return True, move, None
        
        # Format pour les pièces: [pièce][colonne][ligne] ex: nf3, qe4
        piece_move_pattern = "^[nbrqk][a-h][1-8]$"
        
        # Format pour les pions: [colonne1][ligne1][colonne2][ligne2] ex: e2e4
        pawn_move_pattern = "^[a-h][1-8][a-h][1-8]$"
        
        import re
        if re.match(piece_move_pattern, move):
            return True, move, None
        elif re.match(pawn_move_pattern, move):
            return True, move, None
        else:
            return False, None, "Format incorrect pour un coup de pion utilisez le format 'e2e4'; pour un coup de pièce utilisez le format 'Nf3' ou 'Qe4'"
 
    
    def submit_move(self, move):
        if self.current_move_index >= len(self.moves):
            return {'error': 'La partie est terminée'}
        
        # Valider le format de l'entrée
        is_valid, validated_move, error_message = self.validate_input(convertir_notation_francais_en_anglais(move.strip()).lower())
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
        
        is_pawn = self.is_pawn_move(correct_move_san)
        
        submitted_move = validated_move

        is_correct = False
        
        if is_pawn:
            correct_uci = correct_move.uci()
            is_correct = submitted_move == correct_uci
            correct_move_display = correct_uci
        else:
            correct_san = correct_move_san.lower().replace('x', '').replace('+', '')
            is_correct = (submitted_move == correct_san or 
                         submitted_move == correct_move.uci())
            correct_move_display = correct_san
        
        if is_correct:
            self.score += 1
        
        self.board.push(correct_move)
        
        opponent_move = None
        if self.user_side == 'white' and self.current_move_index < len(self.black_moves):
            opponent_move = self.black_moves[self.current_move_index]
        elif self.user_side == 'black' and (self.current_move_index + 1) < len(self.white_moves):
            opponent_move = self.white_moves[self.current_move_index + 1]
            
        if opponent_move:
            self.last_opponent_move = self.board.san(opponent_move)
            self.board.push(opponent_move)
            
        self.current_move_index += 1
        
        hint_message = ""
        if not is_correct:
            if is_pawn:
                hint_message = "Pour les pions, entrez la case de départ et d'arrivée (ex: e2e4)"
            else:
                hint_message = "Pour les pièces, entrez la pièce et la case d'arrivée (ex: Nf3)"
        
        return {
            'is_correct': is_correct,
            'correct_move': correct_move_display,
            'board_fen': self.board.fen(),
            'score': self.score,
            'game_over': self.current_move_index >= len(self.moves),
            'is_player_turn': True,
            'last_opponent_move': self.last_opponent_move,
            'hint': hint_message,
            'is_pawn_move': is_pawn,
            'is_valid_format': True
        }