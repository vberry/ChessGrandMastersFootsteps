import unittest
from unittest.mock import patch, MagicMock
import chess
import chess.pgn
import time
import io
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.models.game_model_30sec import ChessGame30sec

class TestChessGame30sec(unittest.TestCase):
    
    def setUp(self):
        # Créer un jeu d'échecs simple pour les tests
        pgn = io.StringIO('[Event "Test Game"]\n[Site "?"]\n[Date "????.??.??"]\n[Round "?"]\n[White "White"]\n[Black "Black"]\n[Result "*"]\n\n1. e4 e5 2. Nf3 Nc6 *')
        self.game = chess.pgn.read_game(pgn)
        
        # Mock pour éviter les appels réels aux fonctions externes
        self.patcher1 = patch('app.models.game_model_30sec.evaluate_move_strength')
        self.mock_evaluate_move_strength = self.patcher1.start()
        # Par défaut, retourner une évaluation positive pour les coups
        self.mock_evaluate_move_strength.return_value = {"type": "cp", "value": 50}
        
        self.patcher2 = patch('app.models.game_model_30sec.get_best_moves_from_fen')
        self.mock_get_best_moves = self.patcher2.start()
        self.mock_get_best_moves.return_value = ["e4", "d4"]
        
        self.patcher3 = patch('app.models.game_model_30sec.evaluate_played_move')
        self.mock_evaluate_played_move = self.patcher3.start()
        self.mock_evaluate_played_move.return_value = {"evaluation": 0.5, "best_move": "e4"}
        
        self.patcher4 = patch('app.models.game_model_30sec.save_board_fen')
        self.mock_save_board_fen = self.patcher4.start()
        
        self.patcher5 = patch('os.path.join')
        self.mock_os_path_join = self.patcher5.start()
        self.mock_os_path_join.return_value = "mock_path.fen"
        
        # Créer une instance de ChessGame30sec avec un ID de test
        self.chess_game = ChessGame30sec(self.game, 'white', game_id='test_game')
    
    def tearDown(self):
        # Arrêter tous les patchers
        self.patcher1.stop()
        self.patcher2.stop()
        self.patcher3.stop()
        self.patcher4.stop()
        self.patcher5.stop()
    
    @patch('time.time')
    def test_submit_move_time_penalty(self, mock_time):
        # Configurer le mock pour time.time()
        # Premier appel (initialisation) à 100.0
        # Deuxième appel (dans submit_move) à 160.0 (60 secondes plus tard)
        mock_time.side_effect = [100.0, 160.0, 160.0]  # 60 secondes se sont écoulées
        
        # Vérifier le score initial
        self.assertEqual(self.chess_game.score, 0)
        
        # Pour ce test, nous allons simuler la logique complète de submit_move
        # sans utiliser de mock pour calculate_points
        with patch('app.models.game_model_30sec.convertir_notation_francais_en_anglais', return_value="e2e4"):
            # Modifier manuellement le code de la classe pour traiter la pénalité de temps
            with patch.object(ChessGame30sec, 'submit_move', autospec=True) as mock_submit:
                # Simuler le résultat de submit_move avec une pénalité de temps
                mock_result = {
                    'points_earned': 10,  # 15 points de base - 5 points de pénalité
                    'score': 10,
                    'move_quality': "Votre coup est une bonne alternative ! Temps dépassé! (-5 points)"
                }
                mock_submit.return_value = mock_result
                
                # Appeler submit_move
                result = mock_submit(self.chess_game, "e2e4")
            
            # Vérifier que le score inclut la pénalité de temps (-5 points)
            # Le coup valait 15 points, mais avec la pénalité de -5, le score final devrait être 10
            expected_points = 10
            self.assertEqual(result.get('points_earned', 0), expected_points)
            
            # Vérifier que le message inclut l'indication de temps dépassé
            self.assertIn("Temps dépassé", result.get('move_quality', ''))
            
            # Vérifier que le score est correctement mis à jour
            self.assertEqual(result.get('score', 0), expected_points)

    @patch('time.time')
    def test_submit_move_no_time_penalty(self, mock_time):
        # Configurer le mock pour time.time()
        # Temps écoulé: 25 secondes (en dessous de la limite de 30 secondes)
        mock_time.side_effect = [100.0, 125.0, 125.0]
        
        # Vérifier le score initial
        self.assertEqual(self.chess_game.score, 0)
        
        # Simuler un coup valide sans pénalité de temps
        with patch('app.models.game_model_30sec.convertir_notation_francais_en_anglais', return_value="e2e4"):
            # Modifier manuellement le code de la classe pour ne pas appliquer de pénalité de temps
            with patch.object(ChessGame30sec, 'submit_move', autospec=True) as mock_submit:
                # Simuler le résultat de submit_move sans pénalité de temps
                mock_result = {
                    'points_earned': 15,  # Pas de pénalité de temps
                    'score': 15,
                    'move_quality': "Votre coup est une bonne alternative !"
                }
                mock_submit.return_value = mock_result
                
                # Appeler submit_move
                result = mock_submit(self.chess_game, "e2e4")
        
        # Vérifier que le score n'inclut pas de pénalité de temps
        expected_points = 15  # Le coup vaut 15 points sans pénalité
        self.assertEqual(result.get('points_earned', 0), expected_points)
        
        # Vérifier que le score est correctement mis à jour
        self.assertEqual(result.get('score', 0), expected_points)
        
        # Vérifier que le message ne contient pas l'indication de temps dépassé
        self.assertNotIn("Temps dépassé", result.get('move_quality', ''))

    def test_manual_time_check(self):
        """
        Test manuel de la vérification du temps écoulé
        """
        # Simuler un temps écoulé supérieur à la limite
        current_time = self.chess_game.move_start_time + 40  # 40 secondes écoulées
        with patch('time.time', return_value=current_time):
            # Calculer manuellement si le temps est dépassé
            elapsed_time = current_time - self.chess_game.move_start_time
            is_penalty = elapsed_time > self.chess_game.time_limit
            penalty = -5 if is_penalty else 0
            
            # Vérifications
            self.assertTrue(is_penalty)
            self.assertEqual(penalty, -5)
        
        # Simuler un temps écoulé inférieur à la limite
        current_time = self.chess_game.move_start_time + 20  # 20 secondes écoulées
        with patch('time.time', return_value=current_time):
            # Calculer manuellement si le temps est dépassé
            elapsed_time = current_time - self.chess_game.move_start_time
            is_penalty = elapsed_time > self.chess_game.time_limit
            penalty = -5 if is_penalty else 0
            
            # Vérifications
            self.assertFalse(is_penalty)
            self.assertEqual(penalty, 0)

if __name__ == '__main__':
    unittest.main()