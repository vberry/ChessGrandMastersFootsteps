import chess

board = chess.Board()

# Exemple de coups
moves = [chess.Move.from_uci("e2e4"),  # Pion
         chess.Move.from_uci("g1f3")]  # Cavalier

for move in moves:
    # Vérifier si la pièce déplacée est un pion
    if board.piece_at(move.from_square).piece_type == chess.PAWN:
        print(move.uci())  # Notation normale pour les pions
    else:
        print(board.san(move))  # Notation SAN pour les autres pièces

    # Appliquer le coup pour mettre à jour l'échiquier
    board.push(move)
