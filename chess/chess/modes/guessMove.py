import os
import chess
import chess.pgn
import chess.engine
from stockfish import Stockfish

# Chemin vers Stockfish (vérifie qu'il est bien installé à cet emplacement)
STOCKFISH_PATH = "/usr/games/stockfish"

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

def get_best_moves_from_fen(fen_file_path, num_top_moves=3, num_total_moves=10):
    """
    Analyse une position FEN avec Stockfish et retourne les meilleurs coups avec leurs évaluations.
    num_top_moves: nombre de coups à retourner pour les suggestions
    num_total_moves: nombre total de coups à analyser pour l'évaluation
    """
    try:
        with open(fen_file_path, "r") as f:
            fen = f.read().strip()
            
        stockfish = Stockfish(STOCKFISH_PATH)
        stockfish.set_fen_position(fen)
        stockfish.set_depth(15)
        
        board = chess.Board(fen)
        all_moves_info = stockfish.get_top_moves(num_total_moves)
        
        best_moves = []
        for move in all_moves_info:
            move_uci = move["Move"]
            try:
                chess_move = chess.Move.from_uci(move_uci)
                if chess_move in board.legal_moves:
                    score = move.get("Centipawn")
                    mate = move.get("Mate")
                    
                    if mate is not None:
                        evaluation = {"type": "mate", "value": mate}
                        display_score = f"M{mate}"
                    else:
                        evaluation = {"type": "cp", "value": score}
                        # Affichage sans arrondi du score
                        display_score = f"{score/100}"
                    
                    move_info = {
                        "uci": move_uci,
                        "evaluation": evaluation,
                        "display_score": display_score,
                        "san": board.san(chess_move)
                    }
                    
                    best_moves.append(move_info)
            except ValueError:
                continue

        # N'afficher que les num_top_moves meilleurs coups
        print("🔍 Meilleurs coups proposés par Stockfish :")
        for i in range(min(num_top_moves, len(best_moves))):
            move = best_moves[i]
            print(f"➡ {move['uci']} ({move['san']}) : {move['display_score']}")
        
        # Calculer la force relative par rapport au meilleur coup
        if best_moves:
            first_eval = best_moves[0]["evaluation"]
            if first_eval["type"] == "cp":
                base_score = first_eval["value"]
                for move in best_moves:
                    if move["evaluation"]["type"] == "cp":
                        diff = abs(move["evaluation"]["value"] - base_score)
                        # Une différence de 100 centipawns (1 pawn) = 50% de force relative
                        move["relative_strength"] = max(0, 100 - (diff/2))
                    else:
                        move["relative_strength"] = 100 if move["evaluation"]["value"] > 0 else 0
            else:
                for move in best_moves:
                    if move["evaluation"]["type"] == "mate":
                        move["relative_strength"] = 100 - (abs(move["evaluation"]["value"]) - 1) * 10
                    else:
                        move["relative_strength"] = 50
                        
        return best_moves

    except Exception as e:
        print(f"Erreur lors de l'analyse Stockfish : {e}")
        return []

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
        
        self.save_board_fen()
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
            # file_path = os.path.expanduser("~/fichierFenAjour.fen")  # Sauvegarde dans le dossier personnel de l'utilisateur
            
            with open(file_path, "w") as f:
                f.write(self.board.fen())  # Écrit la FEN actuelle
            print(f"FEN sauvegardée : {file_path}")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde FEN : {e}")

    def submit_move(self, move):
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

        is_correct = False
        if is_pawn:
            correct_uci = correct_move.uci()
            is_correct = submitted_move == correct_uci
            submitted_move_san = self.board.san(self.board.parse_uci(submitted_move))
            correct_move_display = correct_move_san
        else:
            correct_san = correct_move_san.lower().replace('x', '').replace('+', '').replace('#', '')
            is_correct = (submitted_move == correct_san or submitted_move == correct_move.uci())
            submitted_move_san = self.board.san(self.board.parse_uci(submitted_move))
            correct_move_display = correct_san

        points = 0
        move_quality_message = ""
        checkmate_bonus = 0

        # Vérifier si le coup soumis est un échec et mat
        temp_board = chess.Board(self.board.fen())
        submitted_chess_move = self.board.parse_uci(submitted_move)
        temp_board.push(submitted_chess_move)
        is_checkmate = temp_board.is_checkmate()
        
        # Réinitialiser le board temporaire
        temp_board = chess.Board(self.board.fen())
        
        submitted_uci = self.board.parse_uci(submitted_move).uci()
        correct_uci = correct_move.uci()
        
        # Trouver l'analyse du coup soumis et du coup correct
        submitted_move_analysis = None
        correct_move_analysis = None
        correct_move_rank = -1
        submitted_move_rank = -1

        for i, move in enumerate(self.best_moves):
            if move["uci"] == submitted_uci:
                submitted_move_analysis = move
                submitted_move_rank = i
            if move["uci"] == correct_uci:
                correct_move_analysis = move
                correct_move_rank = i

        # Attribution des points
        if is_correct:
            if correct_move_rank != -1 and correct_move_rank < 3:  # Coup du maître dans le top 3
                points = 20
                move_quality_message = f"Excellent ! C'est le coup historique et il est dans les 3 meilleurs coups. (+20 points)"
            elif correct_move_analysis:  # Coup du maître analysé par Stockfish
                relative_strength = correct_move_analysis["relative_strength"]
                if relative_strength >= 90:
                    points = 20
                    move_quality_message = f"Excellent ! C'est le coup historique et il est très fort ! (+20 points)"
                elif relative_strength >= 70:
                    points = 10
                    move_quality_message = f"Bien ! C'est le coup historique et c'est un bon coup. (+10 points)"
                else:
                    points = 0
                    move_quality_message = f"C'est le coup historique, mais il y avait mieux selon Stockfish. (+0 points)"
            else:  # Si le coup du maître n'est pas dans les analyses
                points = 0
                move_quality_message = f"C'est le coup historique, mais il ne fait pas partie des meilleurs coups connus. (+0 points)"
        elif submitted_move_analysis:  # Coup autre que le coup du maître
            if submitted_move_rank == 0:
                points = 15
            elif submitted_move_rank == 1:
                points = 10
            elif submitted_move_rank == 2:
                points = 5
            elif submitted_move_analysis["relative_strength"] >= 80:
                points = 5
            elif submitted_move_analysis["relative_strength"] >= 60:
                points = 0
            else:
                points = -10
            move_quality_message = f"{submitted_move_analysis['san']} ({submitted_move_analysis['display_score']}) est classé #{submitted_move_rank+1} selon Stockfish. (+{points} points)"
        else:
            points = -10
            move_quality_message = "Ce coup n'est pas dans les coups recommandés par Stockfish. (-10 points)"

        # Ajouter le bonus d'échec et mat si applicable
        if is_checkmate:
            checkmate_bonus = 20
            points += checkmate_bonus
            move_quality_message += f" ÉCHEC ET MAT ! (Bonus +{checkmate_bonus} points)"

        self.score = round(self.score + points)

        self.board.push(correct_move)
        
        opponent_move = None
        opponent_move_san = None
        opponent_comment = None
        
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
            'previous_position_best_moves': current_position_best_moves  # Coups alternatifs pour la position précédente
        }
