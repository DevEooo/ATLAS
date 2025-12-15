import sqlite3, os

DB_FOLDER = 'database'
DB_NAME = 'atlas'
DB_PATH = os.path.join(DB_FOLDER, DB_NAME)

def get_db_connection():
    connect = sqlite3.connect(DB_PATH)
    return connect 

def register_pelajar_baru(nisn, nama_lengkap, kelas, jurusan):
    connect = get_db_connection()
    cursor = connect.cursor()
    try:
        cursor.execute("""
                       INSERT INTO siswa (nisn, nama_lengkap, kelas, jurusan, status)
                       VALUES (?, ?, ?, ?, ?)
                       """), (nisn, nama_lengkap, kelas, jurusan)
        id_baru = cursor.lastrowid
        connect.commit()
        return id_baru
    except sqlite3.IntegrityError:
        print("[ERROR]: NISN sudah exist")
        return None 
    except Exception as e: 
        print(f"[ERROR]: Terjadi kesalahan database {e}")
    finally:
        connect.close()
        
def get_all_known_encodings():
    import pickle 
    ENCODING_FILE = os.path.join(DB_FOLDER, 'face_encodings.pickle')
    
    if os.path.exists(ENCODING_FILE):
        with open(ENCODING_FILE, 'rb') as f:
            return pickle.load(f)
    else:
        return {"encodings": [], "ids": [], "names": []}