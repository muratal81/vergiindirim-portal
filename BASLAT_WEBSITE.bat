@echo off
REM Cumhur Inan Bilen YMM - Vergi Portali - Web Sitesi Baslatici
cd /d "%~dp0"
echo.
echo  ============================================================
echo    Cumhur Inan Bilen YMM - Vergi Portali
echo  ============================================================
echo.
echo  Web sitesi baslatiliyor...
echo  Adres: http://localhost:5000
echo.
echo  Site otomatik olarak varsayilan tarayicinizda acilacak.
echo  Sunucuyu durdurmak icin: Ctrl+C basin veya pencereyi kapatin.
echo.
py app.py
if errorlevel 1 (
    echo.
    echo  HATA: Site baslatilamadi.
    echo  Once KURULUM.bat dosyasina cift tiklayin (Python paketleri icin).
    echo.
    pause
)
