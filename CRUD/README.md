Proyek ini dibuat dalam rangka memenuhi Tugas mata kuliah Pemrograman Berbasis Objek. 

Library yang dibutuhkan untuk menjalankan aplikasi ini di python adalah:
- flask
- flask-sqlalchemy
- flask-mysqldb
- pymysql

Database yang diperlukan: 
1. db_pegawai
   
Table di dalam database: 
1. admin
   a. nia (varchar(11)) PRIMARYKEY
   b. nama (varchar(50))
   c. password (varchar(255))
   d. email (varchar(255))

2. cuti
   a. kode_cuti (varchar(11)) PRIMARYKEY
   b. nik (varchar(11))
   c. nama (varchar(50))
   d. tglawal (date)
   e. tglakhir (date)
   e. alasan (varchar(255))

3. pegawai
   a. nik  (varchar(11)) PRIMARYKEY
   b. nama (varchar(50))
   c. alamat (varchar(30))
   d. tgllahir (date)
   e. jeniskelamin (enum('Pria', 'Wanita'))
   e. status (enum('Sudah Menikah', 'Belum Menikah', 'Pisah'))
   f. gaji (int(11))
   g. foto (varchar(11))
   h. password (varchar(255))
   i. email(varchar(255))
   j. banyakcuti (int(2)) 

4. pesan
   a. kode   (varchar(8)) PRIMARYKEY
   b. author (varchar(11))
   c. tgl (date)
   d. judul (varchar(150))
   e. isi (varchar(4000))
   e. email	(varchar(255))
   f. file	(varchar(255))