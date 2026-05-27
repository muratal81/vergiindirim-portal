"""Production WSGI entry point - Render/gunicorn icin.

Onemli: gunicorn 'pre-fork' modeli kullanir. Ana process db connection
acarsa, fork'lanan worker'lar bu connection'i paylasir ve PostgreSQL SSL
hatasi (decryption failed/bad record mac) verir. Bu sebeple seed sonrasi
engine'i dispose ediyoruz; her worker kendi connection'ini kuracak.
"""
from app import create_app
from models import db, seed_programs, seed_admin

app = create_app()

with app.app_context():
    db.create_all()
    seed_programs()
    seed_admin()
    db.session.remove()
    # Worker fork'tan once connection'i kapat (multi-worker SSL fix)
    db.engine.dispose()


if __name__ == "__main__":
    app.run()
