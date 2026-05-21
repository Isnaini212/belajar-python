import os
import subprocess
import sys
import tkinter as tk
from tkinter import messagebox


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def warnai_widget(widget, warna_bg, warna_panel, warna_aksen):
    if isinstance(widget, tk.Label):
        widget.configure(bg=warna_bg, fg="#1f2933")
    elif isinstance(widget, tk.LabelFrame):
        widget.configure(bg=warna_panel, fg="#1f2933", font=("Arial", 10, "bold"))
    elif isinstance(widget, tk.Frame):
        widget.configure(bg=warna_bg)
    elif isinstance(widget, tk.Button):
        widget.configure(
            bg=warna_aksen,
            fg="white",
            activebackground="#f8d7da",
            activeforeground="#1f2933",
            font=("Arial", 9, "bold")
        )

    for child in widget.winfo_children():
        warnai_widget(child, warna_bg, warna_panel, warna_aksen)


def buka_modul(nama_file):
    path_file = os.path.join(BASE_DIR, nama_file)

    if not os.path.exists(path_file):
        messagebox.showerror("Error", "File tidak ditemukan: " + nama_file)
        return

    try:
        subprocess.Popen([sys.executable, path_file], cwd=BASE_DIR)
    except Exception as error:
        messagebox.showerror("Error", "Gagal membuka modul:\n" + str(error))


def keluar_aplikasi():
    if messagebox.askyesno("Konfirmasi", "Yakin ingin keluar dari aplikasi?"):
        root.destroy()


root = tk.Tk()
root.title("Menu Utama Akademik dan Payroll")
root.geometry("520x320")
root.resizable(False, False)
root.configure(bg="#f7edf2")

judul = tk.Label(
    root,
    text="MENU UTAMA",
    font=("Arial", 18, "bold")
)
judul.pack(pady=18)

frame_menu = tk.Frame(root)
frame_menu.pack(padx=20, pady=5, fill="both", expand=True)

frame_master = tk.LabelFrame(frame_menu, text="Menu Master", padx=15, pady=15)
frame_master.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

tk.Button(
    frame_master,
    text="Data Mahasiswa",
    width=22,
    command=lambda: buka_modul("mahasiswa.py")
).pack(pady=5)

tk.Button(
    frame_master,
    text="Data Employees",
    width=22,
    command=lambda: buka_modul("employees.py")
).pack(pady=5)

tk.Button(
    frame_master,
    text="Data Matakuliah",
    width=22,
    command=lambda: buka_modul("matakuliah.py")
).pack(pady=5)

frame_transaksi = tk.LabelFrame(frame_menu, text="Menu Transaksi", padx=15, pady=15)
frame_transaksi.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

tk.Button(
    frame_transaksi,
    text="Entry KRS",
    width=22,
    command=lambda: buka_modul("krs.py")
).pack(pady=5)

tk.Button(
    frame_transaksi,
    text="Entry Payroll",
    width=22,
    command=lambda: buka_modul("payroll.py")
).pack(pady=5)

frame_menu.grid_columnconfigure(0, weight=1)
frame_menu.grid_columnconfigure(1, weight=1)

tk.Button(
    root,
    text="Keluar",
    width=15,
    command=keluar_aplikasi
).pack(pady=12)

warnai_widget(root, "#f7edf2", "#f3c7d8", "#b5446e")

root.mainloop()