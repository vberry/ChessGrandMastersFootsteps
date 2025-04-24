from app.models.game_model import ChessGame
from app.views.game_view import display_board, show_score, show_move_quality

class GameController:
    """
        Contrôleur pour gérer une partie d'échecs.

        Cette classe gère les interactions entre le modèle de jeu d'échecs (ChessGame) et 
        les vues. Elle permet de commencer une partie, de gérer les mouvements des utilisateurs 
        et de mettre à jour l'affichage.
    """
     
    def __init__(self, pgn_file, user_side):
        """
            Initialise un contrôleur de jeu d'échecs.

            :param pgn_file: Le fichier PGN contenant les mouvements du jeu.
            :param user_side: Le côté de l'utilisateur ('white' ou 'black').
        """
        self.chess_game = ChessGame(pgn_file, user_side)

    def start_game(self):
        """
            Démarre la partie en affichant le plateau de jeu initial.

            Cette méthode affiche l'état initial du plateau de jeu à l'aide de la fonction 
            `display_board` provenant de la vue.
        """
        display_board(self.chess_game.board.fen())

    def handle_user_move(self, move):
        """
            Gère le mouvement de l'utilisateur et met à jour l'affichage.

            :param move: Le mouvement de l'utilisateur au format standard (ex : 'e2e4').

            Cette méthode soumet un mouvement à la logique du jeu et met à jour l'affichage
            en fonction du résultat. Si le mouvement est valide, elle affiche le nouveau 
            plateau, le score et la qualité du mouvement. Sinon, elle affiche un message d'erreur.
        """
        result = self.chess_game.submit_move(move)
        if 'error' in result:
            print(f"Erreur : {result['error']}")
        else:
            display_board(result['board_fen'])
            show_score(result['score'])
            show_move_quality(result['move_quality'])
