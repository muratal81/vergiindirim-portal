"""Uygulama konfigurasyonu - hem yerel hem production (Render) destekler."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = BASE_DIR / "downloads"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)


def _resolve_database_url() -> str:
    """Production'da DATABASE_URL env variable kullanilir (Render PostgreSQL),
    yerel calismada SQLite kullanilir."""
    url = os.environ.get("DATABASE_URL", "").strip()
    if url:
        # Render bazen 'postgres://' verir; SQLAlchemy 2 'postgresql://' bekler
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url
    return f"sqlite:///{DATA_DIR / 'portal.db'}"


class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET", "vergiindirim-degistir-prod-icin-mutlaka")
    SQLALCHEMY_DATABASE_URI = _resolve_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024

    # PostgreSQL SSL baglanti stabilitesi (Render multi-worker icin kritik)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,      # Her query oncesi connection ping (bad record mac fix)
        "pool_recycle": 280,        # 280 saniyede connection'i yenile
        "pool_size": 5,
        "max_overflow": 10,
    }

    # Production'da behind-proxy oldugu icin secure cookies'ler aktif
    SESSION_COOKIE_SECURE = os.environ.get("RENDER", "") != ""
    REMEMBER_COOKIE_SECURE = os.environ.get("RENDER", "") != ""
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = "https" if os.environ.get("RENDER", "") != "" else "http"

    # Site bilgileri (sablonlarda kullanilir)
    SITE_ADI = os.environ.get("SITE_ADI", "Vergi İndirim Programları")
    SITE_KISA = os.environ.get("SITE_KISA", "Vergi İndirim")
    SITE_SLOGAN = os.environ.get(
        "SITE_SLOGAN",
        "Vergi Uzmanlığı ile Yazılım Teknolojisi Bir Arada"
    )
    SITE_TELEFON = os.environ.get("SITE_TELEFON", "0532 177 47 95")
    SITE_EMAIL = os.environ.get("SITE_EMAIL", "info@vergiindirim.com.tr")
    SITE_ADRES = os.environ.get(
        "SITE_ADRES",
        "Kızılırmak Mah. Muhsin Yazıcıoğlu Cd. No: 29/19 Çankaya / Ankara"
    )
    SITE_SAHIBI = os.environ.get("SITE_SAHIBI", "Murat Alan")
    SITE_DOMAIN = os.environ.get("SITE_DOMAIN", "vergiindirim.com.tr")
