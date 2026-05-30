"""E-posta gonderim modulu.

SMTP ayarlari environment variable'dan okunur. Ayarli degilse mail
gonderilmez (False doner) — bu durumda talepler admin panelinde gorunur.

Render env variable'lari (Gmail App Password ornegi):
    MAIL_HOST=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USER=muratal81@gmail.com
    MAIL_PASS=<16 haneli Google App Password>
    MAIL_FROM=Vergi İndirim <muratal81@gmail.com>
    ADMIN_EMAIL=muratal81@gmail.com
"""
import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


def smtp_ayarli_mi() -> bool:
    return bool(os.environ.get("MAIL_HOST") and os.environ.get("MAIL_USER")
                and os.environ.get("MAIL_PASS"))


def admin_email() -> str:
    return os.environ.get("ADMIN_EMAIL", "muratal81@gmail.com")


def send_mail(to: str, subject: str, body_html: str) -> bool:
    """HTML e-posta gonderir. Basarili ise True, SMTP yoksa/hata olursa False."""
    host = os.environ.get("MAIL_HOST", "").strip()
    port = int(os.environ.get("MAIL_PORT", "587"))
    user = os.environ.get("MAIL_USER", "").strip()
    pw = os.environ.get("MAIL_PASS", "").strip()
    mail_from = os.environ.get("MAIL_FROM", user)
    print(f"[mailer] cagri: to={to} subject={subject[:60]!r} host={host!r} port={port} user={user!r} pw_set={bool(pw)}", flush=True)
    if not (host and user and pw):
        print(f"[mailer] SMTP eksik -> mail gonderilmedi (host={bool(host)}, user={bool(user)}, pw={bool(pw)})", flush=True)
        return False
    try:
        msg = MIMEText(body_html, "html", "utf-8")
        msg["Subject"] = str(Header(subject, "utf-8"))
        # MAIL_FROM "Ad <mail>" veya sadece mail olabilir
        if "<" in mail_from:
            msg["From"] = mail_from
        else:
            msg["From"] = formataddr((str(Header("Vergi İndirim", "utf-8")), mail_from))
        msg["To"] = to
        ctx = ssl.create_default_context()
        if port == 465:
            with smtplib.SMTP_SSL(host, port, context=ctx, timeout=20) as s:
                s.login(user, pw)
                s.sendmail(user, [to], msg.as_string())
        else:
            with smtplib.SMTP(host, port, timeout=20) as s:
                s.starttls(context=ctx)
                s.login(user, pw)
                s.sendmail(user, [to], msg.as_string())
        print(f"[mailer] OK gonderildi: to={to}", flush=True)
        return True
    except Exception as e:
        print(f"[mailer] Gonderim hatasi ({type(e).__name__}): {e}", flush=True)
        return False


def bildir_admin(subject: str, body_html: str) -> bool:
    """Admin'e (site sahibine) bildirim maili."""
    return send_mail(admin_email(), subject, body_html)
