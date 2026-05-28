"""Marka / firma / kisisel veri risk tarayicisi.

Her push oncesi calistirilir. Kaynak kod + dagitilan ZIP icinde
muhasebe yazilimi markalari, gercek firma/kisi adlari ve vergi/kimlik
numaralari arar. Telif/marka/KVKK riskini onlemek icindir.

Calistirma:  py risk_tara.py
"""
import os
import re
import sys
import zipfile

# Spesifik firma/kisi referanslari (eski sahiplik - olmamali)
SPESIFIK = [
    "cibilenymm", "cumhurbilenymm", "CUMHUR İNAN", "CUMHUR INAN",
    "CUMHUR BILEN", "BILEN YMM", "BİLEN YMM", "YAYLA AGRO", "YAYLA AĞRO",
]
# Muhasebe yazilimi markalari (kelime siniri ile)
MARKALAR = ["KORMAS", "GREEN", "LUCA", "MIKRO", "NETSIS", "ZIRVE",
            "ISIK", "IŞIK", "VEGA", "TIGER", "WINGS"]
# Gercek vergi/kimlik no'lari (test verisi)
NUMARALAR = ["3200039053", "2160970424", "51973517132", "006283", "06105060"]

# models.py'deki temizleme listesi (fix_legacy_texts) gercek kullanim degil
ATLA_SATIR_ICEREN = ['riskli = [', '"NETSIS", "ZIRVE"', 'MARKALAR =', 'SPESIFIK =']


def tara_metin(metin: str, kaynak: str, bulgular: list):
    satirlar = metin.split("\n")
    for i, satir in enumerate(satirlar, 1):
        # Temizleme listesi satirlarini atla
        if any(a in satir for a in ATLA_SATIR_ICEREN):
            continue
        up = satir.upper()
        for s in SPESIFIK:
            if s.upper() in up:
                bulgular.append((kaynak, i, s, satir.strip()[:80]))
        for m in MARKALAR:
            if re.search(r"\b" + re.escape(m) + r"\b", up):
                bulgular.append((kaynak, i, m, satir.strip()[:80]))
        for n in NUMARALAR:
            if n in satir:
                bulgular.append((kaynak, i, n, satir.strip()[:80]))


def main():
    base = os.path.dirname(os.path.abspath(__file__))
    bulgular = []
    # 1) Kaynak dosyalar
    for root, dirs, files in os.walk(base):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "data")]
        for f in files:
            if f.endswith((".py", ".html", ".css", ".js", ".md", ".txt")) and f != "risk_tara.py":
                p = os.path.join(root, f)
                try:
                    tara_metin(open(p, encoding="utf-8", errors="ignore").read(),
                               os.path.relpath(p, base), bulgular)
                except Exception:
                    pass
    # 2) Dagitilan ZIP
    zpath = os.path.join(base, "downloads", "TT_HESAP_INCELEMELERI_v1.0.zip")
    if os.path.exists(zpath):
        z = zipfile.ZipFile(zpath)
        for n in z.namelist():
            if n.endswith((".py", ".html", ".css", ".txt", ".md")):
                tara_metin(z.read(n).decode("utf-8", errors="ignore"), "ZIP:" + n, bulgular)

    if bulgular:
        print("!!! RISK BULUNDU:")
        for kaynak, satir, kelime, icerik in bulgular:
            print(f"  [{kelime}] {kaynak}:{satir}  ->  {icerik}")
        sys.exit(1)
    print("TEMIZ — marka/firma/kisisel veri riski bulunamadi (kaynak + dagitilan ZIP).")
    sys.exit(0)


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
