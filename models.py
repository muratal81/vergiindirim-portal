"""Veritabani modelleri."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Site kullanicisi (SMMM/YMM/normal kullanici)."""
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    sifre_hash = db.Column(db.String(256), nullable=False)
    ad_soyad = db.Column(db.String(120), nullable=False)
    unvan = db.Column(db.String(60), default="SMMM")  # SMMM, YMM, Diger
    telefon = db.Column(db.String(20))
    sirket = db.Column(db.String(200))
    rol = db.Column(db.String(20), default="user")  # user, admin
    kayit_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    son_giris = db.Column(db.DateTime)
    aktif = db.Column(db.Boolean, default=True)
    # Sifre sifirlama
    reset_token = db.Column(db.String(64), index=True)
    reset_expiry = db.Column(db.DateTime)

    indirmeler = db.relationship("Download", backref="user", lazy=True)
    siparisler = db.relationship("Order", backref="user", lazy=True)

    def sifre_belirle(self, sifre: str):
        self.sifre_hash = generate_password_hash(sifre)

    def sifre_kontrol(self, sifre: str) -> bool:
        return check_password_hash(self.sifre_hash, sifre)

    @property
    def is_admin(self) -> bool:
        return self.rol == "admin"


class Program(db.Model):
    """Sitede sunulan vergi/hesaplama programi."""
    __tablename__ = "programs"
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    ad = db.Column(db.String(200), nullable=False)
    kisa_aciklama = db.Column(db.String(300))
    aciklama = db.Column(db.Text)
    kategori = db.Column(db.String(60))  # KVK, GVK, Hesap İncelemeleri, KDV vb.
    mevzuat = db.Column(db.String(200))   # ornek: "KVK m.11/1-i"
    versiyon = db.Column(db.String(20), default="1.0")
    ucretsiz = db.Column(db.Boolean, default=True)
    fiyat = db.Column(db.Float, default=0.0)  # TL
    indirme_dosyasi = db.Column(db.String(200))  # downloads klasoru altindaki dosya adi
    durum = db.Column(db.String(20), default="aktif")  # aktif, gelistirme, pasif
    on_plana_cikar = db.Column(db.Boolean, default=False)  # anasayfada gosterilsin
    olusturma_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    indirme_sayisi = db.Column(db.Integer, default=0)

    ozellikler = db.relationship("ProgramOzellik", backref="program", lazy=True, cascade="all, delete-orphan")


class ProgramOzellik(db.Model):
    """Program detay sayfasinda listelenen ozellikler/bullet'lar."""
    __tablename__ = "program_ozellikler"
    id = db.Column(db.Integer, primary_key=True)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    metin = db.Column(db.String(300), nullable=False)
    sira = db.Column(db.Integer, default=0)


class Download(db.Model):
    """Indirme logu."""
    __tablename__ = "downloads"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    tarih = db.Column(db.DateTime, default=datetime.utcnow)
    ip = db.Column(db.String(45))


class Order(db.Model):
    """Ucretli program siparisi (ilerde odeme entegrasyonu icin)."""
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    tutar = db.Column(db.Float)
    durum = db.Column(db.String(20), default="bekliyor")  # bekliyor, odendi, iptal
    tarih = db.Column(db.DateTime, default=datetime.utcnow)


class License(db.Model):
    """Program lisansi - onay mekanizmasi + 1 yil gecerlilik.

    Akis: kullanici lisans talep eder (durum='bekliyor') -> admin onaylar
    (durum='aktif', baslangic=now, bitis=now+1yil, anahtar uretilir) ->
    kullanici programi indirir -> program acilista anahtari /api/lisans-dogrula
    ile kontrol eder. bitis gectiyse program calismaz."""
    __tablename__ = "licenses"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    program_id = db.Column(db.Integer, db.ForeignKey("programs.id"), nullable=False)
    anahtar = db.Column(db.String(40), unique=True, index=True)  # XXXX-XXXX-XXXX-XXXX
    durum = db.Column(db.String(20), default="bekliyor")  # bekliyor, aktif, suresi_doldu, iptal
    baslangic = db.Column(db.DateTime)
    bitis = db.Column(db.DateTime)
    talep_tarihi = db.Column(db.DateTime, default=datetime.utcnow)
    onaylayan = db.Column(db.String(120))   # admin email
    onay_tarihi = db.Column(db.DateTime)
    son_dogrulama = db.Column(db.DateTime)  # program en son ne zaman dogrulama yapti
    not_ = db.Column(db.String(300))

    user = db.relationship("User", backref="lisanslar")
    program = db.relationship("Program", backref="lisanslar")

    @property
    def gecerli_mi(self) -> bool:
        if self.durum != "aktif" or not self.bitis:
            return False
        return datetime.utcnow() <= self.bitis

    @property
    def kalan_gun(self) -> int:
        if not self.bitis:
            return 0
        delta = self.bitis - datetime.utcnow()
        return max(0, delta.days)


class CollabRequest(db.Model):
    """Ozel cozum / is birligi talebi (musteri kendi ihtiyacini anlatir)."""
    __tablename__ = "collab_requests"
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefon = db.Column(db.String(30))
    unvan = db.Column(db.String(60))      # SMMM, YMM, Mukellef, Diger
    sirket = db.Column(db.String(200))
    konu = db.Column(db.String(200))       # ihtiyac basligi
    detay = db.Column(db.Text)             # ihtiyac aciklamasi
    butce = db.Column(db.String(60))       # tahmini butce araligi
    durum = db.Column(db.String(20), default="yeni")  # yeni, gorusuldu, kapandi
    tarih = db.Column(db.DateTime, default=datetime.utcnow)


class ContactMessage(db.Model):
    """Iletisim formu mesaji."""
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    ad_soyad = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telefon = db.Column(db.String(30))
    mesaj = db.Column(db.Text)
    durum = db.Column(db.String(20), default="yeni")
    tarih = db.Column(db.DateTime, default=datetime.utcnow)


def seed_programs():
    """Ilk acilis ve sonraki deploylarda sabit program kayitlarini gunceller."""
    programlar = [
        {
            "slug": "tt-hesap-incelemeleri",
            "ad": "Hesap İncelemeleri Otomasyonu",
            "kisa_aciklama": "Mizan (Excel) + Kurumlar Vergisi Beyannamesi (PDF) → Word formatında bilanço ve gelir tablosu hesap incelemeleri metni",
            "aciklama": (
                "Mizan ve Kurumlar Vergisi Beyannamesi verilerinden hareketle bilanço ve gelir "
                "tablosu hesaplarının inceleme metnini Word formatında otomatik üretir. "
                "A. Bilanço Hesapları (yabancı para hesapları, MDV/MODV, özkaynaklar dahil) ve "
                "B. Gelir Tablosu Hesapları (satış, maliyet, faaliyet/finansman giderleri, FGK hesabı, "
                "dönem karı) bölümleri tam metin olarak Word'e yazılır. Tüm tutarlar mizandan çekilir; "
                "veri uydurulmaz."
            ),
            "kategori": "Hesap İncelemeleri",
            "mevzuat": "VUK m.280, VUK Mük. m.298/A, 555 sıra No.lu VUK GT",
            "ucretsiz": False,
            "fiyat": 2500.0,
            "indirme_dosyasi": "TT_HESAP_INCELEMELERI_v1.0.zip",
            "durum": "gelistirme",
            "on_plana_cikar": True,
            "ozellikler": [
                "Mizan + Dövizli Mizan + Bilanço + Gelir Tablosu Excel okuma",
                "Kurumlar Vergisi Beyannamesi PDF okuma ve mukellef otomatik dolum",
                "31.12.2024 / 580 No.lu VUK GT döviz kurları varsayılan",
                "Yabancı para hesapları için doviz cinsi-kur-TL detay tabloları",
                "Stoklar, MDV, MODV, Özkaynaklar için detay tabloları",
                "Finansman Gider Kısıtlaması (KVK m.11/1-i) otomatik hesaplaması",
                "Beyanname-mizan çapraz mutabakat kontrolu (sarı/kırmızı uyarı)",
                "Hem masaüstü (tkinter) hem yerel web (Flask) ile çalışır",
            ],
        },
        {
            "slug": "arge-indirim-5746",
            "ad": "5746 Sayılı Kanun ARGE İndirim Hesaplama Programı",
            "kisa_aciklama": "Bordro + Muhtasar + SGK Bildirgesi → 5746 SK + KVK m.10/1-a kapsamında AR-GE indirimi",
            "aciklama": (
                "5746 sayılı Araştırma, Geliştirme ve Tasarım Faaliyetlerinin Desteklenmesi Hakkında "
                "Kanun ile KVK m.10/1-a kapsamındaki AR-GE indirimini ücret bordrosu, muhtasar beyanname "
                "ve SGK bildirgelerinden hareketle hesaplar. 750 Ar-Ge Giderleri ve 602 Devlet Katkıları "
                "muavin defterlerini de işler; otomatik Diğer Ar-Ge Giderleri aktarımı yapar."
            ),
            "kategori": "AR-GE / KVK",
            "mevzuat": "5746 SK m.3, KVK m.10/1-a, 5510 SGK",
            "ucretsiz": False,
            "fiyat": 2500.0,
            "indirme_dosyasi": "ARGE_INDIRIM_5746_v1.0.zip",
            "durum": "gelistirme",
            "on_plana_cikar": True,
            "ozellikler": [
                "Yaygın muhasebe/bordro yazılımı çıktı formatları desteği",
                "Muhtasar beyanname ile gelir vergisi stopaj indirimi mutabakatı",
                "SGK işveren primi indirimi (yarısı Hazine, %50)",
                "Damga vergisi istisnası",
                "750 Ar-Ge Giderleri muavin parser (PERSONEL/SARF/AMORT alt grupları)",
                "602 Devlet Katkıları muavin (5746 GV/SGK/DV, 5510)",
                "KVK m.10/1-a uyarınca matrahtan %100 indirim hesabı",
                "Çıktı: Excel + PDF özet tablo",
            ],
        },
        {
            "slug": "fgk-kvk-11-i",
            "ad": "Finansman Gider Kısıtlaması Hesaplama (KVK m.11/1-i)",
            "kisa_aciklama": "Yabancı kaynak/özkaynak oranı → %10 oranında KKEG hesaplaması",
            "aciklama": (
                "5520 sayılı Kurumlar Vergisi Kanunu'nun 11/1-i bendi uyarınca yabancı kaynakları "
                "özkaynaklarını aşan işletmelerde finansman giderlerinin Cumhurbaşkanı kararıyla "
                "%10'a kadar olan kısmının KKEG olarak dikkate alınması zorunluluğunun hesaplamasını "
                "otomatik yapar. Mizan, bilanço ve muavin verilerinden hareketle özkaynak/yabancı "
                "kaynak karşılaştırma tablosu ve KKEG tutarını üretir."
            ),
            "kategori": "KVK",
            "mevzuat": "KVK m.11/1-i, 6322 sayılı Kanun, 3490 sayılı CB Kararı",
            "ucretsiz": True,
            "fiyat": 0.0,
            "indirme_dosyasi": None,
            "durum": "gelistirme",
            "on_plana_cikar": True,
            "ozellikler": [
                "Mizan'dan 3'lü/4'lü/5'li hesap toplamlarının otomatik alınması",
                "Maliyete eklenen finansman gideri ayrıştırma",
                "Yıl içi geçici vergi dönemleri ile tutarlılık kontrolü",
                "Hesap incelemeleri için hazır FGK tablosu",
                "Excel + Word çıktı",
            ],
        },
        {
            "slug": "indirimli-kurumlar-vergisi",
            "ad": "İndirimli Kurumlar Vergisi Hesaplama (KVK m.32/A)",
            "kisa_aciklama": "Yatırım Teşvik Belgesi bazında KVK 32/A, YKT ve asgari KV hesaplama",
            "aciklama": (
                "5520 sayılı KVK m.32/A kapsamında yatırım teşvik belgeli yatırımlar için yatırıma "
                "katkı tutarı, indirimli kurumlar vergisi matrahı, yatırım/işletme dönemi ayrımı, "
                "tevsi yatırım oranlaması, uygun/kapsam dışı harcama ayrımı, devreden katkılar, "
                "endeksleme ve 2025+ yurt içi asgari kurumlar vergisi etkisini birlikte hesaplar."
            ),
            "kategori": "KVK / Teşvik",
            "mevzuat": "KVK m.32/A, KVK m.32/C, 2012/3305 sayılı Karar",
            "ucretsiz": False,
            "fiyat": 19000.0,
            "indirme_dosyasi": "KVK32A_HESAPLAMA_v1.1.zip",
            "durum": "gelistirme",
            "on_plana_cikar": True,
            "ozellikler": [
                "Uygun harcama ile arsa/arazi, kur farkı, finansman ve kapsam dışı harcama ayrımı",
                "Yatırım döneminde iki sınır kontrolü: YKT sınırı ve gerçekleşen uygun harcama sınırı",
                "İşletme döneminde yatırım kazancı ile diğer faaliyet kazancını ayırma",
                "Tevsi yatırım için sabit kıymet ve hasılat bazlı oranlama seçenekleri",
                "Devreden yatırıma katkı, endeksleme ve kalan YKT takibi",
                "2025+ yurt içi asgari kurumlar vergisi etkisi",
                "PDF/Word beyanname ve teşvik belgesi okuma yardımcıları",
                "Geliştirme yol haritası: geçici 8 yıl-bazlı otomasyon, çoklu belge dağıtımı, test senaryo kütüphanesi",
            ],
        },
    ]
    for p in programlar:
        ozellikler = p.pop("ozellikler", [])
        prog = Program.query.filter_by(slug=p["slug"]).first()
        if prog:
            for alan, deger in p.items():
                setattr(prog, alan, deger)
            ProgramOzellik.query.filter_by(program_id=prog.id).delete()
        else:
            prog = Program(**p)
            db.session.add(prog)
            db.session.flush()
        db.session.flush()
        for i, o in enumerate(ozellikler):
            db.session.add(ProgramOzellik(program_id=prog.id, metin=o, sira=i))
    db.session.commit()


def seed_admin():
    """Varsayilan admin kullanicisi (ilk acilis)."""
    if User.query.filter_by(email="muratal81@gmail.com").first():
        return
    admin = User(
        email="muratal81@gmail.com",
        ad_soyad="Murat Alan",
        unvan="SMMM",
        sirket="Murat Alan Vergi İndirim Programları",
        telefon="0532 177 47 95",
        rol="admin",
    )
    admin.sifre_belirle(ADMIN_SIFRE)
    db.session.add(admin)
    db.session.commit()


# Admin varsayilan sifresi (env ile override edilebilir)
import os as _os
ADMIN_SIFRE = _os.environ.get("ADMIN_SIFRE", "Gsm6287289.")


def ensure_schema():
    """Mevcut tabloya sonradan eklenen kolonlari guvenli sekilde ekler.
    db.create_all() var olan tabloya kolon EKLEMEZ; bu fonksiyon onu telafi eder.
    PostgreSQL ve SQLite uyumludur."""
    from sqlalchemy import inspect, text
    insp = inspect(db.engine)
    try:
        mevcut_tablolar = insp.get_table_names()
    except Exception:
        return
    # users tablosuna reset_token / reset_expiry
    if "users" in mevcut_tablolar:
        kolonlar = [c["name"] for c in insp.get_columns("users")]
        eklemeler = []
        if "reset_token" not in kolonlar:
            eklemeler.append("ALTER TABLE users ADD COLUMN reset_token VARCHAR(64)")
        if "reset_expiry" not in kolonlar:
            eklemeler.append("ALTER TABLE users ADD COLUMN reset_expiry TIMESTAMP")
        for sql in eklemeler:
            try:
                with db.engine.begin() as conn:
                    conn.execute(text(sql))
            except Exception as e:
                print(f"[ensure_schema] {sql} -> {e}")


def sync_admin_sifre():
    """Mevcut admin kullanicisinin sifresini guncel degerle eslestir."""
    admin = User.query.filter_by(email="muratal81@gmail.com").first()
    if admin:
        admin.sifre_belirle(ADMIN_SIFRE)
        admin.rol = "admin"
        db.session.commit()


def fix_legacy_texts():
    """Eski 'Tam Tasdik' / 'YMM tasdik' metinlerini guncelle (etik temizlik).
    Mevcut PostgreSQL kayitlari seed ile guncellenmedigi icin burada zorla guncellenir."""
    p = Program.query.filter_by(slug="tt-hesap-incelemeleri").first()
    if p:
        p.ad = "Hesap İncelemeleri Otomasyonu"
        p.kategori = "Hesap İncelemeleri"
        p.kisa_aciklama = ("Mizan (Excel) + Kurumlar Vergisi Beyannamesi (PDF) → Word formatında "
                           "bilanço ve gelir tablosu hesap incelemeleri metni")
        p.mevzuat = "VUK m.280, VUK Mük. m.298/A, 555 sıra No.lu VUK GT"
    # Kategorisi 'Tam Tasdik' olan tum kayitlari guncelle
    for prog in Program.query.filter_by(kategori="Tam Tasdik").all():
        prog.kategori = "Hesap İncelemeleri"
    # Marka ismi gecen ozellikleri temizle (telif/marka riski)
    riskli = ["KORMAS", "GREEN", "ISIK", "IŞIK", "LUCA", "LOGO", "MIKRO",
              "NETSIS", "ZIRVE", "VEGA", "YAYLA", "AGRO"]
    for oz in ProgramOzellik.query.all():
        if any(m in (oz.metin or "").upper() for m in riskli):
            oz.metin = "Yaygın muhasebe/bordro yazılımı çıktı formatları desteği"
    db.session.commit()


def update_program_settings():
    """Program fiyat / ucret / durum ayarlarini mevcut DB'de gunceller.
    seed_programs program iceriklerini de gunceller; bu fonksiyon ise fiyat,
    ucret ve durum gibi yayin ayarlarini merkezi olarak korur."""
    ayarlar = {
        # slug: (ucretsiz, fiyat, durum)  durum: aktif|gelistirme|pasif
        "tt-hesap-incelemeleri":      (False, 2500.0,  "gelistirme"),
        "arge-indirim-5746":          (False, 2500.0,  "gelistirme"),
        "fgk-kvk-11-i":               (True,  0.0,     "gelistirme"),
        "indirimli-kurumlar-vergisi": (False, 19000.0, "gelistirme"),
    }
    for slug, (ucretsiz, fiyat, durum) in ayarlar.items():
        p = Program.query.filter_by(slug=slug).first()
        if p:
            p.ucretsiz = ucretsiz
            p.fiyat = fiyat
            p.durum = durum
    db.session.commit()
