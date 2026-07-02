from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "hidayet_saygi_ozel_anahtar_key"  # Oturum güvenliği için

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sirket.db")

# İSTEDİĞİN GÜNCEL GİRİŞ BİLGİLERİ
ADMIN_USER = "hidayets"
ADMIN_PASS = "171025"

def veri_tabani_kur():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ayarlar (
            anahtar TEXT PRIMARY KEY,
            deger TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urunler (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            urun_adi TEXT,
            urun_detay TEXT,
            urun_gorsel TEXT
        )
    ''')
    
    try:
        cursor.execute("ALTER TABLE urunler ADD COLUMN urun_gorsel TEXT")
    except sqlite3.OperationalError:
        pass

    cursor.execute("SELECT COUNT(*) FROM ayarlar")
    if cursor.fetchone()[0] == 0:
        varsayilanlar = {
            "baslik": "Hidayet Saygı Ahşap Ürünleri",
            "alt_baslik": "Endüstriyel Kereste ve Palet Üretiminde Çözüm Ortağınız",
            "aciklama": "Geleneksel hizmet kalıplarının dışına çıkarak; endüstriyel ahşap, ham madde ve palet tedariğinde iş ortaklarımıza küresel standartlarda, kesintisiz ve tam zamanlı çözümler sunuyoruz.",
            "hakkimizda_metni": "Hidayet Saygı Ahşap Ürünleri olarak, sektördeki köklü tecrübemiz ve yüksek üretim kapasitemiz ile endüstriyel ahşap çözümleri sunuyoruz. Konya Organize Sanayi Bölgesi'nde yer alan tesisimizde; Euro palet, özel ölçü palet, inşaatlık ve ambalajlık kereste üretimini modern teknoloji ve fırınlama altyapısıyla gerçekleştiriyoruz. Müşterilerimize sadece bir tedarikçi değil, lojistik ve operasyonel süreçlerinde güvenilir bir çözüm ortağı olma vizyonuyla çalışıyoruz.",
            "logo_url": "https://images.unsplash.com/photo-1533090161767-e6ffed986c88?q=80&w=200",
            "kapak_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?q=80&w=1200",
            "adres": "Organize Sanayi Bölgesi, Konya / Türkiye",
            "eposta": "info@hidayetsaygiahsap.com",
            "whatsapp_no": "905000000000",
            "harita_linki": "https://maps.google.com"
        }
        for anahtar, deger in varsayilanlar.items():
            cursor.execute("INSERT OR IGNORE INTO ayarlar (anahtar, deger) VALUES (?, ?)", (anahtar, deger))
            
    conn.commit()
    conn.close()

def verileri_getir():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT anahtar, deger FROM ayarlar")
    veriler = dict(cursor.fetchall())
    cursor.execute("SELECT id, urun_adi, urun_detay, urun_gorsel FROM urunler")
    veriler['urunler_listesi'] = cursor.fetchall()
    conn.close()
    return veriler

@app.route('/')
def home():
    try:
        veri = verileri_getir()
    except Exception:
        veri_tabani_kur()
        veri = verileri_getir()
    return render_template('index.html', veri=veri)

@app.route('/login', methods=['GET', 'POST'])
def login():
    hata = None
    if request.method == 'POST':
        kullanici = request.form.get('kullanici')
        sifre = request.form.get('sifre')
        if kullanici == ADMIN_USER and sifre == ADMIN_PASS:
            session['giriş_yapti'] = True
            return redirect(url_for('admin'))
        else:
            hata = "Kullanıcı adı veya şifre hatalı!"
    return render_template('login.html', hata=hata)

@app.route('/logout')
def logout():
    session.pop('giriş_yapti', None)
    return redirect(url_for('home'))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('giriş_yapti'):
        return redirect(url_for('login'))
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    if request.method == 'POST':
        islem = request.form.get('islem')
        
        if islem == 'urun_ekle':
            yeni_ad = request.form.get('yeni_urun_adi')
            yeni_detay = request.form.get('yeni_urun_detay')
            yeni_gorsel = request.form.get('yeni_urun_gorsel') or "https://images.unsplash.com/photo-1541534741688-6078c6bfb5c5?q=80&w=500"
            if yeni_ad and yeni_detay:
                cursor.execute("INSERT INTO urunler (urun_adi, urun_detay, urun_gorsel) VALUES (?, ?, ?)", (yeni_ad, yeni_detay, yeni_gorsel))
                
        elif islem == 'urun_sil':
            silinecek_id = request.form.get('urun_id')
            cursor.execute("DELETE FROM urunler WHERE id = ?", (silinecek_id,))
            
        else:
            for anahtar in request.form:
                if anahtar not in ['islem', 'yeni_urun_adi', 'yeni_urun_detay', 'yeni_urun_gorsel', 'urun_id']:
                    cursor.execute("UPDATE ayarlar SET deger = ? WHERE anahtar = ?", (request.form.get(anahtar), anahtar))
            
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
        
    conn.close()
    veri = verileri_getir()
    return render_template('admin.html', veri=veri)

if __name__ == '__main__':
    veri_tabani_kur()
    app.run(debug=True)