import os
from pathlib import Path
from flask import Flask, render_template

from controllers.recommend_controller import recommend_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.register_blueprint(recommend_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


def main():
    app = create_app()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
