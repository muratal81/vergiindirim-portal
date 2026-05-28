"""Cumhur Inan Bilen YMM - Vergi Programlari Portali

Calistirma:
    py app.py

Tarayicida:
    http://localhost:5000
"""
import os
import sys
import threading
import webbrowser
from datetime import datetime
from pathlib import Path

from flask import (Flask, render_template, request, redirect, url_for, flash,
                   send_from_directory, abort, session)
from flask_login import (LoginManager, login_user, logout_user, login_required,
                         current_user)

import uuid
import functools
from datetime import timedelta
from flask import jsonify

from config import Config, DOWNLOADS_DIR
from models import (db, User, Program, ProgramOzellik, Download, Order,
                    License, CollabRequest, ContactMessage, seed_programs, seed_admin)


def _yeni_lisans_anahtari() -> str:
    """XXXX-XXXX-XXXX-XXXX formatinda benzersiz lisans anahtari."""
    h = uuid.uuid4().hex.upper()[:16]
    return "-".join(h[i:i+4] for i in range(0, 16, 4))


def admin_required(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return wrapper


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "giris"
    login_manager.login_message = "Bu sayfa için giriş yapmanız gereklidir."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Sablon icine her route'da gonderilecek config bilgileri
    @app.context_processor
    def inject_globals():
        return {
            "SITE_ADI": app.config["SITE_ADI"],
            "SITE_KISA": app.config["SITE_KISA"],
            "SITE_SLOGAN": app.config["SITE_SLOGAN"],
            "SITE_TELEFON": app.config["SITE_TELEFON"],
            "SITE_EMAIL": app.config["SITE_EMAIL"],
            "SITE_ADRES": app.config["SITE_ADRES"],
            "SITE_SAHIBI": app.config["SITE_SAHIBI"],
            "YIL": datetime.now().year,
        }

    # ------------------ ANA ROUTE'LAR ----------------------
    @app.route("/")
    def index():
        on_plan = Program.query.filter_by(on_plana_cikar=True, durum="aktif").all()
        gelistirme = Program.query.filter_by(durum="gelistirme").all()
        return render_template("index.html", on_plan=on_plan, gelistirme=gelistirme)

    @app.route("/programlar")
    def programlar():
        kategori = request.args.get("kategori")
        q = Program.query
        if kategori:
            q = q.filter_by(kategori=kategori)
        prog_list = q.order_by(Program.on_plana_cikar.desc(), Program.ad).all()
        kategoriler = [r[0] for r in db.session.query(Program.kategori).distinct() if r[0]]
        return render_template("programlar.html", programlar=prog_list, kategoriler=kategoriler, secili_kategori=kategori)

    @app.route("/program/<slug>")
    def program_detay(slug):
        program = Program.query.filter_by(slug=slug).first_or_404()
        ozellikler = ProgramOzellik.query.filter_by(program_id=program.id).order_by(ProgramOzellik.sira).all()
        return render_template("program_detay.html", program=program, ozellikler=ozellikler)

    @app.route("/indir/<slug>")
    @login_required
    def indir(slug):
        program = Program.query.filter_by(slug=slug).first_or_404()
        if program.durum != "aktif":
            flash("Bu program henüz yayında değil.", "warning")
            return redirect(url_for("program_detay", slug=slug))
        if not program.indirme_dosyasi:
            flash("İndirme dosyası bulunamadı.", "danger")
            return redirect(url_for("program_detay", slug=slug))

        # Ucretli programlar lisans (onay + 1 yil gecerlilik) gerektirir
        if not program.ucretsiz:
            lisans = (License.query
                      .filter_by(user_id=current_user.id, program_id=program.id, durum="aktif")
                      .order_by(License.bitis.desc()).first())
            if not lisans or not lisans.gecerli_mi:
                flash(
                    "Bu program ücretli olup lisans gerektirir. Lütfen lisans talep edin; "
                    "talebiniz onaylandığında indirme aktifleşecektir.", "warning"
                )
                return redirect(url_for("lisans_talep", slug=slug))

        # Indirme kaydi
        dl = Download(user_id=current_user.id, program_id=program.id, ip=request.remote_addr)
        program.indirme_sayisi = (program.indirme_sayisi or 0) + 1
        db.session.add(dl)
        db.session.commit()
        return send_from_directory(str(DOWNLOADS_DIR), program.indirme_dosyasi, as_attachment=True)

    @app.route("/lisans-talep/<slug>")
    @login_required
    def lisans_talep(slug):
        program = Program.query.filter_by(slug=slug).first_or_404()
        if program.ucretsiz:
            return redirect(url_for("indir", slug=slug))
        # Zaten aktif lisans var mi?
        aktif = License.query.filter_by(
            user_id=current_user.id, program_id=program.id, durum="aktif").first()
        if aktif and aktif.gecerli_mi:
            flash("Bu program için zaten geçerli bir lisansınız var.", "info")
            return redirect(url_for("panel"))
        # Bekleyen talep var mi?
        bekleyen = License.query.filter_by(
            user_id=current_user.id, program_id=program.id, durum="bekliyor").first()
        if not bekleyen:
            yeni = License(user_id=current_user.id, program_id=program.id, durum="bekliyor")
            db.session.add(yeni)
            db.session.commit()
        flash(
            f"Lisans talebiniz alındı. Onay ve ödeme bilgileri için {app.config['SITE_TELEFON']} "
            "numarasından iletişime geçebilirsiniz. Onaylandığında programı indirebilirsiniz.",
            "success"
        )
        return redirect(url_for("panel"))

    # ----- LISANS DOGRULAMA API (program tarafi cagirir) -----
    @app.route("/api/lisans-dogrula", methods=["POST", "GET"])
    def api_lisans_dogrula():
        anahtar = (request.values.get("anahtar") or "").strip().upper()
        if not anahtar:
            return jsonify({"gecerli": False, "mesaj": "Anahtar gönderilmedi."}), 400
        lisans = License.query.filter_by(anahtar=anahtar).first()
        if not lisans:
            return jsonify({"gecerli": False, "mesaj": "Lisans anahtarı bulunamadı."}), 404
        # Suresi gecmisse durumu guncelle
        if lisans.durum == "aktif" and lisans.bitis and lisans.bitis < datetime.utcnow():
            lisans.durum = "suresi_doldu"
        lisans.son_dogrulama = datetime.utcnow()
        db.session.commit()
        return jsonify({
            "gecerli": lisans.gecerli_mi,
            "durum": lisans.durum,
            "program": lisans.program.ad if lisans.program else "",
            "baslangic": lisans.baslangic.strftime("%d.%m.%Y") if lisans.baslangic else None,
            "bitis": lisans.bitis.strftime("%d.%m.%Y") if lisans.bitis else None,
            "kalan_gun": lisans.kalan_gun,
            "kullanici": lisans.user.ad_soyad if lisans.user else "",
            "mesaj": "Lisans geçerli." if lisans.gecerli_mi else "Lisans geçersiz veya süresi dolmuş.",
        })

    @app.route("/hakkimizda")
    def hakkimizda():
        return render_template("hakkimizda.html")

    @app.route("/iletisim", methods=["GET", "POST"])
    def iletisim():
        if request.method == "POST":
            ad = request.form.get("ad_soyad", "").strip()
            email = request.form.get("email", "").strip()
            tel = request.form.get("telefon", "").strip()
            mesaj = request.form.get("mesaj", "").strip()
            if not (ad and email and mesaj):
                flash("Ad-soyad, e-posta ve mesaj alanları zorunludur.", "danger")
                return render_template("iletisim.html", form=request.form)
            m = ContactMessage(ad_soyad=ad, email=email, telefon=tel, mesaj=mesaj)
            db.session.add(m)
            db.session.commit()
            flash("Mesajınız alındı. En kısa sürede dönüş yapılacaktır.", "success")
            return redirect(url_for("iletisim"))
        return render_template("iletisim.html", form={})

    @app.route("/isbirligi", methods=["GET", "POST"])
    def isbirligi():
        if request.method == "POST":
            ad = request.form.get("ad_soyad", "").strip()
            email = request.form.get("email", "").strip()
            tel = request.form.get("telefon", "").strip()
            unvan = request.form.get("unvan", "").strip()
            sirket = request.form.get("sirket", "").strip()
            konu = request.form.get("konu", "").strip()
            detay = request.form.get("detay", "").strip()
            butce = request.form.get("butce", "").strip()
            if not (ad and email and konu and detay):
                flash("Ad-soyad, e-posta, konu ve ihtiyaç açıklaması zorunludur.", "danger")
                return render_template("isbirligi.html", form=request.form)
            talep = CollabRequest(
                ad_soyad=ad, email=email, telefon=tel, unvan=unvan,
                sirket=sirket, konu=konu, detay=detay, butce=butce,
            )
            db.session.add(talep)
            db.session.commit()
            flash(
                "Talebiniz alındı. İhtiyacınızı değerlendirip en kısa sürede sizinle iletişime "
                "geçeceğiz. İlginiz için teşekkürler.", "success"
            )
            return redirect(url_for("isbirligi"))
        return render_template("isbirligi.html", form={})

    # ------------------ AUTH ----------------------
    @app.route("/giris", methods=["GET", "POST"])
    def giris():
        if current_user.is_authenticated:
            return redirect(url_for("panel"))
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            sifre = request.form.get("sifre", "")
            user = User.query.filter_by(email=email).first()
            if user and user.sifre_kontrol(sifre):
                if not user.aktif:
                    flash("Hesabınız aktif değil.", "danger")
                    return render_template("giris.html")
                login_user(user, remember=True)
                user.son_giris = datetime.utcnow()
                db.session.commit()
                flash(f"Hoşgeldiniz {user.ad_soyad}.", "success")
                return redirect(request.args.get("next") or url_for("panel"))
            flash("E-posta veya şifre hatalı.", "danger")
        return render_template("giris.html")

    @app.route("/kayit", methods=["GET", "POST"])
    def kayit():
        if current_user.is_authenticated:
            return redirect(url_for("panel"))
        if request.method == "POST":
            email = request.form.get("email", "").strip().lower()
            sifre = request.form.get("sifre", "")
            sifre2 = request.form.get("sifre2", "")
            ad_soyad = request.form.get("ad_soyad", "").strip()
            unvan = request.form.get("unvan", "SMMM")
            telefon = request.form.get("telefon", "").strip()
            sirket = request.form.get("sirket", "").strip()

            if not (email and sifre and ad_soyad):
                flash("E-posta, şifre ve ad-soyad zorunludur.", "danger")
                return render_template("kayit.html", form=request.form)
            if len(sifre) < 6:
                flash("Şifre en az 6 karakter olmalıdır.", "danger")
                return render_template("kayit.html", form=request.form)
            if sifre != sifre2:
                flash("Şifreler eşleşmiyor.", "danger")
                return render_template("kayit.html", form=request.form)
            if User.query.filter_by(email=email).first():
                flash("Bu e-posta zaten kayıtlı.", "danger")
                return render_template("kayit.html", form=request.form)

            user = User(
                email=email, ad_soyad=ad_soyad, unvan=unvan,
                telefon=telefon, sirket=sirket
            )
            user.sifre_belirle(sifre)
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash("Kayıt başarılı. Hoşgeldiniz!", "success")
            return redirect(url_for("panel"))
        return render_template("kayit.html", form={})

    @app.route("/cikis")
    @login_required
    def cikis():
        logout_user()
        flash("Çıkış yapıldı.", "info")
        return redirect(url_for("index"))

    # ------------------ KULLANICI PANELI ----------------------
    @app.route("/panel")
    @login_required
    def panel():
        indirmeler = (
            Download.query.filter_by(user_id=current_user.id)
            .order_by(Download.tarih.desc()).limit(20).all()
        )
        lisanslar = (
            License.query.filter_by(user_id=current_user.id)
            .order_by(License.talep_tarihi.desc()).all()
        )
        prog_map = {p.id: p for p in Program.query.all()}
        return render_template("panel.html", indirmeler=indirmeler,
                               lisanslar=lisanslar, prog_map=prog_map)

    # ------------------ ADMIN PANELI ----------------------
    @app.route("/admin")
    @admin_required
    def admin():
        bekleyen_lisans = License.query.filter_by(durum="bekliyor").order_by(License.talep_tarihi.desc()).all()
        aktif_lisans = License.query.filter_by(durum="aktif").order_by(License.bitis.asc()).all()
        talepler = CollabRequest.query.order_by(CollabRequest.tarih.desc()).limit(50).all()
        mesajlar = ContactMessage.query.order_by(ContactMessage.tarih.desc()).limit(50).all()
        kullanicilar = User.query.order_by(User.kayit_tarihi.desc()).all()
        prog_map = {p.id: p for p in Program.query.all()}
        istatistik = {
            "kullanici": User.query.count(),
            "indirme": Download.query.count(),
            "bekleyen_lisans": len(bekleyen_lisans),
            "aktif_lisans": len(aktif_lisans),
            "talep": CollabRequest.query.filter_by(durum="yeni").count(),
            "mesaj": ContactMessage.query.filter_by(durum="yeni").count(),
        }
        return render_template("admin.html", bekleyen_lisans=bekleyen_lisans,
                               aktif_lisans=aktif_lisans, talepler=talepler,
                               mesajlar=mesajlar, kullanicilar=kullanicilar,
                               prog_map=prog_map, istatistik=istatistik)

    @app.route("/admin/lisans/<int:lid>/onayla")
    @admin_required
    def admin_lisans_onayla(lid):
        lisans = License.query.get_or_404(lid)
        lisans.anahtar = _yeni_lisans_anahtari()
        lisans.durum = "aktif"
        lisans.baslangic = datetime.utcnow()
        lisans.bitis = datetime.utcnow() + timedelta(days=365)  # 1 yil
        lisans.onaylayan = current_user.email
        lisans.onay_tarihi = datetime.utcnow()
        db.session.commit()
        flash(f"Lisans onaylandı. Anahtar: {lisans.anahtar} (1 yıl geçerli)", "success")
        return redirect(url_for("admin"))

    @app.route("/admin/lisans/<int:lid>/iptal")
    @admin_required
    def admin_lisans_iptal(lid):
        lisans = License.query.get_or_404(lid)
        lisans.durum = "iptal"
        db.session.commit()
        flash("Lisans iptal edildi.", "info")
        return redirect(url_for("admin"))

    @app.route("/admin/talep/<int:tid>/kapat")
    @admin_required
    def admin_talep_kapat(tid):
        t = CollabRequest.query.get_or_404(tid)
        t.durum = "gorusuldu"
        db.session.commit()
        flash("Talep 'görüşüldü' olarak işaretlendi.", "info")
        return redirect(url_for("admin"))

    @app.route("/admin/mesaj/<int:mid>/kapat")
    @admin_required
    def admin_mesaj_kapat(mid):
        m = ContactMessage.query.get_or_404(mid)
        m.durum = "okundu"
        db.session.commit()
        flash("Mesaj 'okundu' olarak işaretlendi.", "info")
        return redirect(url_for("admin"))

    return app


def main():
    app = create_app()
    with app.app_context():
        db.create_all()
        seed_programs()
        seed_admin()
    threading.Timer(1.5, lambda: webbrowser.open("http://localhost:5000")).start()
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    main()
