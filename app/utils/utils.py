def convertir_notation_francais_en_anglais(move_fr):
    """Convertit une notation SAN française (ex: Cf3) en notation SAN anglaise (ex: Nf3)"""
    conversion_pieces = {"C": "N", "F": "B", "T": "R", "D": "Q", "R": "K"}
    for fr, en in conversion_pieces.items():
        move_fr = move_fr.replace(fr, en)
    return move_fr
