from app import create_app

# Crée l'application Flask
app = create_app()

if __name__ == "__main__":
    """
        Lancer l'application Flask en mode développement.

        Ce bloc de code est exécuté si ce fichier est lancé directement (pas importé comme module).
        Il démarre le serveur Flask sur l'adresse http://127.0.0.1:5000/ avec le mode debug activé.

        Exemple d'exécution :
            python run.py
    """
    print("🔄 Serveur Flask démarré sur http://127.0.0.1:5000/")
    # Démarre le serveur Flask avec le mode debug
    app.run(debug=True)
