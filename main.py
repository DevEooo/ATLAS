import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
import os
import cv2  

ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

class ATLAS(ctk.CTk):
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

        self.title_label = ctk.CTkLabel(self.main_frame, text="LIVE VIEW", font=ctk.CTkFont(size=20, weight="bold")) ## Title
        self.title_label.grid(row=0, column=0, padx=20, pady=10)
        
        self.video_container = ctk.CTkFrame(self.main_frame, fg_color="gray20", width=640, height=480)
        self.video_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 10))
        
        self.video_label = ctk.CTkLabel(self.video_container, text="Memuat kamera... \n Mohon tunggu sebentar!", fg_color="gray20")
        self.video_label.pack(expand=True, fill="both")
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Siap Menerima Absensi", 
                                          fg_color="gray30", corner_radius=5, height=30)
        self.status_label.grid(row=2, column=0, sticky="ew", padx=20, pady=10)

        self.start_video_stream()


    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Menu", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.enroll_button = ctk.CTkButton(self.sidebar_frame, text="Register Wajah", command=self.open_enroller_window)
        self.enroll_button.grid(row=1, column=0, padx=20, pady=10)

        self.log_button = ctk.CTkButton(self.sidebar_frame, text="Log Absensi")
        self.log_button.grid(row=2, column=0, padx=20, pady=10)

        self.exit_button = ctk.CTkButton(self.sidebar_frame, text="Keluar", fg_color="red", hover_color="darkred", command=self.on_closing)
        self.exit_button.grid(row=5, column=0, padx=20, pady=(10, 20))


    def start_video_stream(self):
        print("[INFO] Video stream placeholder is running.")
        
        self.after(3000, lambda: self.status_label.configure(text="Status: Memuat database wajah..."))


    def open_enroller_window(self): ## Def window baru
        if self.enroller_window is None or not self.enroller_window.winfo_exists():
            self.enroller_window = ToplevelEnroller(self)   
        else:
            self.enroller_window.focus()   

    def on_closing(self): ## Jalankan fungsi destroy jika keluar
        if messagebox.askokcancel("Tutup Aplikasi", "Yakin mau keluear dari sistem?"):
            self.destroy()


class ToplevelEnroller(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
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

    def process_enrollment(self):
        nisn = self.nisn_entry.get().strip()
        nama = self.nama_entry.get().strip()
        kelas = self.kelas_entry.get().strip()
        jurusan = self.jurusan_entry.get().strip()

        if not all([nisn, nama, kelas, jurusan]):
            self.status_enroll_label.configure(text="Tolong isi semua fieldnya ya!", text_color="yellow")
            return
        
        self.status_enroll_label.configure(text=f"Merekam wajah untuk {nama}... Cek Webcam!", text_color="green")


if __name__ == "__main__":
    app = ATLAS()
    app.enroller_window = None 
    app.mainloop()