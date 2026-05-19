# kode program untuk membuat modul mahasiswa.py

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3

# Koneksi database
conn = sqlite3.connect("AKADEMIKDB.db")
cursor = conn.cursor()

# =========================
# Membuat Fungsi CRUD
# =========================

def tampil_data():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("SELECT nim, nama, jurusan, fakultas FROM mahasiswa")
    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def simpan_data():
    nim = entry_nim.get()
    nama = entry_nama.get()
    jurusan = entry_jurusan.get()
    fakultas = entry_fakultas.get()

    if nim == "" or nama == "" or jurusan == "" or fakultas == "":
        messagebox.showwarning("Peringatan", "Semua data harus diisi")
        return

    try:
        cursor.execute("""
            INSERT INTO mahasiswa (nim, nama, jurusan, fakultas)
            VALUES (?, ?, ?, ?)
        """, (nim, nama, jurusan, fakultas))

        conn.commit()
        messagebox.showinfo("Sukses", "Data berhasil disimpan")
        bersihkan_form()
        tampil_data()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "NIM sudah terdaftar")


def update_data():
    nim = entry_nim.get()
    nama = entry_nama.get()
    jurusan = entry_jurusan.get()
    fakultas = entry_fakultas.get()

    if nim == "":
        messagebox.showwarning("Peringatan", "Pilih atau cari data terlebih dahulu")
        return

    cursor.execute("""
        UPDATE mahasiswa 
        SET nama = ?, jurusan = ?, fakultas = ?
        WHERE nim = ?
    """, (nama, jurusan, fakultas, nim))

    conn.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Sukses", "Data berhasil diupdate")
        bersihkan_form()
        tampil_data()
    else:
        messagebox.showwarning("Gagal", "Data dengan NIM tersebut tidak ditemukan")


def delete_data():
    nim = entry_nim.get()

    if nim == "":
        messagebox.showwarning("Peringatan", "Pilih atau cari data yang ingin dihapus")
        return

    konfirmasi = messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?")

    if konfirmasi:
        cursor.execute("DELETE FROM mahasiswa WHERE nim = ?", (nim,))
        conn.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Sukses", "Data berhasil dihapus")
            bersihkan_form()
            tampil_data()
        else:
            messagebox.showwarning("Gagal", "Data tidak ditemukan")


def cari_data():
    keyword = entry_cari.get()

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT nim, nama, jurusan, fakultas 
        FROM mahasiswa
        WHERE nim LIKE ? OR nama LIKE ? OR jurusan LIKE ? OR fakultas LIKE ?
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def pilih_data(event):
    selected_item = tree.selection()

    if selected_item:
        item = tree.item(selected_item)
        row = item["values"]

        bersihkan_form()

        entry_nim.insert(0, row[0])
        entry_nama.insert(0, row[1])
        entry_jurusan.insert(0, row[2])
        entry_fakultas.insert(0, row[3])


def bersihkan_form():
    entry_nim.delete(0, tk.END)
    entry_nama.delete(0, tk.END)
    entry_jurusan.delete(0, tk.END)
    entry_fakultas.delete(0, tk.END)


def reset_data():
    entry_cari.delete(0, tk.END)
    bersihkan_form()
    tampil_data()


# =========================
# Membuat GUI Tkinter
# =========================

root = tk.Tk()
root.title("Form Data Mahasiswa")
root.geometry("800x500")

# Pengaturan Pada Form input
tk.Label(root, text="NIM").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_nim = tk.Entry(root, width=35)
entry_nim.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Nama").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_nama = tk.Entry(root, width=35)
entry_nama.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Jurusan").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_jurusan = tk.Entry(root, width=35)
entry_jurusan.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Fakultas").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_fakultas = tk.Entry(root, width=35)
entry_fakultas.grid(row=3, column=1, padx=10, pady=5)

# Pengaturan pada Tombol CRUD
frame_tombol = tk.Frame(root)
frame_tombol.grid(row=4, column=0, columnspan=2, pady=10)

tk.Button(frame_tombol, text="Simpan", width=10, command=simpan_data).grid(row=0, column=0, padx=5)
tk.Button(frame_tombol, text="Update", width=10, command=update_data).grid(row=0, column=1, padx=5)
tk.Button(frame_tombol, text="Delete", width=10, command=delete_data).grid(row=0, column=2, padx=5)
tk.Button(frame_tombol, text="Cancel", width=10, command=bersihkan_form).grid(row=0, column=3, padx=5)

# Pengaturan Pada Tombol Pencarian
tk.Label(root, text="Cari Data").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_cari = tk.Entry(root, width=35)
entry_cari.grid(row=5, column=1, padx=10, pady=5)

tk.Button(root, text="Cari", width=10, command=cari_data).grid(row=5, column=2, padx=5)
tk.Button(root, text="Tampil Semua", width=12, command=reset_data).grid(row=5, column=3, padx=5)

# Pengaturan Pada Tabel Treeview
tree = ttk.Treeview(root, columns=("NIM", "Nama", "Jurusan", "Fakultas"), show="headings")
tree.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

tree.heading("NIM", text="NIM")
tree.heading("Nama", text="Nama")
tree.heading("Jurusan", text="Jurusan")
tree.heading("Fakultas", text="Fakultas")

tree.column("NIM", width=120)
tree.column("Nama", width=200)
tree.column("Jurusan", width=180)
tree.column("Fakultas", width=180)

tree.bind("<<TreeviewSelect>>", pilih_data)

# Jalankan tampil data pertama kali
tampil_data()

root.mainloop()
