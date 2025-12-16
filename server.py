import os
from pathlib import Path
from flask import Flask, render_template
from dotenv import load_dotenv

from controllers.recommend_controller import recommend_bp
from models.database import init_db

# Load biến môi trường từ file .env
load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="views/templates", static_folder="views/static")
    app.register_blueprint(recommend_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app


# Khởi tạo database và tạo app instance cho gunicorn
print("Khởi tạo database...")
init_db()
print("Database đã sẵn sàng!")

# Tạo app instance ở module level để gunicorn có thể tìm thấy
app = create_app()


def main():
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)


if __name__ == "__main__":
    main()
