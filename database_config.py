import sqlite3, os

DB_FOLDER = "database"
DB_NAME = "atlas.db"
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def create_table():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"[ERROR]: Folder {DB_FOLDER} gagal dibuat")
    else:
        print(f"[INFO]: Database {DB_NAME} berhasil dibuat di {DB_FOLDER}")
   
        
    try: 
        connect = sqlite3.connect(DB_PATH)
        cursor = connect.cursor()
        print(f"[INFO]: Terhubung dengan {DB_PATH}")

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS siswa (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                nisn TEXT UNIQUE NOT NULL,
                nama_lengkap VARCHAR(100) NOT NULL, 
                kelas VARCHAR(20) NOT NULL,
                jurusan VARCHAR(50) NOT NULL, 
                status TEXT DEFAULT 'Aktif NULLABLE'
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_wajah (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_siswa INTEGER NOT NULL,
                encoding_wajah BLOB NOT NULL, 
                path_raw_photo VARCHAR(255) NOT NULL,
                FOREIGN KEY (id_siswa) REFERENCES siswa(id) ON DELETE CASCADE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS absensi (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                id_siswa INTEGER NOT NULL,
                tanggal_absen DATE NOT NULL, 
                waktu_absen TIMESTAMP NOT NULL, 
                tipe_absen TEXT NOT NULL,
                akurasi_kecocokan FLOAT NOT NULL,
                FOREIGN KEY (id_siswa) REFERENCES siswa(id) ON DELETE CASCADE
            )
        ''')
        
        connect.commit()
        print(f"[INFO]: Tabel berhasil dibuat")
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        
    finally:
        if connect:
            connect.close()
            
if __name__ == "__main__":
    create_table()