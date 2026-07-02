from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3, os

app = Flask(__name__)
app.secret_key = "hidayet_saygi_2026_sabit"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sirket.db")

# Giriş Bilgileri
ADMIN_USER = "hidayets"
ADMIN_PASS = "171025"

# Veritabanı ve Tablo Kontrolü
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS ayarlar (anahtar TEXT PRIMARY KEY, deger TEXT)")
    cursor.execute("CREATE TABLE IF NOT EXISTS urunler (id INTEGER PRIMARY KEY AUTOINCREMENT, urun_adi TEXT, urun_detay TEXT, urun_gorsel TEXT)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ayarlar")
    ayarlar = dict(cursor.fetchall())
    cursor.execute("SELECT * FROM urunler")
    urunler = cursor.fetchall()
    conn.close()
    return render_template('index.html', ayarlar=ayarlar, urunler=urunler)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'): return redirect(url_for('login'))
    if request.method == 'POST':
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        # Basit ayar güncelleme
        for key in request.form:
            if key not in ['urun_adi', 'urun_detay', 'urun_gorsel']:
                cursor.execute("INSERT OR REPLACE INTO ayarlar (anahtar, deger) VALUES (?, ?)", (key, request.form[key]))
        # Ürün ekleme
        if 'urun_adi' in request.form and request.form['urun_adi']:
            cursor.execute("INSERT INTO urunler (urun_adi, urun_detay, urun_gorsel) VALUES (?, ?, ?)", 
                           (request.form['urun_adi'], request.form['urun_detay'], request.form['urun_gorsel']))
        conn.commit()
        conn.close()
        return redirect(url_for('admin'))
    return render_template('admin.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == ADMIN_USER and request.form['pass'] == ADMIN_PASS:
            session['logged_in'] = True
            return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
