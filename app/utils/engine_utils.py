import chess.engine
from stockfish import Stockfish

STOCKFISH_PATH = "/opt/homebrew/bin/stockfish"
STOCKFISH_PATH = "/usr/games/stockfish"

def evaluate_move_strength(board, move):
    """
    Évalue la force d'un coup avec Stockfish
    Retourne un dictionnaire avec l'évaluation du coup
    """
    temp_board = chess.Board(board.fen())
    temp_board.push(move)
    stockfish = Stockfish(STOCKFISH_PATH)
    stockfish.set_fen_position(temp_board.fen())
    stockfish.set_depth(15)
    
    # Obtenir l'évaluation de la position après le coup
    evaluation = stockfish.get_evaluation()
    
    return {
        "type": evaluation["type"],
        "value": evaluation["value"],
        "display_score": f"M{evaluation['value']}" if evaluation["type"] == "mate" else f"{evaluation['value']/100}"
    }

def get_best_moves_from_fen(fen_file_path, num_top_moves=3, num_total_moves=3):
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
