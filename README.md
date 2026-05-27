# Vergi İndirim Programları Portalı

**[vergiindirim.com.tr](https://vergiindirim.com.tr)** — Mükelleflerin yasal yollardan vergi yükünü düşüren özellikli vergi konularını otomatize eden masaüstü ve web programları portalı.

## İçerik

- **Tam Tasdik Raporu - Hesap İncelemeleri** otomasyonu (Mizan + Beyanname → Word)
- **5746 sayılı Kanun AR-GE İndirim** hesaplama
- **Finansman Gider Kısıtlaması** (KVK m.11/1-i)
- **İndirimli Kurumlar Vergisi** (KVK m.32/A)
- (Yol haritasında: KKM İstisnası, Enflasyon Düzeltmesi, İştirak Kazançları İstisnası)

## Teknoloji

- **Backend:** Python 3.11 + Flask 3 + SQLAlchemy 2 + Flask-Login
- **Veritabanı:** PostgreSQL (production) / SQLite (yerel)
- **Frontend:** HTML + CSS (inline kurumsal tasarım)
- **Deployment:** Render.com (Procfile + render.yaml + gunicorn)

## Yerel Çalıştırma

```bash
py -m pip install -r requirements.txt
py app.py
# http://localhost:5000
```

veya Windows için `BASLAT_WEBSITE.bat` çift tıkla.

## Production Deployment (Render)

1. GitHub'a push: `git push origin main`
2. Render.com Blueprint ile `render.yaml` deploy edilir
3. Custom domain bağlanır: `vergiindirim.com.tr`
4. SSL otomatik (Let's Encrypt)

## Lisans ve Sahiplik

Tüm program hakları, kaynak kodu ve site sahipliği **Murat Alan** adına kayıtlıdır.

İletişim: muratal81@gmail.com | 0532 177 47 95
