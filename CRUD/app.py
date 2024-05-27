from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

import pymysql.cursors, os, datetime, random, string

application = Flask(__name__)
conn = cursor = None
application.secret_key = 'your secret key'

#My SQL Configuration
application.config['MYSQL_HOST'] = 'localhost'
application.config['MYSQL_USER'] = 'root'
application.config['MYSQL_PASSWORD'] = ''
application.config['MYSQL_DB'] = 'db_pegawai'

application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/db_pegawai'

db = SQLAlchemy(application)    
mysql = MySQL(application)

#fungsi untuk menyimpan lokasi foto
UPLOAD_FOLDER = 'E:\FILE OCTA\KULIAH\SEMESTER 2\WEB OOP\Web_Pegawai\CRUD\static\images'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#fungsi koneksi ke basis data
def openDb():
    global conn, cursor
    conn = pymysql.connect(db="db_pegawai", user="root", passwd="",host="localhost",port=3306,autocommit=True)
    cursor = conn.cursor()	

#fungsi menutup koneksi
def closeDb():
    global conn, cursor
    cursor.close()
    conn.close()

@application.route('/general/')
def general():
    return render_template('general.html')

@application.route('/', methods=['GET','POST'])
def home():
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))

    if request.method == "POST":
        nik = request.form.get('nik')
        password = request.form.get('password')
        cur = mysql.connection.cursor()
        
        cur.execute(f"SELECT nik, password FROM pegawai WHERE nik = '{nik}'")
        user = cur.fetchone()
        cur.close()
        
        if user and check_password_hash(user[1], password):
            session['nik'] = user[0]
            return redirect(url_for('user_dashboard'))
        else:
            return render_template('home.html', error='Invalid nik or password!!!')
        
    return render_template('home.html')

# User Pages
@application.route('/user/')
def user():
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' not in session:
        return redirect(url_for('home'))
    return redirect(url_for('user_dashboard'))

@application.route('/user/dashboard/')
def user_dashboard():
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' not in session:
        return redirect(url_for('home'))
    nik = session['nik']
    openDb()
    cursor.execute(f"SELECT * FROM pegawai WHERE nik = '{nik}'")
    data = cursor.fetchone()
    closeDb()
    return render_template('user_dashboard.html', data=data, welcome=True)

@application.route('/user/profile/')
def user_profile():
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' not in session:
        return redirect(url_for('home'))
    nik = session['nik']
    openDb()
    cursor.execute(f"SELECT * FROM pegawai WHERE nik = '{nik}'")
    data = cursor.fetchone()
    closeDb()
    return render_template('user_dashboard.html', data=data, profile=True)

# halaman pesan
@application.route('/user/messages/')
def user_messages():
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' not in session:
        return redirect(url_for('home'))
    
    openDb()
    container = []
    cursor.execute(f"SELECT * FROM pesan ORDER BY tgl DESC")
    result = cursor.fetchall()
    for message in result:
        container.append(message)
    closeDb()
    return render_template('user_messages.html', container=container, nik=session['nik'])

@application.route('/user/messages/<kode>/')
def user_message(kode):
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' not in session:
        return redirect(url_for('home'))
    openDb()
    cursor.execute(f"SELECT * FROM pesan WHERE kode = '{kode}'")
    pesan = cursor.fetchone()
    if not pesan:
        return redirect(url_for('user_messages'))
    isi = pesan[4].split("\n")
    closeDb()
    return render_template('user_message.html', pesan=pesan, isi=isi)

# contact page
@application.route('/user/contact/')
def user_contact():
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' not in session:
        return redirect(url_for('home'))
    # html unfinished
    return render_template('contact.html', nik=session['nik'])   

@application.route('/user/logout/')
def user_logout():
    session.pop('nik', None)
    return redirect(url_for('home'))


@application.route('/forgot/', methods=['GET','POST'])
def forgot():
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))

    if request.method == "POST":
        nik = request.form['nik']
        email = request.form['email']
        cur = mysql.connection.cursor()

        cur.execute(f"SELECT nik, email FROM pegawai WHERE nik=%s AND email=%s", (nik,email))
        user = cur.fetchone()
        cur.close()
        
        if user:
            session['forgot'] = user[0]
            return redirect(url_for('forgot_entry'))
        else:
            return render_template('forgot.html', error='Invalid nik or email!!!')

    return render_template('forgot.html')

@application.route('/forgot/entry/',  methods=['GET','POST'])
def forgot_entry():
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' not in session:
        return redirect(url_for('forgot'))

    if request.method == "POST":
        password = request.form['password']
        confirm_pwd = request.form['confirm_password']

        if password != confirm_pwd:
            return render_template('forgot_entry.html', error='Passwords do not match!')

        hashed_password = generate_password_hash(password) #Hash the password

        cur = mysql.connection.cursor()
        cur.execute(f"UPDATE pegawai SET password=%s WHERE nik=%s", (hashed_password, forgot))
        mysql.connection.commit()
        cur.close()

        session.pop('forgot', None)
        return redirect(url_for('home'))

    return render_template('forgot_entry.html')

@application.route('/clear_session1/')
def clear_session():
    session.pop('forgot', None)
    return redirect(url_for('forgot'))

# Admin Pages
@application.route('/admin/')
def admin():
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'nia' in session:
        return redirect(url_for('admin_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    return redirect(url_for('admin_login'))

#fungsi view admin_dashboard() untuk menampilkan data dari basis data
@application.route('/admin/dashboard/')
def admin_dashboard():   
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))
    
    nia = session['nia']
    openDb()
    container = []
    sql = "SELECT * FROM pegawai ORDER BY NIK ASC;"
    cursor.execute(sql)
    results = cursor.fetchall()
    for data in results:
        container.append(data)
    sql = f"SELECT nama FROM admin where nia = '{nia}'"
    cursor.execute(sql)
    admin = cursor.fetchone()
    closeDb()
    return render_template('admin_dashboard.html', container=container, admin=admin[0], dashboard=True)


@application.route('/admin/login/', methods=['GET', 'POST'])
def admin_login():
    if 'nia' in session:
        return redirect(url_for('admin'))
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))

    if request.method == "POST":
        nia = request.form["nia"]
        password = request.form["password"]
        
        cur = mysql.connection.cursor()
    
        cur.execute(f"SELECT nia, password FROM admin WHERE nia = '{nia}'")
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user[1], password):
            session["nia"] = user[0]
            return redirect(url_for("admin_dashboard"))
        else:
            return render_template("admin_login.html", error="Invalid NIA or password!")
    return render_template("admin_login.html")

@application.route('/admin/register/', methods=['GET', 'POST'])
def admin_register():
    if 'nia' in session:
        return redirect(url_for('admin'))
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    generated_nia = generate_nia()

    if request.method == "POST":
        nia = request.form["nia"]
        nama = request.form["nama"]

        password = request.form['password']

        confirm_pwd = request.form['confirm_password']

        if password != confirm_pwd:
            return render_template('admin_register.html', nia=generated_nia, error='Passwords do not match!')

        hashed_password = generate_password_hash(password) #Hash the password

        code = request.form["code"]
        if code != SECRET_CODE:
            return render_template('admin_register.html', nia=generated_nia, error="Wrong Code.")

        openDb()
        # SQL SYNTAX untuk memasukan username dan password di tabel karyawan
        cursor.execute(f"INSERT INTO admin(nia, nama, password) values('{nia}', '{nama}', '{hashed_password}')")
        conn.commit()
        closeDb()
        return redirect(url_for("admin_login"))
    
    return render_template('admin_register.html', nia=generated_nia)


@application.route('/admin/messages/')
def admin_messages():
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))
    
    openDb()
    container = []
    cursor.execute(f"SELECT * FROM pesan ORDER BY tgl DESC")
    result = cursor.fetchall()
    for message in result:
        container.append(message)
    closeDb()
    return render_template('admin_messages.html', container=container)

@application.route('/admin/messages/<kode>/')
def admin_message(kode):
    if 'nik' in session:
        return redirect(url_for('user_dashboard'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))
    openDb()
    cursor.execute(f"SELECT * FROM pesan WHERE kode = '{kode}'")
    pesan = cursor.fetchone()
    if not pesan:
        return redirect(url_for('admin_messages'))
    isi = pesan[4].split("\n")
    closeDb()
    return render_template('admin_message.html', pesan=pesan, isi=isi)

@application.route('/admin/tambah_pesan/', methods=['GET', 'POST'])
def admin_tambah_pesan():
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))
    
    kode = generate_pesan()

    if request.method == 'POST':
        openDb()
        cursor.execute(f"SELECT * FROM admin WHERE nia = '{session['nia']}'")
        admin = cursor.fetchone()
        author  = admin[1]
        tgl = datetime.date.today()
        judul = request.form['judul']
        isi = request.form['isi']

        sql = f"INSERT INTO pesan (kode,author,tgl,judul,isi) VALUES ('{kode}', '{author}', '{tgl}', '{judul}', '{isi}')"
        cursor.execute(sql)
        conn.commit()
        closeDb()
        return redirect(url_for('admin_messages'))
    return render_template('admin_tambah_pesan.html')

@application.route('/admin/messages/edit/<kode>')
def admin_edit_pesan(kode):
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))   

@application.route('/admin/messages/hapus/<kode>')
def admin_hapus_pesan(kode):
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))
    openDb()
    cursor.execute(f"DELETE FROM pesan WHERE kode='{kode}'")
    conn.commit()
    closeDb()
    return redirect(url_for('admin_messages'))

@application.route('/admin/logout/')
def admin_logout():
    session.pop('nia', None)
    return redirect(url_for('home'))


#fungsi view tambah() untuk membuat form tambah data
@application.route('/admin/tambah/', methods=['GET','POST'])
def tambah():
    if 'forgot' in session:
        return redirect(url_for('forgot_entry'))
    if 'nik' in session:
        return redirect(url_for('user'))
    if 'nia' not in session:
        return redirect(url_for('admin_login'))

    generated_nik = generate_nik()  # Memanggil fungsi untuk mendapatkan NIK otomatis
    
    if request.method == 'POST':
        nik = request.form['nik']
        password = request.form['password']

        confirm_pwd = request.form['confirm_password']

        if password != confirm_pwd:
            return render_template('tambah_1.html', form_data=request.form, nik=generated_nik, error='Passwords do not match!')

        hashed_password = generate_password_hash(password) #Hash the password

        nama = request.form['nama']
        email = request.form['email']
        alamat = request.form['alamat']
        tgllahir = request.form['tgllahir']
        jeniskelamin = request.form['jeniskelamin']
        status = request.form['status']
        gaji = request.form['gaji']
        foto = request.form['nik']

        # Pastikan direktori upload ada
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Simpan foto dengan nama NIK
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto.filename != '':
                foto.save(os.path.join(application.config['UPLOAD_FOLDER'], f"{nik}.jpg"))

        openDb()
        sql = "INSERT INTO pegawai (nik,password,email,nama,alamat,tgllahir,jeniskelamin,status,gaji,foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val = (nik,hashed_password,email,nama,alamat,tgllahir,jeniskelamin,status,gaji,nik)
        cursor.execute(sql, val)
        conn.commit()
        closeDb()
        return redirect(url_for('admin_dashboard'))        
    else:
        return render_template('tambah.html', nik=generated_nik)  # Mengirimkan NIK otomatis ke template
    
#fungsi view edit() untuk form edit data
@application.route('/admin/edit/<nik>/', methods=['GET','POST'])
def hapus(nik):
    openDb()
    cursor.execute('DELETE FROM pegawai WHERE nik=%s', (nik,))
    # Hapus foto berdasarkan NIK
    path_to_photo = os.path.join(application.root_path, UPLOAD_FOLDER, f'{nik}.jpg')
    if os.path.exists(path_to_photo):
        os.remove(path_to_photo)

    conn.commit()
    closeDb()
    return redirect(url_for('admin_dashboard'))

    
#fungsi view edit() untuk form edit data
@application.route('/edit/<nik>', methods=['GET','POST'])
def edit(nik):
    #Jika belum login sebagai admin tidak ke edit, harus login dulu
    try: nia = session['nia']
    except KeyError: return redirect(url_for('admin'))
    
    try:
        #Jika sudah login sebagai user, tidak bisa ke edit, harus logout dulu
        nik = session['nik']
    except:
        pass
    else:
        return redirect(url_for('user'))
    
    try: forgot = session['forgot']
    except: pass
    else: return redirect(url_for('forgot_entry'))


#fungsi cetak ke PDF
@application.route('/print/<nik>', methods=['GET'])
def get_employee_data(nik):
    # Koneksi ke database
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 password='',  # Password Anda (jika ada)
                                 db='db_pegawai',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            # Query untuk mengambil data pegawai berdasarkan NIK
            sql = "SELECT * FROM pegawai WHERE nik = %s"
            cursor.execute(sql, (nik,))
            employee_data = cursor.fetchone()  # Mengambil satu baris data pegawai

            # Log untuk melihat apakah permintaan diterima dengan benar
            print("Menerima permintaan untuk NIK:", nik)

            # Log untuk melihat data yang dikirim ke klien
            print("Data yang dikirim:", employee_data)

            return jsonify(employee_data)  # Mengembalikan data sebagai JSON

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': 'Terjadi kesalahan saat mengambil data'}), 500

    finally:
        connection.close()  # Menutup koneksi database setelah selesai

#Create Model
class Users(db.Model):
    nik = db.Column(db.Integer, primary_key = True)
    password_hash = db.Column(db.String(128))

    @property
    def password(self):
        raise AttributeError('password is not a readable atribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash)

SECRET_CODE = "1209"

# other functions
def generate_nia():
    # mendefinisikan fungsi openDb(), cursor, dan closeDb() 
    openDb()

    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    # Mengambil empat digit terakhir dari tahun
    year_str = str(current_year).zfill(2)
    
    # Mengambil dua digit dari bulan
    current_month_str = str(current_month).zfill(2)

    # Membuat format nia tanpa nomor urut terlebih dahulu
    base_nia_without_number = f"A-{year_str}{current_month_str}"

    # Mencari nia terakhir dari database untuk mendapatkan nomor urut
    cursor.execute("SELECT nia FROM admin WHERE nia LIKE %s ORDER BY nia DESC LIMIT 1", (f"{base_nia_without_number}%",))
    last_nia = cursor.fetchone()

    if last_nia:
        last_number = int(last_nia[0].split("-")[-1])  # Mengambil nomor urut terakhir
        next_number = last_number + 1
        # Membuat nia lengkap dengan nomor urut
        next_nia = f"A-{str(next_number).zfill(3)}"
    else:
        next_number = 1  # Jika belum ada data, mulai dari 1
        # Membuat nia lengkap dengan nomor urut
        next_nia = f"{base_nia_without_number}{str(next_number).zfill(3)}"
    
    closeDb()  # untuk menutup koneksi database 
    
    return next_nia

#fungsi membuat NIK otomatis
def generate_nik():
    # mendefinisikan fungsi openDb(), cursor, dan closeDb() 
    openDb()

    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    # Mengambil empat digit terakhir dari tahun
    year_str = str(current_year).zfill(2)
    
    # Mengambil dua digit dari bulan
    current_month_str = str(current_month).zfill(2)

    # Membuat format NIK tanpa nomor urut terlebih dahulu
    base_nik_without_number = f"P-{year_str}{current_month_str}"

    # Mencari NIK terakhir dari database untuk mendapatkan nomor urut
    cursor.execute("SELECT nik FROM pegawai WHERE nik LIKE %s ORDER BY nik DESC LIMIT 1", (f"{base_nik_without_number}%",))
    last_nik = cursor.fetchone()

    if last_nik:
        last_number = int(last_nik[0].split("-")[-1])  # Mengambil nomor urut terakhir
        next_number = last_number + 1
        # Membuat NIK lengkap dengan nomor urut
        next_nik = f"P-{str(next_number).zfill(3)}"
    else:
        next_number = 1  # Jika belum ada data, mulai dari 1
        # Membuat NIK lengkap dengan nomor urut
        next_nik = f"{base_nik_without_number}{str(next_number).zfill(3)}"
    
    closeDb()  # untuk menutup koneksi database 
    
    return next_nik


# membuat kode pesan otomatis
def generate_pesan():
    openDb()
    LENGTH = 8

    while True:
        characters = string.ascii_letters + string.digits
        generated_string = ''.join(random.choices(characters, k=LENGTH))
        cursor.execute(f"SELECT kode FROM pesan WHERE kode = '{generated_string}'")
        temp = cursor.fetchone()
        if not temp:
            break
    closeDb()
    return generated_string

#Program utama     
def main():
    application.run(debug=True)

main()