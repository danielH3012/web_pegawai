import pymysql.cursors, os
import datetime

from flask import Flask, jsonify, redirect, render_template, request, url_for

application = Flask(__name__)

conn = cursor = None
global cons,cons2
cons = True
cons2 = True

@application.route('/')
def awal():
    return render_template("home.html")

@application.route('/hrd', methods=['GET','POST'])
def login():
    global cons 
    cons = True
    if request.method == 'POST':
        nama = request.form['nama']
        password = request.form['pw']
        if(nama != 'admin' or password != 'adminadmin'):
            return render_template('loginsalah.html')
        else:
            cons = True
            return redirect('/index')
    else:
        return render_template("login.html")
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

#fungsi view index() untuk menampilkan data dari basis data
@application.route('/index')
def index():   
    if cons:
        openDb()
        container = []
        sql = "SELECT * FROM pegawai ORDER BY NIK DESC;"
        cursor.execute(sql)
        results = cursor.fetchall()
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month
        current_day = datetime.datetime.now().day
        current = datetime.date(int(current_year), int(current_month), int(current_day))
        for data in results:
         mulai = data[10].split('-')
         selesai = data[11].split('-')
         if(len(mulai) > 2):
          if((datetime.date(int(mulai[0]), int(mulai[1]),int(mulai[2]))<= current and
            datetime.date(int(selesai[0]), int(selesai[1]),int(selesai[2])) >= current)):
             sql = "UPDATE pegawai SET cuti=%s WHERE nik=%s"
             val = ('YES',data[0])
             cursor.execute(sql, val)
          else:
             sql = "UPDATE pegawai SET cuti=%s WHERE nik=%s"
             val = ('NO',data[0])
             cursor.execute(sql, val)
         container.append(data)
        
        if(current_day == 1 and current_month==1):
            sql = "UPDATE pegawai SET cuti=%s"
            val = 30
            cursor.execute(sql,30)
            conn.commit()
        closeDb()
        return render_template('index.html', container=container,)
    else:
        return redirect('/hrd')


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

#fungsi untuk menyimpan lokasi foto
UPLOAD_FOLDER = 'C:/Users/USER/AppData/Local/Programs/Python/Python312/dataflask/web_pegawai/crud/static/foto/'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#fungsi view tambah() untuk membuat form tambah data
@application.route('/tambah', methods=['GET','POST'])
def tambah():
    if cons:
        generated_nik = generate_nik()  # Memanggil fungsi untuk mendapatkan NIK otomatis
    
        if request.method == 'POST':
            nik = request.form['nik']
            nama = request.form['nama']
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
                    foto.save(os.path.join(application.config['UPLOAD_FOLDER'],f"{nik}.jpg"))

            openDb()
            sql = "INSERT INTO pegawai (nik,nama,alamat,tgllahir,jeniskelamin,status,gaji,foto) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (nik,nama,alamat,tgllahir,jeniskelamin,status,gaji,nik)
            cursor.execute(sql, val)
            conn.commit()
            sql = "INSERT INTO password (nik,password) VALUES (%s, %s)"
            val = (nik,nik)
            cursor.execute(sql, val)
            sql = "UPDATE password SET password=SHA(%s) WHERE nik=%s"
            val = (nik,nik)
            cursor.execute(sql, val)
            conn.commit()
            closeDb()
            return redirect(url_for('index'))        
        else:
            return render_template('tambah.html', nik=generated_nik)  # Mengirimkan NIK otomatis ke template
    else:
        return redirect('/hrd')
    
#fungsi view edit() untuk form edit data
@application.route('/edit/<nik>', methods=['GET','POST'])
def edit(nik):
    if cons:
        openDb()
        cursor.execute('SELECT * FROM pegawai WHERE nik=%s', (nik))
        data = cursor.fetchone()
        if request.method == 'POST':
            nik = request.form['nik']
            nama = request.form['nama']
            alamat = request.form['alamat']
            tgllahir = request.form['tgllahir']
            jeniskelamin = request.form['jeniskelamin']
            status = request.form['status']
            gaji = request.form['gaji']
            foto = request.form['nik']

            path_to_photo = os.path.join(application.root_path, 'C:/Users/user/AppData/Local/Programs/Python/Python311/Scripts/dataflask/web_pegawai/crud/static/foto/', f'{nik}.jpg')
            if os.path.exists(path_to_photo):
                os.remove(path_to_photo)

        # Pastikan direktori upload ada
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)

        # Simpan foto dengan nama NIK
            if 'foto' in request.files:
                foto = request.files['foto']
                if foto.filename != '':
                    foto.save(os.path.join(application.config['UPLOAD_FOLDER'], f"{nik}.jpg"))
            sql = "UPDATE pegawai SET nama=%s, alamat=%s, tgllahir=%s, jeniskelamin=%s, status=%s, gaji=%s, foto=%s WHERE nik=%s"
            val = (nama, alamat, tgllahir,jeniskelamin, status, gaji, foto, nik)
            cursor.execute(sql, val)
            conn.commit()
            closeDb()
            return redirect(url_for('index'))
        else:
            closeDb()
            return render_template('edit.html', data = data)
    else:
        return redirect('/hrd')

#fungsi menghapus data
@application.route('/hapus/<nik>', methods=['GET','POST'])
def hapus(nik):
        openDb()
        cursor.execute('DELETE FROM pegawai WHERE nik=%s', (nik,))
        cursor.execute('DELETE FROM password WHERE nik=%s', (nik,))
    # Hapus foto berdasarkan NIK
        path_to_photo = os.path.join(application.root_path, 'C:/Users/user/AppData/Local/Programs/Python/Python311/Scripts/dataflask/web_pegawai/crud/static/foto/', f'{nik}.jpg')
        if os.path.exists(path_to_photo):
            os.remove(path_to_photo)

        conn.commit()
        closeDb()
        return redirect(url_for('index'))


#fungsi cetak ke PDF
@application.route('/get_employee_data/<nik>', methods=['GET'])
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

@application.route('/cuti/<nik>', methods=['GET','POST'])
def cuti(nik):
    if cons:
        openDb()
        cursor.execute('SELECT * FROM pegawai WHERE nik=%s', (nik))
        data = cursor.fetchone()
        print(request)
        if request.method == 'POST':
            day = request.form['tgl1']
            month = request.form['bulan1']
            year = request.form['tahun1']

            day2 = request.form['tgl2']
            month2 = request.form['bulan2']
            year2 = request.form['tahun2']

            total = request.form['jatah']
            d1 = datetime.date(int(year2), int(month2),int(day2))
            d2 = datetime.date(int(year), int(month), int(day))
            current_year = datetime.datetime.now().year
            current_month = datetime.datetime.now().month
            current_day = datetime.datetime.now().day
            current = datetime.date(int(current_year), int(current_month), int(current_day))

            result = (d1-d2).days
            sisa = int(total) - result
 
            if(sisa > 0 and d2 < d1 and current < d2):
                sql = "UPDATE pegawai SET jatahCuti=%s, mulaiCuti=%s, selesaiCuti=%s WHERE nik=%s"
                val = (str(sisa),str(d2),str(d1),nik)
                cursor.execute(sql, val)
                conn.commit()
                closeDb()
                return redirect(url_for('index'))
            else:
                closeDb()
                return render_template('cuti.html', data=data)
        else:
            closeDb()
            return render_template('cuti.html', data=data)
    else:
        return redirect('/hrd')  
    
@application.route('/pegawai', methods=['GET','POST'])
def login2():
    global cons2 
    cons2 = False
    openDb()
    try:
        if request.method == 'POST':
            nik = request.form['nama']
            password = request.form['pw']
            cursor.execute('SELECT * FROM password WHERE nik=%s', nik)
            data = cursor.fetchone()
            val = [nik,password]
            cursor.execute('SELECT COUNT(*) FROM password WHERE nik = %s && password = SHA(%s);',val)
            data2 = cursor.fetchone()
            print(data2)
            if data2[0] <= 0:
                closeDb()
                return redirect('/pegawai')
            else:
                closeDb()
                cons2 = True
                return redirect(url_for('home', nik=data[0]))
    except:
            #closeDb()
            #return render_template('pegawai.html')
            print('error')
    closeDb()
    return render_template("pegawaisalah.html")

@application.route('/home/<nik>', methods=['GET','POST'])
def home(nik):
    if cons2:
        openDb()
        cursor.execute('SELECT * FROM pegawai WHERE nik=%s', (nik))
        data = cursor.fetchone()
        jatah = data[8]
        statusCuti = data[9]
        nama = data[1]
        return render_template("beranda.html",data = data)
    else:
        return redirect('/pegawai')  
    
@application.route('/profil/<nik>', methods=['GET','POST'])
def profil(nik):
    if cons2:
        openDb()
        cursor.execute('SELECT * FROM pegawai WHERE nik=%s', (nik))
        data = cursor.fetchone()
        return render_template("profil.html",row = data)
    else:
        return redirect('/pegawai')  
    
@application.route('/pw/<nik>', methods=['GET','POST'])
def pw(nik):
    if cons2:
        openDb()
        
        print(request)
        if request.method == 'POST':
            pw = request.form['pw']
            sql = "UPDATE password SET password=SHA(%s) WHERE nik=%s"
            val = (pw,nik)
            cursor.execute(sql, val)
            conn.commit()
            closeDb()
            return redirect(url_for('home', nik=nik))
        else:
            closeDb()
            return render_template('pw.html',nik = nik)
    else:
        return redirect('/pegawai')
    
@application.route('/pengumuman(admin)', methods=['GET','POST'])
def pa():
    if cons:
        openDb()
        print(request)
        container=[]
        if request.method == 'POST':
            judul = request.form['judul']
            isi = request.form['isi']
            sql = "INSERT INTO pesan (judul, isi) VALUES (%s,%s)"
            val = (judul,isi)
            cursor.execute(sql, val)
            conn.commit()
            closeDb()
            return redirect('/index')
        else:
            sql = "SELECT * FROM pesan"
            cursor.execute(sql)
            result = cursor.fetchall()
            for data in result:
                container.append(data)
            closeDb()
            return render_template('peng1.html', data = container)
    else:
        return redirect('/hrd')
    
@application.route('/pengumuman')
def pengumuman():
    if cons2:
        openDb()
        container = []
        sql = "SELECT * FROM pesan;"
        cursor.execute(sql)
        results = cursor.fetchall()
        for data in results:
            container.append(data)
        closeDb()
        return render_template('berpeng.html', data = container)
    else:
        closeDb()
        return redirect('/pegawai')
    
@application.route('/berita/<judul>', methods=['GET','POST'])
def berita(judul):
    if cons2:
        openDb()
        cursor.execute('SELECT * FROM pesan WHERE judul=%s', (judul))
        data = cursor.fetchone()
        closeDb()
        return render_template('peng2.html', data = data)
    else:
        closeDb()
        return redirect('/pegawai')
    
@application.route('/hapus_ber/<judul>', methods=['GET','POST'])
def hapus_ber(judul):
        openDb()
        cursor.execute('DELETE FROM pesan WHERE judul=%s', (judul))
        conn.commit()
        closeDb()
        return redirect('/pengumuman(admin)')

@application.route('/japri/<nik>', methods=['GET','POST'])
def japri(nik):
    if cons2:
        openDb()
        cursor.execute('SELECT * FROM private_chat WHERE nik=%s', (nik))
        data = cursor.fetchall()
        closeDb()
        return render_template('japri.html', data = data)
    else:
        closeDb()
        return redirect('/pegawai')
    
@application.route('/prifat/<nik>', methods=['GET','POST'])
def prifat(nik):
        openDb()
        print(request)
        print(openDb())
        container=[]
        if request.method == 'POST':
            openDb()
            isi = request.form['isi']
            sql = "INSERT INTO private_chat (isi,nik) VALUES (%s,%s)"
            val = (isi,nik)
            cursor.execute(sql, val)
            conn.commit()
            closeDb()
            return redirect('/index')
        else:
            sql = "SELECT * FROM private_chat WHERE nik = %s"
            cursor.execute(sql,nik)
            result = cursor.fetchall()

            for data in result:
                container.append(data)
            print(container)
            closeDb()
            return render_template('prifat.html', data = container, nik = nik)
#Program utama      
if __name__ == '__main__':
    application.run(debug=True)
