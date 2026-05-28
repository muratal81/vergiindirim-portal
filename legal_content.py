"""Yasal sayfa icerikleri (Turkiye e-ticaret mevzuatina uygun).

NOT: Bu metinler genel sablon niteligindedir. Yururluge almadan once bir
hukuk muresavirine/avukata kontrol ettirilmesi tavsiye edilir.
"""

# {{SAHIBI}}, {{EMAIL}}, {{TELEFON}}, {{ADRES}}, {{DOMAIN}} placeholder'lari
# render sirasinda config degerleriyle degistirilir.

GIZLILIK = """
<h2>1. Veri Sorumlusu</h2>
<p>6698 sayılı Kişisel Verilerin Korunması Kanunu ("KVKK") uyarınca, kişisel verileriniz;
veri sorumlusu sıfatıyla <strong>{{SAHIBI}}</strong> tarafından aşağıda açıklanan kapsamda
işlenebilecektir. İletişim: {{EMAIL}} · {{TELEFON}} · {{ADRES}}</p>

<h2>2. İşlenen Kişisel Veriler</h2>
<p>Üyelik ve hizmet sunumu kapsamında; ad-soyad, e-posta adresi, telefon numarası, ünvan
(SMMM/YMM vb.) ve şirket/ofis bilgisi işlenmektedir. Programların kendisi mükellef verisini
(mizan, beyanname vb.) <strong>yerel olarak</strong> işler; bu veriler sunucularımıza
gönderilmez.</p>

<h2>3. Kişisel Verilerin İşlenme Amaçları</h2>
<ul>
<li>Üyelik kaydının oluşturulması ve yönetimi,</li>
<li>Talep edilen programların sunulması ve lisans/indirme süreçlerinin yürütülmesi,</li>
<li>İletişim taleplerinin ve özel çözüm taleplerinin değerlendirilmesi,</li>
<li>Yasal yükümlülüklerin yerine getirilmesi ve faturalandırma.</li>
</ul>

<h2>4. Hukuki Sebep ve Aktarım</h2>
<p>Kişisel verileriniz KVKK m.5 kapsamında sözleşmenin kurulması/ifası ve meşru menfaat
hukuki sebeplerine dayanılarak işlenir. Verileriniz yurt dışına aktarılmaz; yalnızca yasal
zorunluluk halinde yetkili kamu kurumları ile paylaşılabilir. Barındırma hizmeti güvenli
altyapı sağlayıcıları üzerinden yürütülür.</p>

<h2>5. Saklama Süresi</h2>
<p>Kişisel verileriniz, ilgili mevzuatta öngörülen süreler (Vergi Usul Kanunu m.253 uyarınca
asgari 5 yıl) ve işleme amacının gerektirdiği süre boyunca saklanır; sürenin sonunda silinir,
yok edilir veya anonim hale getirilir.</p>

<h2>6. KVKK m.11 Kapsamındaki Haklarınız</h2>
<p>Kişisel verilerinizin işlenip işlenmediğini öğrenme, düzeltilmesini/silinmesini isteme,
işlemenin sınırlandırılmasını talep etme ve diğer KVKK m.11 haklarınızı {{EMAIL}} adresine
başvurarak kullanabilirsiniz.</p>
"""

KULLANIM = """
<h2>1. Genel</h2>
<p>{{DOMAIN}} web sitesi ("Site") {{SAHIBI}} tarafından işletilmektedir. Siteyi kullanarak
bu Kullanım Koşullarını kabul etmiş sayılırsınız.</p>

<h2>2. Hizmetin Niteliği</h2>
<p>Site üzerinden sunulan programlar, vergi mevzuatı kapsamındaki hesaplamaları kolaylaştırmaya
yönelik <strong>yardımcı yazılım araçlarıdır</strong>. Üretilen çıktıların doğruluğu, ilgili
mali müşavir/yetkili kişi tarafından kontrol edilmeli ve nihai sorumluluk kullanıcıya aittir.
Yazılım çıktıları resmi beyan, tasdik veya mali müşavirlik hizmeti yerine geçmez.</p>

<h2>3. Fikri Mülkiyet</h2>
<p>Sitedeki tüm program hakları, kaynak kodu, tasarım ve içerikler {{SAHIBI}}'na aittir.
İzinsiz kopyalanamaz, çoğaltılamaz, dağıtılamaz veya ticari amaçla kullanılamaz.</p>

<h2>4. Lisans ve Kullanım</h2>
<p>İndirilen programlar, verilen lisans kapsamında ve süresince (varsa 1 yıl) kullanılabilir.
Lisans devredilemez. Programların başka kişilerle paylaşılması, satılması veya kaynak kodunun
değiştirilerek dağıtılması yasaktır.</p>

<h2>5. Sorumluluğun Sınırlandırılması</h2>
<p>Yazılımların kullanımından doğabilecek doğrudan/dolaylı zararlardan {{SAHIBI}} sorumlu
tutulamaz. Mevzuat değişiklikleri ve hesaplama sonuçlarının güncel mevzuata uygunluğu
kullanıcı tarafından teyit edilmelidir.</p>

<h2>6. Değişiklikler</h2>
<p>{{SAHIBI}}, bu koşulları önceden bildirimde bulunmaksızın güncelleme hakkını saklı tutar.</p>
"""

MESAFELI = """
<h2>1. Taraflar ve Konu</h2>
<p>İşbu Mesafeli Satış Sözleşmesi; satıcı <strong>{{SAHIBI}}</strong> ({{EMAIL}}, {{TELEFON}},
{{ADRES}}) ile {{DOMAIN}} üzerinden dijital ürün (yazılım/program lisansı) satın alan ALICI
arasında, 6502 sayılı Tüketicinin Korunması Hakkında Kanun ve Mesafeli Sözleşmeler Yönetmeliği
uyarınca düzenlenmiştir.</p>

<h2>2. Ürün ve Bedel</h2>
<p>Satışa konu ürün, Site üzerinde nitelikleri ve fiyatı belirtilen dijital yazılım/program
lisansıdır. Fiyatlara KDV dahildir (uygulanabilir olduğu ölçüde). Ödeme onaylandığında lisans
tahsis edilir ve indirme aktifleşir.</p>

<h2>3. Teslimat</h2>
<p>Ürün dijital olup, ödeme onayı ve lisans onayı sonrasında üyelik hesabı üzerinden elektronik
ortamda (indirme bağlantısı/lisans anahtarı) teslim edilir. Fiziksel teslimat yoktur.</p>

<h2>4. Cayma Hakkı</h2>
<p>Mesafeli Sözleşmeler Yönetmeliği m.15/1-ğ uyarınca, <strong>elektronik ortamda anında ifa
edilen ve tüketiciye anında teslim edilen gayri maddi mallara (dijital içerik/yazılım) ilişkin
sözleşmelerde cayma hakkı bulunmamaktadır.</strong> Lisans anahtarı teslim edilip indirme
gerçekleştikten sonra iade yapılamaz. İndirme gerçekleşmeden önce talep halinde iade
değerlendirilebilir.</p>

<h2>5. Fatura</h2>
<p>Satın alınan ürünler için yasal fatura düzenlenir; talep halinde e-arşiv fatura iletilir.</p>

<h2>6. Uyuşmazlık</h2>
<p>Uyuşmazlıklarda Tüketici Hakem Heyetleri ve Tüketici Mahkemeleri yetkilidir. Şikayet ve
talepler için {{EMAIL}} adresine başvurulabilir.</p>
"""

CEREZ = """
<h2>1. Çerez Nedir?</h2>
<p>Çerezler, ziyaret ettiğiniz web sitelerinin tarayıcınıza kaydettiği küçük metin
dosyalarıdır. {{DOMAIN}}, oturum yönetimi ve temel site işlevleri için zorunlu çerezler
kullanır.</p>

<h2>2. Kullanılan Çerezler</h2>
<ul>
<li><strong>Zorunlu çerezler:</strong> Oturum açma (giriş/üyelik) ve güvenlik için gereklidir;
bunlar olmadan site düzgün çalışmaz.</li>
<li><strong>İşlevsel çerezler:</strong> Tercihlerinizi (ör. oturum hatırlama) saklamak için
kullanılır.</li>
</ul>
<p>Site, üçüncü taraf reklam/izleme çerezleri kullanmamaktadır.</p>

<h2>3. Çerezleri Yönetme</h2>
<p>Tarayıcı ayarlarınızdan çerezleri silebilir veya engelleyebilirsiniz. Ancak zorunlu
çerezlerin engellenmesi durumunda giriş yapma gibi işlevler çalışmayabilir.</p>

<h2>4. İletişim</h2>
<p>Çerez politikamıza ilişkin sorularınız için {{EMAIL}} adresinden bize ulaşabilirsiniz.</p>
"""

SAYFALAR = {
    "gizlilik": ("Gizlilik Politikası ve KVKK Aydınlatma Metni", GIZLILIK),
    "kullanim-kosullari": ("Kullanım Koşulları", KULLANIM),
    "mesafeli-satis": ("Mesafeli Satış Sözleşmesi", MESAFELI),
    "cerez": ("Çerez Politikası", CEREZ),
}


def render_icerik(key: str, cfg: dict):
    """Placeholder'lari config degerleriyle degistirip (baslik, html) doner."""
    item = SAYFALAR.get(key)
    if not item:
        return None
    baslik, html = item
    html = (html.replace("{{SAHIBI}}", cfg.get("SITE_SAHIBI", ""))
                .replace("{{EMAIL}}", cfg.get("SITE_EMAIL", ""))
                .replace("{{TELEFON}}", cfg.get("SITE_TELEFON", ""))
                .replace("{{ADRES}}", cfg.get("SITE_ADRES", ""))
                .replace("{{DOMAIN}}", cfg.get("SITE_DOMAIN", "")))
    return baslik, html
