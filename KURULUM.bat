@echo off
REM Cumhur Inan Bilen YMM - Vergi Portali - Ilk Kurulum
echo.
echo  Web sitesi icin gerekli Python paketleri yukleniyor...
echo.
py -m pip install flask flask-login flask-sqlalchemy werkzeug python-docx openpyxl pdfplumber
echo.
echo  Kurulum tamamlandi. Artik BASLAT_WEBSITE.bat dosyasina cift tiklayarak
echo  web sitesini calistirabilirsiniz.
echo.
pause
