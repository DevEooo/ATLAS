import os, cv2, pickle, sys, face_recognition, numpy as np, tkinter as tk, customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.db_helper import register_pelajar_baru, get_all_known_encodings, get_db_connection
from src.face_capture import mulai_rekam_wajah
from src.exporter import export_log_csv

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

############################################

class ATLAS(ctk.CTk): ## Cam section
    def __init__(self):
        super().__init__()

        self.title("ATLAS - Attendance Tracking and Live Verification System")
        self.geometry("1160x680")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.known_face_encodings = []
        self.known_face_ids = []
        self.known_face_name = []
        self.load_encodings()
        
        self.cd_attendance = {}

        self.buat_sidebar()
        self.buat_main_frame()

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

        self.cap = cv2.VideoCapture(0)
        self.looping_vid()

    def buat_sidebar(self): ## Object untuk membuat semua button di sidebar
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


    def start_video_stream(self, id_pelajar): ## Import variable dari face_capture.py
        print("[INFO]: Video stream placeholder sedang berjalan.")
        
        self.after(3000, lambda: self.status_label.configure(text="Status: Memuat database wajah..."))


    def open_enroller_window(self): ## Def window baru
        if self.enroller_window is None or not self.enroller_window.winfo_exists():
            self.enroller_window = ToplevelEnroller(self)   
        else:
            self.enroller_window.focus()   

    def on_closing(self): ## Jalankan fungsi destroy jika keluar
        if messagebox.askokcancel("Tutup Aplikasi", "Yakin mau keluear dari sistem?"):
            self.cap.release()
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
            
    def load_encodings(self):
        try:
            db_path = os.path.join(os.path.dirname(__file__), 'database', 'face_encoding_pickle')
            if os.path.exists(db_path):
                with open(db_path, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data["encodings"]
                    self.known_face_ids = data["ids"]
                    self.known_face_name = data["names"]
                print(f"[INFO]: Berhasil memuat data wajah {len(self.known_face_encodings)}")
            else:
                print("[WARNING]: File encoding tidak ditemukan, silahkan register.")
        except Exception as e:
            print(f"[ERROR]: Encoding gagal: {e}")
    
    def tandai_attendance(self, pelajar_id, nama_lengkap, jarak):
        sekarang = datetime.now()
        tanggal_hari_ini = datetime.strptime("%d-%m-%Y")
        
        if pelajar_id in self.cd_attendance: # CD Logic
            terakhir = self.cd_attendance[pelajar_id]
            if (sekarang - terakhir).total_seconds() < 3600: ## 3600s = 1h
                return
        
        try: 
            connect = get_db_connection()
            cursor = connect.cursor()
            
            cursor.execute("""
                           INSERT INTO absensi (id_siswa, tanggal_absen, waktu_absen, tipe_absen, akurasi_kecocokan)
                           VALUES (?, ?, ?, ?, ?)
                           """, (pelajar_id, tanggal_hari_ini, sekarang.strftime("%S:%M:%H"), "Masuk", float(jarak)))
            
            connect.commit()
            connect.close()
            
            self.cd_attendance[pelajar_id] = sekarang
            
            self.status_label.configure(text=f"Selamat datang, {nama_lengkap}", fg_color="green")
            print(f"[SUCCESS]: Absen untuk nama {nama_lengkap}")
            
            self.after(3000, lambda: self.status_label.configure(text="Sistem ready."))
            
        except Exception as e:
            print(f"[ERROR]: Gagal menyimpan absensi: {e}")
        
    def buat_main_frame(self):
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.title_label = ctk.CTkLabel(self.main_frame, text="LIVE ATTENDANCE VIEW", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=10)

        self.video_container = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.video_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        self.video_label = ctk.CTkLabel(self.video_container, text="", corner_radius=10)
        self.video_label.pack(expand=True, fill="both")

        self.status_label = ctk.CTkLabel(self.main_frame, text="Sistem Siap. Menunggu Wajah...", 
                                          fg_color="gray30", corner_radius=5, height=40, font=("Arial", 14))
        self.status_label.grid(row=2, column=0, sticky="ew", padx=20, pady=10)
        
    def looping_vid(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # --- VISUAL ROI ---
            center_X, center_Y = w // 2, h // 2
            axes = (160, 220)
            
            mask = np.zeros((h, w, 3), dtype='uint8')
            cv2.ellipse(mask, (center_X, center_Y), axes, 0, 0, 360, (255, 255, 255), -1)
            
            blur_frame = cv2.GaussianBlur(frame, (21, 21), 0)
            dimmed_bg = cv2.addWeighted(blur_frame, 0.5, np.zeros(frame.shape, frame.dtype), 0, 0)
            
            mask_inv = cv2.bitwise_not(cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
            face_area = cv2.bitwise_and(frame, frame, mask=cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY))
            bg_area = cv2.bitwise_and(dimmed_bg, dimmed_bg, mask=mask_inv)
            final_frame = cv2.add(face_area, bg_area)
            
            default_border = (255, 255, 0) # Cyan
            
            crop_Y1, crop_Y2 = center_Y - axes[1], center_Y + axes[1]
            crop_X1, crop_X2 = center_X - axes[0], center_X + axes[0]
            
            if crop_X1 > 0 and crop_Y1 > 0 and crop_X2 < w and crop_Y2 < h:
                roi_frame = frame[crop_Y1:crop_Y2, crop_X1:crop_X2]
                rgb_roi = cv2.cvtColor(roi_frame, cv2.COLOR_BGR2RGB)
                
                face_locations = face_recognition.face_locations(rgb_roi)
                
                if face_locations:
                    default_border = (0, 255, 255) # Kuning (Processing)
                    
                    # [FIX CRASH 1]: Cek dulu apakah database kosong?
                    if len(self.known_face_encodings) > 0:
                        face_encodings = face_recognition.face_encodings(rgb_roi, face_locations)
                        
                        for face_encoding in face_encodings:
                            # Hitung jarak
                            jarak_face = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                            
                            # [FIX CRASH 2]: Pastikan jarak_face tidak kosong sebelum argmin
                            if len(jarak_face) > 0:
                                index_kecocokan_terbaik = np.argmin(jarak_face)
                                jarak = jarak_face[index_kecocokan_terbaik]
                                
                                # Logika Match
                                if jarak < 0.50:
                                    nama = self.known_face_name[index_kecocokan_terbaik]
                                    p_id = self.known_face_ids[index_kecocokan_terbaik] 
                                    
                                    default_border = (0, 255, 0) # Hijau
                                    cv2.putText(final_frame, f"{nama}", (center_X - 50, center_Y + axes[1] + 30), 
                                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                                    
                                    self.tandai_attendance(p_id, nama, jarak)
                                    
                                elif jarak < 0.65:
                                    default_border = (0, 165, 255) # Orange
                                    self.status_label.configure(text="⚠️ Wajah kurang jelas.", fg_color="orange")
                                else:
                                    default_border = (0, 0, 255) # Merah (Unknown)
                                    self.status_label.configure(text="⛔ Wajah tidak dikenali", fg_color="red")
                            else:
                                # Jika error perhitungan
                                default_border = (0, 0, 255)
                    else:
                        default_border = (0, 0, 255) 
                        self.status_label.configure(text="⚠️ Database Kosong. Silakan Register dulu.", fg_color="orange")
                        cv2.putText(final_frame, "DATABASE KOSONG", (center_X - 70, center_Y + axes[1] + 30), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            cv2.ellipse(final_frame, (center_X, center_Y), axes, 0, 0, 360, default_border, 3)
            
            # [FIX UI]: Menggunakan CTkImage (Best Practice CustomTkinter)
            # Konversi BGR -> RGB
            rgb_image = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(rgb_image)
            
            # Bungkus dengan CTkImage agar HighDPI friendly
            # Size disesuaikan dengan ukuran frame kamera asli atau ukuran container
            ctk_img = ctk.CTkImage(light_image=pil_image, dark_image=pil_image, size=(w, h))
            
            self.video_label.configure(image=ctk_img)
            self.video_label.image = ctk_img # Keep reference agar tidak dibuang garbage collector
            
        self.after(20, self.looping_vid)

####################################################

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