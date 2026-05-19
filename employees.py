# kode program untuk membuat modul employees.py

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

# =========================================
# Koneksi Database
# =========================================

conn = sqlite3.connect("AKADEMIKDB.db")
cursor = conn.cursor()

# =========================================
# Fungsi CRUD
# =========================================

def tampil_data():

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute(""" SELECT employee_id, name, job, salary, commission FROM employees""")
    rows = cursor.fetchall()
    for row in rows:
        tree.insert("", tk.END, values=row)


def simpan_data():

    employee_id = entry_employee_id.get()
    name = entry_name.get()
    job = entry_job.get()
    salary = entry_salary.get()
    commission = entry_commission.get()

    if employee_id == "" or name == "" or job == "" or salary == "" or commission == "":
        messagebox.showwarning("Peringatan", "Semua data wajib diisi")
        return

    try:

        cursor.execute("""INSERT INTO employees(employee_id, name, job, salary, commission)
            VALUES (?, ?, ?, ?, ?)
        """, (employee_id, name, job, salary, commission))
        conn.commit()

        messagebox.showinfo("Sukses", "Data employee berhasil disimpan")

        bersihkan_form()
        tampil_data()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Employee ID sudah ada")


def update_data():

    employee_id = entry_employee_id.get()
    name = entry_name.get()
    job = entry_job.get()
    salary = entry_salary.get()
    commission = entry_commission.get()

    if employee_id == "":
        messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu")
        return

    cursor.execute("""
        UPDATE employees
        SET name = ?, job = ?, salary = ?, commission = ?
        WHERE employee_id = ?
    """, (name, job, salary, commission, employee_id))
    conn.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Sukses", "Data berhasil diupdate")
        bersihkan_form()
        tampil_data()
    else:
        messagebox.showwarning("Gagal", "Data tidak ditemukan")


def delete_data():

    employee_id = entry_employee_id.get()

    if employee_id == "":
        messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus")
        return

    jawab = messagebox.askyesno(
        "Konfirmasi",
        "Yakin ingin menghapus data?"
    )

    if jawab:

        cursor.execute("""DELETE FROM employees WHERE employee_id = ?""", (employee_id,))
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

    cursor.execute("""SELECT employee_id, name, job, salary, commission FROM employees
        WHERE employee_id LIKE ? OR name LIKE ? OR job LIKE ?
           OR salary LIKE ? OR commission LIKE ?
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%",
        "%" + keyword + "%"
    ))

    rows = cursor.fetchall()

    for row in rows:
        tree.insert("", tk.END, values=row)


def pilih_data(event):

    selected = tree.selection()

    if selected:

        item = tree.item(selected)
        row = item["values"]

        bersihkan_form()

        entry_employee_id.insert(0, row[0])
        entry_name.insert(0, row[1])
        entry_job.insert(0, row[2])
        entry_salary.insert(0, row[3])
        entry_commission.insert(0, row[4])


def bersihkan_form():

    entry_employee_id.delete(0, tk.END)
    entry_name.delete(0, tk.END)
    entry_job.delete(0, tk.END)
    entry_salary.delete(0, tk.END)
    entry_commission.delete(0, tk.END)


def reset_data():

    entry_cari.delete(0, tk.END)
    bersihkan_form()
    tampil_data()


# =========================================
# GUI Tkinter
# =========================================

root = tk.Tk()

root.title("GUI Data Employees")
root.geometry("950x550")

# =========================================
# Pengaturan Pada Form Input
# =========================================

tk.Label(root, text="Employee ID").grid(row=0, column=0, padx=10, pady=5, sticky="w")

entry_employee_id = tk.Entry(root, width=35)
entry_employee_id.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Name").grid(row=1, column=0, padx=10, pady=5, sticky="w")

entry_name = tk.Entry(root, width=35)
entry_name.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Job").grid(row=2, column=0, padx=10, pady=5, sticky="w")

entry_job = tk.Entry(root, width=35)
entry_job.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Salary").grid(row=3, column=0, padx=10, pady=5, sticky="w")

entry_salary = tk.Entry(root, width=35)
entry_salary.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Commission").grid(row=4, column=0, padx=10, pady=5, sticky="w")

entry_commission = tk.Entry(root, width=35)
entry_commission.grid(row=4, column=1, padx=10, pady=5)

# =========================================
# Pengaturan Pada Tombol CRUD
# =========================================

frame_tombol = tk.Frame(root)
frame_tombol.grid(row=5, column=0, columnspan=4, pady=10)

tk.Button(frame_tombol, text="Simpan", width=12, command=simpan_data).grid(row=0, column=0, padx=5)
tk.Button(frame_tombol, text="Update", width=12, command=update_data).grid(row=0, column=1, padx=5)
tk.Button(frame_tombol, text="Delete", width=12, command=delete_data).grid(row=0, column=2, padx=5)
tk.Button(frame_tombol, text="Bersihkan", width=12, command=bersihkan_form).grid(row=0, column=3, padx=5)

# =========================================
# Pencarian
# =========================================

tk.Label(root, text="Cari Data").grid(row=6, column=0, padx=10, pady=5, sticky="w")

entry_cari = tk.Entry(root, width=35)
entry_cari.grid(row=6, column=1, padx=10, pady=5)

tk.Button(root, text="Cari", width=12, command=cari_data).grid(row=6, column=2)
tk.Button(root, text="Tampil Semua", width=15, command=reset_data).grid(row=6, column=3)

# =========================================
# Pengaturan Pada Tabel Treeview
# =========================================

tree = ttk.Treeview(
    root,
    columns=(
        "Employee ID",
        "Name",
        "Job",
        "Salary",
        "Commission"
    ),
    show="headings"
)

tree.grid(
    row=7,
    column=0,
    columnspan=4,
    padx=10,
    pady=10,
    sticky="nsew"
)

tree.heading("Employee ID", text="Employee ID")
tree.heading("Name", text="Name")
tree.heading("Job", text="Job")
tree.heading("Salary", text="Salary")
tree.heading("Commission", text="Commission")

tree.column("Employee ID", width=120)
tree.column("Name", width=220)
tree.column("Job", width=180)
tree.column("Salary", width=120)
tree.column("Commission", width=120)

tree.bind("<<TreeviewSelect>>", pilih_data)

# =========================================
# Load Awal
# =========================================

tampil_data()

root.mainloop()
