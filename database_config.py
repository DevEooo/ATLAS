import sqlite3, os

DB_FOLDER = "database"
DB_NAME = "atlas"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def create_table():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"[INFO] Folder {DB_FOLDER} berhasil dibuat")
    else:
        print(f"[INFO] Folder {DB_FOLDER} gagal dibuat")
        
    connect = sqlite3.connect(DB_PATH)
    cursor = connect.cursor()
    
    if(connect):
        print(f"[INFO] Sedang membuat table di {DB_PATH}")
    else: 
        print(f"[FAIL] Gagal membuat table")
        
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS siswa (
                       id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       nisn INTEGER(10) UNIQUE NOT NULL,
                       nama_lengkap VARCHAR(100) NOT NULL, 
                       kelas VARCHAR(20) NOT NULL,
                       jurusan VARCHAR(50) NOT NULL, 
                       status ENUM('Aktif', '')
                   )
                   ''')
    
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS data_wajah (
                       id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       id_siswa INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
                       encoding_wajah BLOB NOT NULL, 
                       path_raw_photo VARCHAR(255) NOT NULL
                   )
                   ''')
    
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS absensi (
                       id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       id_siswa INTEGER NOT NULL REFERENCES siswa(id) ON DELETE CASCADE,
                       tanggal_absen DATE NOT NULL, 
                       waktu_absen TIMESTAMP NOT NULL, 
                       tipe_absen ENUM('Masuk', 'Pulang'),
                       akurasi_kecocokan FLOAT NOT NULL
                   )
                   ''')
    
    connect.commit()
    connect.close()
    print(f"[SUCCESS] Table berhasil dibuat di {DB_PATH}")
    
    if __name__ == "__main__":
        create_table()