import sqlite3, csv, os
from datetime import datetime
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, 'database', 'atlas.db')

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def export_log_csv():
    if not os.path.exists(DB_FILE):
        return False, "[FAIL]: Database tidak ditemukan"
    
    try:
        connect = sqlite3.connect(DB_FILE)
        cursor = connect.cursor()
        
        query = """
            SELECT absensi.tanggal_absen, 
            absensi.waktu_absen,
            siswa.nama_lengkap,
            siswa.kelas,
            siswa.jurusan,
            absensi.tipe_absen,
            absensi.akurasi_kecocokan
            FROM absensi JOIN siswa ON absensi.id_siswa = siswa.id
            ORDER BY absensi.id DESC 
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            return False, "Data absensi masih kosong"
        
        filename = f"Log_Absensi_ATLAS{get_timestamp()}.csv"
        output_path = os.path.join(BASE_DIR, filename)
        
        with open(output_path, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Tanggal", "Jam", "Nama Siswa", "Kelas", "Status", "Akurasi"])
            writer.writerow(rows)
            
        return True, f"Data berhasil disimpan di \n {filename}" 
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        
    finally: 
        if connect:
            connect.close()

def export_data_pelajar():
    
    if not os.path.exists(DB_FILE):
        return False, "[FAIL]: Database tidak ditemukan"
    
    try:
        connect = sqlite3.connect(DB_FILE)
        cursor = connect.cursor()
        
        cursor.execute("SELECT id, nisn, nama_lengkap, kelas, jurusan, status FROM siswa")
        row = cursor.fetchall()
        
        if not row:
            return False, "Belum ada Siswa/i yang terdaftar"
        
        filename = f"Daftar_Pelajar_{get_timestamp()}.csv"
        output_path = os.path.join(BASE_DIR, filename)
        
        with open(output_path, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["ID", "NISN", "Nama Lengkap", "Kelas", "Jurusan", "Status"])
            writer.writerow(row)
            
        return True, f"File berhasil disimpan di: \n {filename}"
        
    except Exception as e:
        print(f"[ERROR]: {e}")
        
    finally: 
        if connect:
            connect.close()
            
            