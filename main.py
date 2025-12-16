import os, cv2, pickle, sys, face_recognition, numpy as np, tkinter as tk, customtkinter as ctk
from tkinter import messagebox

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.db_helper import register_pelajar_baru, get_all_known_encodings
from src.face_capture import mulai_rekam_wajah
from src.exporter import export_log_csv

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class ATLAS(ctk.CTk): ## Cam section
    def __init__(self):
        super().__init__()

        self.title("ATLAS - Attendance Tracking and Live Verification System")
        self.geometry("1160x680")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_sidebar()

        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        self.video_container = ctk.CTkFrame(self.main_frame, fg_color="gray20", width=640, height=480)
        self.video_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        self.video_label = ctk.CTkLabel(self.video_container, text="Memuat kamera... \n Mohon tunggu sebentar!", fg_color="gray20")
        self.video_label.pack(expand=True, fill="both")
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Siap Menerima Absensi", fg_color="gray30", corner_radius=5, height=30)
        self.status_label.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        self.start_video_stream()

    def create_sidebar(self): ## Object untuk membuat semua button di sidebar
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Menu", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.enroll_button = ctk.CTkButton(self.sidebar_frame, text="Register Wajah", command=self.open_enroller_window)
        self.enroll_button.grid(row=1, column=0, padx=20, pady=10)

        self.log_button = ctk.CTkButton(self.sidebar_frame, text="Log Absensi")
        self.log_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.download_button = ctk.CTkButton(self.sidebar_frame, text="Download", command=self.download_action)
        self.download_button.grid(row=5, column=0, padx=20, pady=(10, 65))

        self.exit_button = ctk.CTkButton(self.sidebar_frame, text="Keluar", fg_color="red", hover_color="darkred", command=self.on_closing)
        self.exit_button.grid(row=5, column=0, padx=20, pady=(35, 0))


    def start_video_stream(self):
        print("[INFO]: Video stream placeholder sedang berjalan.")
        
        self.after(3000, lambda: self.status_label.configure(text="Status: Memuat database wajah..."))


    def open_enroller_window(self): ## Def window baru
        if self.enroller_window is None or not self.enroller_window.winfo_exists():
            self.enroller_window = ToplevelEnroller(self)   
        else:
            self.enroller_window.focus()   

    def on_closing(self): ## Jalankan fungsi destroy jika keluar
        if messagebox.askokcancel("Tutup Aplikasi", "Yakin mau keluear dari sistem?"):
            self.destroy()
            
    def download_action(self): ## Aksi download apabila PIN benar
        dialog = ctk.CTkInputDialog(text="Masukan PIN untuk download log", title="PIN Keamanan")
        pin = dialog.get_input()
        
        if pin == "NurulFikri":
            success, message = export_log_csv()
            
            if success:
                messagebox.showinfo("Berhasil!", message)
            else:
                messagebox.showinfo("Gagal", message)
        elif pin is None:
            pass
        else:
            messagebox.showinfo("PIN Salah", "Akses ditolak")


class ToplevelEnroller(ctk.CTkToplevel): 
    
    def __init__(self, *args, **kwargs): ## Form
        super().__init__(*args, **kwargs)
        self.title("ATLAS - Pendaftaran Wajah Baru")
        self.geometry("500x500")
        
        self.grab_set() 
        
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        ctk.CTkLabel(self.form_frame, text="Form Pendaftaran Siswa/i", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(10, 15))

        ctk.CTkLabel(self.form_frame, text="NISN (Nomor Induk Siswa/i Nasional):").pack(pady=(10, 0))
        self.nisn_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Contoh: 12345")
        self.nisn_entry.pack(fill="x", padx=40)
        
        ctk.CTkLabel(self.form_frame, text="Nama Lengkap:").pack(pady=(10, 0))
        self.nama_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Nama Lengkap")
        self.nama_entry.pack(fill="x", padx=40)

        ctk.CTkLabel(self.form_frame, text="Kelas:").pack(pady=(10, 0))
        self.kelas_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Contoh: XII")
        self.kelas_entry.pack(fill="x", padx=40)
        
        ctk.CTkLabel(self.form_frame, text="Jurusan:").pack(pady=(10, 0))
        self.jurusan_entry = ctk.CTkEntry(self.form_frame, placeholder_text="Contoh: PPLG 1")
        self.jurusan_entry.pack(fill="x", padx=40)
        
        self.start_enroll_button = ctk.CTkButton(self.form_frame, text="Mulai Rekam Wajah", command=self.process_enrollment)
        self.start_enroll_button.pack(pady=30)
        
        self.status_enroll_label = ctk.CTkLabel(self.form_frame, text="", text_color="yellow")
        self.status_enroll_label.pack()
        
    def get_all_known_encodings():
        DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        ENCODING_FILE = os.path.join(DB_FOLDER, 'face_encodings.pickle')
        
        if os.path.exists(ENCODING_FILE):
         with open(ENCODING_FILE, 'rb') as f:
            return pickle.load(f)
        else:
            return {"encodings": [], "ids": [], "names": []}
    
    def mulai_rekam_wajah(nisn, nama_lengkap, kelas, jurusan, status):
        DB_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database')
        ENCODING_FILE = os.path.join(DB_FOLDER, 'face_encodings.pickle')
    
        id_pelajar = register_pelajar_baru(nisn, nama_lengkap, kelas, jurusan, status)
        if id_pelajar is None:
            return False, "Pendaftaran gagal, ID Pelajar tidak ditemukan."

        print(f"\n[INFO]: Siswa/i dengan nama {nama_lengkap} terdaftar dengan ID: {id_pelajar}. Mulai merekam...")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Gagal membuka kamera, pastikan kamera tidak digunakan aplikasi lain."

        SAMPLE_COUNT_TARGET = 7
        samples_captured = 0 
        encodings_list = []

        while samples_captured < SAMPLE_COUNT_TARGET:
            ret, frame = cap.read()
            if not ret: break 

            frame = cv2.flip(frame, 1)

            cv2.putText(frame, f"Siswa/i: {nama_lengkap} | Sampel: {samples_captured} / {SAMPLE_COUNT_TARGET}", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            cv2.putText(frame, "Tekan 'S' untuk ambil sample", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

            cv2.imshow("ATLAS Perekam Wajah (Tekan Esc untuk batal)", frame)

            key = cv2.waitKey(1) & 0xFF

            if key == ord('s'):
                face_locations = face_recognition.face_locations(frame)
                if len(face_locations) == 1:
                    face_encoding = face_recognition.face_encodings(frame, face_locations)

                    if face_encoding: 
                        encodings_list.append(face_encoding[0])
                        samples_captured += 1 

                        cv2.putText(frame, "Direkam!", (10, 400), cv2.FONT_HERSHEY_SCRIPT_SIMPLEX, 1, (0, 0, 255), 3)
                        cv2.imshow(frame, "ATLAS Perekam Wajah (Tekan Esc untuk batal.)")
                        cv2.waitKey(500)

            elif len(face_locations) > 1:
                print(" [WARNING]: Wajah terdeteksi lebih dari 1.")
            else: 
                print(" [WARNING]: Wajah tidak terdeteksi")

            if key == ord('esc'):
                break
            
            cap.release()
            cv2.destroyAllWindows()

            if len(encodings_list) >= SAMPLE_COUNT_TARGET:
                avg_encoding = np.mean(encodings_list, axis=0)

                data = get_all_known_encodings()
                data["encodings"].append(avg_encoding)
                data["ids"].append(id_pelajar)
                data["names"].append(nama_lengkap)

                with open(ENCODING_FILE, 'wb') as f:
                    pickle.dump(data, f)

                return True, f"Wajah dengan nama {nama_lengkap} berhasil didaftarkan! Total {len(data['encodings'])} data."

            else:
                return False, "Pendaftaran wajah dibatalkan/kurang sampel."
        
    def process_enrollment(self):
            nisn = self.nisn_entry.get().strip()
            nama = self.nama_entry.get().strip()
            kelas = self.kelas_entry.get().strip()
            jurusan = self.jurusan_entry.get().strip()

            if not all([nisn, nama, kelas, jurusan]):
                self.status_enroll_label.configure(text="Tolong isi semua fieldnya ya!", text_color="yellow")
                return

            self.status_enroll_label.configure(text=f"Merekam wajah untuk {nama}...", text_color="green")
            self.update()
            
            success, message = mulai_rekam_wajah(nisn, nama, kelas, jurusan)
            
            if success:
                self.status_enroll_label.configure(text=f"Berhasil, {message}", text_color="green")
            else:
                self.status_enroll_label.configure(text=f"Gagal, {message}", text_color="red")
                self.nisn_entry.delete(0, 'end')


if __name__ == "__main__":
    app = ATLAS()
    app.enroller_window = None 
    app.mainloop()