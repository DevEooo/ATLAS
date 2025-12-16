import sqlite3, os, csv

DB_FILE = os.path.join("database", "atlas.db")
OUTPUT = "ATLAS.csv"

def export_data():
    if not os.path.exists(DB_FILE):
        print("[ERROR]: File .db tidak ditemukan.")
        return
    
    try:
        connect = sqlite3.connect(DB_FILE)
        cursor = connect.cursor()
        
        print(f"[INFO]: Mengumpulkan semua data {DB_FILE}...")
        
        query = "SELECT * FROM siswa"        
        cursor.execute(query)
        
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]
        
        with open(OUTPUT, 'w', newline='', encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(columns)
            writer.writerow(rows)
            
        print(f"[BERHASIL]: Data diexport ke: {OUTPUT}")
            
    except sqlite3.OperationalError:
        print(f"[ERROR]: Tabel belum dibuat atau mungkin kerusakan pada database.")
    except Exception as e:
        print(f"[ERROR]: {e}")
    finally:
        if connect:
            connect.close()
            
if __name__ == "__main__":
    export_data()