"""Production WSGI entry point - Render/gunicorn icin."""
from app import create_app
from models import db, seed_programs, seed_admin

app = create_app()

with app.app_context():
    db.create_all()
    seed_programs()
    seed_admin()

if __name__ == "__main__":
    app.run()
