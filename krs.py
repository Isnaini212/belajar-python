import csv
import sqlite3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from html import escape

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

KOLOM_CETAK = (
    "Tahun Ajar",
    "Semester",
    "NIM",
    "Nama",
    "Jurusan",
    "Fakultas",
    "Kode MK",
    "Nama MK",
    "SKS",
    "Biaya"
)

matakuliah_terpilih = []

def ambil_data_krs(keyword=""):
    cursor.execute("""
        SELECT	k.thn_ajar, k.semester, k.nim, 
	    m.nama, m.jurusan, m.fakultas, k.kodemk, mk.namamk, mk.sks,
            IFNULL(mk.biaya, 0)
        FROM krs k
        JOIN mahasiswa m ON k.nim = m.nim
        JOIN matakuliah mk ON k.kodemk = mk.kodemk
        WHERE CAST(k.thn_ajar AS TEXT) LIKE ?
           OR k.semester LIKE ?
           OR CAST(k.nim AS TEXT) LIKE ?
           OR m.nama LIKE ?
           OR k.kodemk LIKE ?
           OR mk.namamk LIKE ?
        ORDER BY k.thn_ajar, k.semester, k.nim, k.kodemk
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))
    return cursor.fetchall()


def isi_entry_readonly(entry, nilai):
    entry.config(state="normal")
    entry.delete(0, tk.END)
    entry.insert(0, nilai)
    entry.config(state="readonly")


def tampilkan_mahasiswa(event=None):
    nim = entry_nim.get()

    if nim == "":
        bersihkan_mahasiswa()
        return

    cursor.execute("""
        SELECT nama, jurusan, fakultas
        FROM mahasiswa
        WHERE nim = ?
    """, (nim,))
    data = cursor.fetchone()

    if data:
        isi_entry_readonly(entry_nama, data[0])
        isi_entry_readonly(entry_jurusan, data[1])
        isi_entry_readonly(entry_fakultas, data[2])
    else:
        bersihkan_mahasiswa()
        messagebox.showwarning("Peringatan", "NIM tidak ditemukan di tabel mahasiswa")


def tampilkan_matakuliah(event=None):
    kodemk = entry_kodemk.get()

    if kodemk == "":
        bersihkan_matakuliah()
        return

    cursor.execute("""
        SELECT namamk, sks, IFNULL(biaya, 0)
        FROM matakuliah
        WHERE kodemk = ?
    """, (kodemk,))
    data = cursor.fetchone()

    if data:
        isi_entry_readonly(entry_namamk, data[0])
        isi_entry_readonly(entry_sks, data[1])
        isi_entry_readonly(entry_biaya, data[2])
    else:
        bersihkan_matakuliah()
        messagebox.showwarning("Peringatan", "Kode matakuliah tidak ditemukan")


def refresh_tree_matakuliah():
    for item in tree_matakuliah.get_children():
        tree_matakuliah.delete(item)

    total_sks = 0
    total_biaya = 0

    for row in matakuliah_terpilih:
        tree_matakuliah.insert("", tk.END, values=row)
        try:
            total_sks += int(row[2])
        except ValueError:
            pass
        total_biaya += int(row[3])

    label_total.config(text="Total SKS: " + str(total_sks) + " | Total Biaya: " + str(total_biaya))


def tambah_matakuliah():
    kodemk = entry_kodemk.get()
    namamk = entry_namamk.get()
    sks = entry_sks.get()
    biaya = entry_biaya.get()

    if kodemk == "" or namamk == "":
        messagebox.showwarning("Peringatan", "Isi kode matakuliah terlebih dahulu")
        return

    for row in matakuliah_terpilih:
        if row[0] == kodemk:
            messagebox.showwarning("Peringatan", "Matakuliah sudah ada di daftar KRS")
            return

    matakuliah_terpilih.append((kodemk, namamk, sks, biaya))
    bersihkan_matakuliah()
    refresh_tree_matakuliah()


def hapus_matakuliah():
    selected = tree_matakuliah.selection()

    if not selected:
        messagebox.showwarning("Peringatan", "Pilih matakuliah yang ingin dihapus dari daftar")
        return

    kodemk = tree_matakuliah.item(selected[0])["values"][0]

    for row in list(matakuliah_terpilih):
        if row[0] == kodemk:
            matakuliah_terpilih.remove(row)
            break

    refresh_tree_matakuliah()


def validasi_header_krs():
    thn_ajar = entry_thn_ajar.get()
    semester = combo_semester.get()
    nim = entry_nim.get()

    if thn_ajar == "" or semester == "" or nim == "":
        messagebox.showwarning("Peringatan", "Tahun ajar, semester, dan NIM wajib diisi")
        return None

    if entry_nama.get() == "":
        messagebox.showerror("Error", "NIM belum valid")
        return None

    if len(matakuliah_terpilih) == 0:
        messagebox.showwarning("Peringatan", "Tambahkan minimal satu matakuliah")
        return None

    return thn_ajar, semester, nim


def simpan_data():
    data_header = validasi_header_krs()

    if data_header is None:
        return

    thn_ajar, semester, nim = data_header

    try:
        for row in matakuliah_terpilih:
            cursor.execute("""
                INSERT INTO krs (thn_ajar, semester, nim, kodemk)
                VALUES (?, ?, ?, ?)
            """, (thn_ajar, semester, nim, row[0]))

        conn.commit()
        messagebox.showinfo("Sukses", "Data KRS berhasil disimpan")
        bersihkan_form()

    except sqlite3.IntegrityError:
        conn.rollback()
        messagebox.showerror("Error", "Sebagian atau seluruh matakuliah sudah ada pada KRS ini")


def load_krs_terpilih(thn_ajar, semester, nim):
    cursor.execute("""
        SELECT mk.kodemk, mk.namamk, mk.sks, IFNULL(mk.biaya, 0)
        FROM krs k
        JOIN matakuliah mk ON k.kodemk = mk.kodemk
        WHERE k.thn_ajar = ? AND k.semester = ? AND k.nim = ?
        ORDER BY mk.kodemk
    """, (thn_ajar, semester, nim))

    matakuliah_terpilih.clear()
    matakuliah_terpilih.extend(cursor.fetchall())
    refresh_tree_matakuliah()


def bersihkan_mahasiswa():
    isi_entry_readonly(entry_nama, "")
    isi_entry_readonly(entry_jurusan, "")
    isi_entry_readonly(entry_fakultas, "")


def bersihkan_matakuliah():
    entry_kodemk.delete(0, tk.END)
    isi_entry_readonly(entry_namamk, "")
    isi_entry_readonly(entry_sks, "")
    isi_entry_readonly(entry_biaya, "")


def bersihkan_form():
    entry_thn_ajar.delete(0, tk.END)
    combo_semester.set("")
    entry_nim.delete(0, tk.END)
    bersihkan_mahasiswa()
    bersihkan_matakuliah()
    matakuliah_terpilih.clear()
    refresh_tree_matakuliah()


def rows_untuk_cetak():
    rows = ambil_data_krs()

    if len(rows) == 0:
        messagebox.showwarning("Peringatan", "Tidak ada data untuk dicetak")
        return None

    return rows


def cetak_csv():
    rows = rows_untuk_cetak()

    if rows is None:
        return

    filename = filedialog.asksaveasfilename(
        title="Simpan CSV",
        defaultextension=".csv",
        filetypes=[("CSV File", "*.csv")]
    )

    if filename == "":
        return

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(KOLOM_CETAK)
        writer.writerows(rows)

    messagebox.showinfo("Sukses", "Cetak CSV berhasil: " + filename)


def cetak_excel():
    rows = rows_untuk_cetak()

    if rows is None:
        return

    filename = filedialog.asksaveasfilename(
        title="Simpan Excel",
        defaultextension=".xls",
        filetypes=[("Excel File", "*.xls")]
    )

    if filename == "":
        return

    with open(filename, "w", encoding="utf-8") as file:
        file.write("<html><head><meta charset='utf-8'></head><body>")
        file.write("<table border='1'>")
        file.write("<tr>")
        for column in KOLOM_CETAK:
            file.write("<th>" + escape(str(column)) + "</th>")
        file.write("</tr>")
        for row in rows:
            file.write("<tr>")
            for value in row:
                file.write("<td>" + escape(str(value)) + "</td>")
            file.write("</tr>")
        file.write("</table></body></html>")

    messagebox.showinfo("Sukses", "Cetak Excel berhasil: " + filename)


def cetak_pdf():
    rows = rows_untuk_cetak()

    if rows is None:
        return

    filename = filedialog.asksaveasfilename(
        title="Simpan PDF",
        defaultextension=".pdf",
        filetypes=[("PDF File", "*.pdf")]
    )

    if filename == "":
        return

    buat_pdf_sederhana(filename, rows)
    messagebox.showinfo("Sukses", "Cetak PDF berhasil: " + filename)


def escape_pdf_text(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def format_baris_pdf(row):
    teks = " | ".join(str(value) for value in row)
    if len(teks) > 170:
        teks = teks[:167] + "..."
    return teks


def buat_pdf_sederhana(filename, rows):
    judul = "Laporan Data KRS"
    header = format_baris_pdf(KOLOM_CETAK)
    garis = "-" * min(len(header), 170)
    semua_baris = [judul, "", header, garis] + [format_baris_pdf(row) for row in rows]

    baris_per_halaman = 34
    halaman = [
        semua_baris[index:index + baris_per_halaman]
        for index in range(0, len(semua_baris), baris_per_halaman)
    ]

    pages_id = 2
    font_id = 3
    next_object_id = 4
    page_objects = []
    kids = []

    for nomor, lines in enumerate(halaman, start=1):
        content_lines = [
            "BT",
            "/F1 8 Tf",
            "40 555 Td",
            "12 TL"
        ]

        for line in lines:
            content_lines.append("(" + escape_pdf_text(line) + ") Tj")
            content_lines.append("T*")

        content_lines.append("ET")
        stream = "\n".join(content_lines).encode("latin-1", "replace")
        content_id = next_object_id
        page_id = next_object_id + 1
        next_object_id += 2

        page_objects.append((
            content_id,
            "<< /Length " + str(len(stream)) + " >>\nstream\n" +
            stream.decode("latin-1") + "\nendstream"
        ))
        page_objects.append((
            page_id,
            "<< /Type /Page /Parent " + str(pages_id) + " 0 R "
            "/MediaBox [0 0 842 595] "
            "/Resources << /Font << /F1 " + str(font_id) + " 0 R >> >> "
            "/Contents " + str(content_id) + " 0 R >>"
        ))
        kids.append(str(page_id) + " 0 R")

    pages_object = "<< /Type /Pages /Kids [" + " ".join(kids) + "] /Count " + str(len(kids)) + " >>"
    objects = [
        (1, "<< /Type /Catalog /Pages 2 0 R >>"),
        (2, pages_object),
        (3, "<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>"),
    ] + page_objects

    offsets = []
    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")

    for object_id, obj in objects:
        offsets.append(len(pdf))
        pdf.extend((str(object_id) + " 0 obj\n").encode("latin-1"))
        pdf.extend(obj.encode("latin-1", "replace"))
        pdf.extend(b"\nendobj\n")

    xref_pos = len(pdf)
    pdf.extend(("xref\n0 " + str(next_object_id) + "\n").encode("latin-1"))
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets:
        pdf.extend((str(offset).zfill(10) + " 00000 n \n").encode("latin-1"))

    pdf.extend((
        "trailer\n<< /Size " + str(next_object_id) + " /Root 1 0 R >>\n"
        "startxref\n" + str(xref_pos) + "\n%%EOF"
    ).encode("latin-1"))

    with open(filename, "wb") as file:
        file.write(pdf)


root = tk.Tk()
root.title("Form Entry Kartu Rencana Studi")
root.geometry("850x520")

tk.Label(root, text="Tahun Ajar").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_thn_ajar = tk.Entry(root, width=35)
entry_thn_ajar.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Semester").grid(row=1, column=0, padx=10, pady=5, sticky="w")
combo_semester = ttk.Combobox(root, width=32, state="readonly", values=("Ganjil", "Genap", "Pendek"))
combo_semester.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="NIM").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_nim = tk.Entry(root, width=35)
entry_nim.grid(row=2, column=1, padx=10, pady=5)
entry_nim.bind("<Return>", tampilkan_mahasiswa)
entry_nim.bind("<FocusOut>", tampilkan_mahasiswa)

tk.Label(root, text="Nama").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_nama = tk.Entry(root, width=35, state="readonly")
entry_nama.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Jurusan").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_jurusan = tk.Entry(root, width=35, state="readonly")
entry_jurusan.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Fakultas").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_fakultas = tk.Entry(root, width=35, state="readonly")
entry_fakultas.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Kode MK").grid(row=0, column=2, padx=10, pady=5, sticky="w")
entry_kodemk = tk.Entry(root, width=35)
entry_kodemk.grid(row=0, column=3, padx=10, pady=5)
entry_kodemk.bind("<Return>", tampilkan_matakuliah)
entry_kodemk.bind("<FocusOut>", tampilkan_matakuliah)

tk.Label(root, text="Nama MK").grid(row=1, column=2, padx=10, pady=5, sticky="w")
entry_namamk = tk.Entry(root, width=35, state="readonly")
entry_namamk.grid(row=1, column=3, padx=10, pady=5)

tk.Label(root, text="SKS").grid(row=2, column=2, padx=10, pady=5, sticky="w")
entry_sks = tk.Entry(root, width=35, state="readonly")
entry_sks.grid(row=2, column=3, padx=10, pady=5)

tk.Label(root, text="Biaya").grid(row=3, column=2, padx=10, pady=5, sticky="w")
entry_biaya = tk.Entry(root, width=35, state="readonly")
entry_biaya.grid(row=3, column=3, padx=10, pady=5)

tk.Button(root, text="Tambah MK", width=15, command=tambah_matakuliah).grid(row=4, column=3, padx=10, pady=5, sticky="w")
tk.Button(root, text="Hapus MK", width=15, command=hapus_matakuliah).grid(row=4, column=3, padx=10, pady=5, sticky="e")

tree_matakuliah = ttk.Treeview(
    root,
    columns=("Kode MK", "Nama MK", "SKS", "Biaya"),
    show="headings",
    height=6
)
tree_matakuliah.grid(row=6, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

tree_matakuliah.heading("Kode MK", text="Kode MK")
tree_matakuliah.heading("Nama MK", text="Nama MK")
tree_matakuliah.heading("SKS", text="SKS")
tree_matakuliah.heading("Biaya", text="Biaya")

tree_matakuliah.column("Kode MK", width=120)
tree_matakuliah.column("Nama MK", width=300)
tree_matakuliah.column("SKS", width=100)
tree_matakuliah.column("Biaya", width=150)

label_total = tk.Label(root, text="Total SKS: 0 | Total Biaya: 0")
label_total.grid(row=7, column=0, columnspan=4, padx=10, pady=5, sticky="w")

frame_tombol = tk.Frame(root)
frame_tombol.grid(row=8, column=0, columnspan=4, pady=10)

tk.Button(frame_tombol, text="Simpan", width=12, command=simpan_data).grid(row=0, column=0, padx=5)
tk.Button(frame_tombol, text="Cancel", width=12, command=bersihkan_form).grid(row=0, column=1, padx=5)
tk.Button(frame_tombol, text="Cetak CSV", width=12, command=cetak_csv).grid(row=0, column=2, padx=5)
tk.Button(frame_tombol, text="Cetak Excel", width=12, command=cetak_excel).grid(row=0, column=3, padx=5)
tk.Button(frame_tombol, text="Cetak PDF", width=12, command=cetak_pdf).grid(row=0, column=4, padx=5)

root.grid_columnconfigure(3, weight=1)

terapkan_tema(root, "#e8fbf5", "#bdeede", "#198c73")
root.mainloop()