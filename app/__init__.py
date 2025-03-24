from flask import Flask

def create_app():
    app = Flask(__name__)

    # Importer et enregistrer le Blueprint game_bp
    from app.routes.game_routes import game_bp
    app.register_blueprint(game_bp, url_prefix="")

    return app
