"""Production WSGI entry point - Render/gunicorn icin.

Onemli: gunicorn 'pre-fork' modeli kullanir. Ana process db connection
acarsa, fork'lanan worker'lar bu connection'i paylasir ve PostgreSQL SSL
hatasi (decryption failed/bad record mac) verir. Bu sebeple seed sonrasi
engine'i dispose ediyoruz; her worker kendi connection'ini kuracak.
"""
from app import create_app
from models import (db, seed_programs, seed_admin, sync_admin_sifre, fix_legacy_texts)

app = create_app()

with app.app_context():
    db.create_all()           # Yeni tablolar (licenses, collab_requests, contact_messages) olusur
    seed_programs()           # Ilk acilis program kayitlari
    seed_admin()              # Admin yoksa olustur
    sync_admin_sifre()        # Mevcut admin sifresini guncel degerle esitle
    fix_legacy_texts()        # Eski 'Tam Tasdik' metinlerini guncelle
    db.session.remove()
    # Worker fork'tan once connection'i kapat (multi-worker SSL fix)
    db.engine.dispose()


if __name__ == "__main__":
    app.run()
