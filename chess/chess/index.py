import os
from modes.guessMove import load_pgn_games, get_game_from_file, replay_game


# Définir le dossier contenant les fichiers PGN
PGN_FOLDER = os.path.join(os.path.dirname(__file__), "dossierPgn")

# Charger les parties PGN disponibles
pgn_games = load_pgn_games(PGN_FOLDER)

if not pgn_games:
    print("Aucun fichier PGN trouvé dans le dossier.")
    exit()

print("\nParties disponibles :")
for i, game in enumerate(pgn_games):
    print(f"{i + 1}. {game['event']} - {game['white']} vs {game['black']} (Résultat: {game['result']})")

while True:
    try:
        choice = int(input("\nEntrez le numéro de la partie que vous voulez jouer : ")) - 1
        if 0 <= choice < len(pgn_games):
            selected_file = os.path.join(PGN_FOLDER, pgn_games[choice]["file"])
            break
        else:
            print("Numéro invalide, veuillez essayer encore.")
    except ValueError:
        print("Entrée invalide, veuillez entrer un numéro.")

game = get_game_from_file(selected_file)

if game is None:
    print("Le fichier PGN est vide ou corrompu.")
    exit()

# Afficher les informations du jeu
print("\nInformations sur la partie :")
print(f"Event: {game.headers['Event']}")
print(f"Site: {game.headers['Site']}")
print(f"Date: {game.headers['Date']}")
print(f"Round: {game.headers['Round']}")
print(f"White: {game.headers['White']}")
print(f"Black: {game.headers['Black']}")
print(f"Result: {game.headers['Result']}")

user_side = input("\nQuel joueur voulez-vous être ? (White ou Black) : ").strip().lower()
while user_side not in ["white", "black"]:
    user_side = input("Choix invalide. Veuillez entrer 'White' ou 'Black' : ").strip().lower()

# Rejouer la partie
replay_game(game, user_side)
