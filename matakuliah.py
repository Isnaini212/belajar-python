import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

conn = sqlite3.connect("AKADEMIKDB.db")
cursor = conn.cursor()


def terapkan_tema(window, warna_bg, warna_panel, warna_aksen):
    window.configure(bg=warna_bg)
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="white", fieldbackground="white", rowheight=24)
    style.configure("Treeview.Heading", background=warna_panel, foreground="#1f2933", font=("Arial", 9, "bold"))

    for widget in window.winfo_children():
        warnai_widget(widget, warna_bg, warna_panel, warna_aksen)


def warnai_widget(widget, warna_bg, warna_panel, warna_aksen):
    if isinstance(widget, tk.Label):
        widget.configure(bg=warna_bg, fg="#1f2933", font=("Arial", 9, "bold"))
    elif isinstance(widget, (tk.Frame, tk.LabelFrame)):
        widget.configure(bg=warna_bg)
    elif isinstance(widget, tk.Button):
        widget.configure(bg=warna_aksen, fg="white", activebackground=warna_panel, activeforeground="#1f2933")

    for child in widget.winfo_children():
        warnai_widget(child, warna_bg, warna_panel, warna_aksen)


def buat_tabel_jika_belum_ada():
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matakuliah (
            kodemk TEXT NOT NULL,
            namamk TEXT NOT NULL,
            sks TEXT NOT NULL,
            biaya INTEGER,
            PRIMARY KEY(kodemk)
        )
    """)
    conn.commit()


def tampil_data():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT kodemk, namamk, sks, biaya
        FROM matakuliah
        ORDER BY kodemk
    """)

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)


def simpan_data():
    kodemk = entry_kodemk.get()
    namamk = entry_namamk.get()
    sks = entry_sks.get()
    biaya = entry_biaya.get()

    if kodemk == "" or namamk == "" or sks == "":
        messagebox.showwarning("Peringatan", "Kode MK, Nama MK, dan SKS wajib diisi")
        return

    if biaya == "":
        biaya = 0

    try:
        cursor.execute("""
            INSERT INTO matakuliah (kodemk, namamk, sks, biaya)
            VALUES (?, ?, ?, ?)""", (kodemk, namamk, sks, biaya))

        conn.commit()
        messagebox.showinfo("Sukses", "Data matakuliah berhasil disimpan")
        bersihkan_form()
        tampil_data()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Kode MK sudah terdaftar")


def update_data():
    kodemk = entry_kodemk.get()
    namamk = entry_namamk.get()
    sks = entry_sks.get()
    biaya = entry_biaya.get()

    if kodemk == "":
        messagebox.showwarning("Peringatan", "Pilih atau cari data terlebih dahulu")
        return

    if namamk == "" or sks == "":
        messagebox.showwarning("Peringatan", "Nama MK dan SKS wajib diisi")
        return

    if biaya == "":
        biaya = 0

    cursor.execute("""
        UPDATE matakuliah
        SET namamk = ?, sks = ?, biaya = ?
        WHERE kodemk = ?
    """, (namamk, sks, biaya, kodemk))

    conn.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Sukses", "Data matakuliah berhasil diupdate")
        bersihkan_form()
        tampil_data()
    else:
        messagebox.showwarning("Gagal", "Data dengan Kode MK tersebut tidak ditemukan")


def delete_data():
    kodemk = entry_kodemk.get()

    if kodemk == "":
        messagebox.showwarning("Peringatan", "Pilih atau cari data yang ingin dihapus")
        return

    cursor.execute("SELECT * FROM krs WHERE kodemk = ?", (kodemk,))
    if cursor.fetchone() is not None:
        messagebox.showerror("Error", "Matakuliah tidak bisa dihapus karena sudah dipakai di data KRS")
        return

    if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
        cursor.execute("DELETE FROM matakuliah WHERE kodemk = ?", (kodemk,))
        conn.commit()

        if cursor.rowcount > 0:
            messagebox.showinfo("Sukses", "Data matakuliah berhasil dihapus")
            bersihkan_form()
            tampil_data()
        else:
            messagebox.showwarning("Gagal", "Data tidak ditemukan")


def cari_data():
    keyword = entry_cari.get()

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT kodemk, namamk, sks, biaya
        FROM matakuliah
        WHERE kodemk LIKE ?
           OR namamk LIKE ?
           OR sks LIKE ?
           OR CAST(biaya AS TEXT) LIKE ?
        ORDER BY kodemk
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)


def pilih_data(event):
    selected = tree.selection()

    if selected:
        row = tree.item(selected[0])["values"]

        bersihkan_form()

        entry_kodemk.insert(0, row[0])
        entry_namamk.insert(0, row[1])
        entry_sks.insert(0, row[2])
        entry_biaya.insert(0, row[3])


def bersihkan_form():
    entry_kodemk.delete(0, tk.END)
    entry_namamk.delete(0, tk.END)
    entry_sks.delete(0, tk.END)
    entry_biaya.delete(0, tk.END)


def reset_data():
    entry_cari.delete(0, tk.END)
    bersihkan_form()
    tampil_data()


buat_tabel_jika_belum_ada()

root = tk.Tk()
root.title("Form Data Matakuliah")
root.geometry("850x520")

tk.Label(root, text="Kode MK").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_kodemk = tk.Entry(root, width=35)
entry_kodemk.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Nama MK").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_namamk = tk.Entry(root, width=35)
entry_namamk.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="SKS").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_sks = tk.Entry(root, width=35)
entry_sks.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Biaya").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_biaya = tk.Entry(root, width=35)
entry_biaya.grid(row=3, column=1, padx=10, pady=5)

frame_tombol = tk.Frame(root)
frame_tombol.grid(row=4, column=0, columnspan=4, pady=10)

tk.Button(frame_tombol, text="Simpan", width=12, command=simpan_data).grid(row=0, column=0, padx=5)
tk.Button(frame_tombol, text="Update", width=12, command=update_data).grid(row=0, column=1, padx=5)
tk.Button(frame_tombol, text="Delete", width=12, command=delete_data).grid(row=0, column=2, padx=5)
tk.Button(frame_tombol, text="Cancel", width=12, command=bersihkan_form).grid(row=0, column=3, padx=5)

tk.Label(root, text="Cari Data").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_cari = tk.Entry(root, width=35)
entry_cari.grid(row=5, column=1, padx=10, pady=5)

tk.Button(root, text="Cari", width=12, command=cari_data).grid(row=5, column=2, padx=5)
tk.Button(root, text="Tampil Semua", width=15, command=reset_data).grid(row=5, column=3, padx=5)

tree = ttk.Treeview(
    root,
    columns=("Kode MK", "Nama MK", "SKS", "Biaya"),
    show="headings"
)
tree.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

tree.heading("Kode MK", text="Kode MK")
tree.heading("Nama MK", text="Nama MK")
tree.heading("SKS", text="SKS")
tree.heading("Biaya", text="Biaya")

tree.column("Kode MK", width=120)
tree.column("Nama MK", width=280)
tree.column("SKS", width=100)
tree.column("Biaya", width=140)

tree.bind("<<TreeviewSelect>>", pilih_data)

root.grid_rowconfigure(6, weight=1)
root.grid_columnconfigure(3, weight=1)

terapkan_tema(root, "#fff3e6", "#ffd5a3", "#c76d1d")
tampil_data()

root.mainloop()
