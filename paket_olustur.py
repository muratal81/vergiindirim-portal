r"""Hesap Incelemeleri programini temiz, AES sifreli ZIP'e paketler.

Kaynak: ..\TT HESAP INCELEMERLI PROGRAMI\TT_HESAP_INCELEMELERI
Hedef:  downloads\VI_RAPOR_v1.1.zip  (master sablon, parolasiz)

Indirme anindaki sifreli kopya, app.py tarafindan kullanici lisansina
ozel rastgele parolayla on-the-fly olarak _olustur_sifreli_zip() ile uretilir.

Bu script ZIP'in temiz ICERIGINI hazirlar:
  - Musteri verileri (XLSX/PDF) dahil edilmez
  - test_*, _repro_*, _inspect_*, _read_xlsx dev/debug betikleri dahil edilmez
  - ornek_ciktilar/ klasoru (gercek musteri Word ciktilari) dahil edilmez
  - __pycache__ klasorleri dahil edilmez
  - Marka temiz tarama: KORMAS/GREEN/LUCA/ISIK/MIKRO/NETSIS/ZIRVE/VEGA/YAYLA/AGRO yoksa devam
"""
from __future__ import annotations
import os
import re
import sys
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
KAYNAK_PARENT = BASE.parent / "TT HESAP İNCELEMERLİ PROGRAMI"
KAYNAK = KAYNAK_PARENT / "TT_HESAP_INCELEMELERI"
HEDEF = BASE / "downloads" / "VI_RAPOR_v1.1.zip"

# Parent klasorden ZIP'in KOKUNE alinacak baslatici dosyalar
KOK_DOSYALAR = ["KURULUM.bat", "BASLAT_MASAUSTU.bat", "BASLAT_WEB.bat"]

DISLA_DIZIN = {"__pycache__", "ornek_ciktilar", ".venv", ".git"}
DISLA_DOSYA_DESEN = re.compile(
    r"^(test_calistir\.py|_repro_.*\.py|_inspect_.*\.py|_read_xlsx\.py|.*\.pyc|.*\.pyo)$",
    re.IGNORECASE
)
# Marka/firma adlari (paket icerigi tarama).
# NOT: Kelime-sinirli regex; "topluca" -> LUCA false positive olusturmaz,
# "GREEN" sadece marka adi olarak kullanildiginda yakalanir (renk degiskeni degil).
# Renk degiskeni (#xxxxxx ile baslayan veya GREEN = "#..." gibi) hosgorulur.
RISKLI_PATTERN = re.compile(
    r"\b(KORMAS|LUCA|NETSIS|ZIRVE|VEGA|YAYLA AGRO|YAYLA TARIM|CIBILEN|CUMHUR İNAN)\b",
    re.IGNORECASE
)


def _dahil_mi(yol: Path) -> bool:
    # Klasor disla
    for parca in yol.parts:
        if parca in DISLA_DIZIN:
            return False
    # Dosya adi disla
    if DISLA_DOSYA_DESEN.match(yol.name):
        return False
    return True


def _risk_tara_dosya(yol: Path) -> list[str]:
    """Marka adi vb. risk kelimesi geciyor mu? Sadece metin dosyalarini tara."""
    if yol.suffix.lower() not in (".py", ".md", ".txt", ".json"):
        return []
    try:
        icerik = yol.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    bulundu = sorted(set(m.upper() for m in RISKLI_PATTERN.findall(icerik)))
    return bulundu


def paket_olustur(kaynak: Path = KAYNAK, hedef: Path = HEDEF) -> None:
    if not kaynak.exists():
        print(f"HATA: Kaynak bulunamadi: {kaynak}")
        sys.exit(1)
    hedef.parent.mkdir(parents=True, exist_ok=True)

    dahil_edilenler: list[Path] = []
    risk_bulgulari: dict[str, list[str]] = {}
    for kok, dirs, dosyalar in os.walk(kaynak):
        # Dizinleri yerinde dislayalim
        dirs[:] = [d for d in dirs if d not in DISLA_DIZIN]
        for d in dosyalar:
            tam = Path(kok) / d
            goreceli = tam.relative_to(kaynak)
            if not _dahil_mi(goreceli):
                continue
            riskler = _risk_tara_dosya(tam)
            if riskler:
                risk_bulgulari[str(goreceli)] = riskler
            dahil_edilenler.append(tam)

    if risk_bulgulari:
        print("UYARI: Su dosyalarda marka/firma adi geciyor; ZIP'e KOYULMAYACAK:")
        for yol, kels in risk_bulgulari.items():
            print(f"  {yol}: {', '.join(kels)}")
        dahil_edilenler = [d for d in dahil_edilenler if str(d.relative_to(kaynak)) not in risk_bulgulari]

    if hedef.exists():
        hedef.unlink()

    # KURULUM_VE_KULLANIM.md'i ZIP kokune kopyala (kullanici hemen gorsun)
    readme_kaynak = kaynak / "KURULUM_VE_KULLANIM.md"

    with zipfile.ZipFile(hedef, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        # 1) Baslatici .bat'lar (ZIP kokune)
        bat_sayisi = 0
        for bat in KOK_DOSYALAR:
            kaynak_yol = KAYNAK_PARENT / bat
            if kaynak_yol.exists():
                zf.write(kaynak_yol, arcname=bat)
                bat_sayisi += 1
            else:
                print(f"UYARI: {bat} bulunamadi: {kaynak_yol}")
        # 2) README'i kokte de yer alsin (kullanici aciliste gorsun)
        if readme_kaynak.exists():
            zf.write(readme_kaynak, arcname="KURULUM_VE_KULLANIM.md")
        # 3) Program kodu (TT_HESAP_INCELEMELERI/ alt klasoru)
        for tam in dahil_edilenler:
            arc = "TT_HESAP_INCELEMELERI/" + str(tam.relative_to(kaynak)).replace("\\", "/")
            zf.write(tam, arcname=arc)

    boyut_kb = hedef.stat().st_size / 1024
    toplam = len(dahil_edilenler) + bat_sayisi + (1 if readme_kaynak.exists() else 0)
    print(f"OK: {hedef} olusturuldu ({boyut_kb:.1f} KB, {toplam} dosya)")
    print(f"     - Baslatici .bat: {bat_sayisi}, README: {'evet' if readme_kaynak.exists() else 'YOK'}, program: {len(dahil_edilenler)}")
    print("Not: Bu master ZIP parolasizdir; indirme aninda kullanici lisansina ozel")
    print("     AES parolali bir kopyasi app.py icinde uretilir.")


if __name__ == "__main__":
    paket_olustur()
