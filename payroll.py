# kode program untuk membuat modul payroll.py

# install terlebih dulu library tkcalendar
# python -m pip install tkcalendar

import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3

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


def tampil_data():
    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT p.payroll_id, p.payroll_date, p.employee_id, 
	    e.name, e.job, e.salary, e.commission, p.total_amount
        FROM payroll p
        JOIN employees e ON p.employee_id = e.employee_id
    """)

    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)


def hitung_total():
    salary = entry_salary.get()
    commission = entry_commission.get()

    if salary == "":
        salary = 0

    if commission == "":
        commission = 0

    total = int(salary) + int(commission)

    entry_total_amount.config(state="normal")
    entry_total_amount.delete(0, tk.END)
    entry_total_amount.insert(0, total)
    entry_total_amount.config(state="readonly")


def tampilkan_employee(event=None):
    employee_id = entry_employee_id.get()

    if employee_id == "":
        return

    cursor.execute("""
        SELECT name, job, salary, commission
        FROM employees
        WHERE employee_id = ?""", (employee_id,))

    data = cursor.fetchone()

    entry_name.config(state="normal")
    entry_job.config(state="normal")
    entry_salary.config(state="normal")
    entry_commission.config(state="normal")

    entry_name.delete(0, tk.END)
    entry_job.delete(0, tk.END)
    entry_salary.delete(0, tk.END)
    entry_commission.delete(0, tk.END)

    if data:
        entry_name.insert(0, data[0])
        entry_job.insert(0, data[1])
        entry_salary.insert(0, data[2])
        entry_commission.insert(0, data[3])

        hitung_total()
    else:
        messagebox.showwarning("Peringatan", "Employee ID tidak ditemukan")

    entry_name.config(state="readonly")
    entry_job.config(state="readonly")
    entry_salary.config(state="readonly")
    entry_commission.config(state="readonly")


def simpan_data():
    payroll_id = entry_payroll_id.get()
    payroll_date = entry_payroll_date.get()
    employee_id = entry_employee_id.get()
    total_amount = entry_total_amount.get()

    if payroll_id == "" or payroll_date == "" or employee_id == "" or total_amount == "":
        messagebox.showwarning("Peringatan", "Semua data wajib diisi")
        return

    cursor.execute("SELECT * FROM employees WHERE employee_id = ?", (employee_id,))

    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Employee ID tidak ada di tabel employees")
        return

    try:
        cursor.execute("""
            INSERT INTO payroll (payroll_id, payroll_date, employee_id, total_amount)
            VALUES (?, ?, ?, ?)""", (payroll_id, payroll_date, employee_id, total_amount))

        conn.commit()
        messagebox.showinfo("Sukses", "Data payroll berhasil disimpan")
        bersihkan_form()
        tampil_data()

    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "Payroll ID sudah ada")


def update_data():
    payroll_id = entry_payroll_id.get()
    payroll_date = entry_payroll_date.get()
    employee_id = entry_employee_id.get()
    total_amount = entry_total_amount.get()

    if payroll_id == "":
        messagebox.showwarning("Peringatan", "Pilih data terlebih dahulu")
        return

    cursor.execute("""
        UPDATE payroll
        SET payroll_date = ?,
            employee_id = ?,
            total_amount = ?
        WHERE payroll_id = ?
    """, (payroll_date, employee_id, total_amount, payroll_id))

    conn.commit()

    if cursor.rowcount > 0:
        messagebox.showinfo("Sukses", "Data berhasil diupdate")
        bersihkan_form()
        tampil_data()
    else:
        messagebox.showwarning("Gagal", "Data tidak ditemukan")


def delete_data():
    payroll_id = entry_payroll_id.get()

    if payroll_id == "":
        messagebox.showwarning("Peringatan", "Pilih data yang ingin dihapus")
        return

    if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data?"):
        cursor.execute("DELETE FROM payroll WHERE payroll_id = ?", (payroll_id,))
        conn.commit()

        messagebox.showinfo("Sukses", "Data berhasil dihapus")
        bersihkan_form()
        tampil_data()


def cari_data():
    keyword = entry_cari.get()

    for item in tree.get_children():
        tree.delete(item)

    cursor.execute("""
        SELECT p.payroll_id, p.payroll_date, p.employee_id,
            e.name, e.job, e.salary, e.commission, p.total_amount
        FROM payroll p
        JOIN employees e ON p.employee_id = e.employee_id
        WHERE p.payroll_id LIKE ?
           OR p.payroll_date LIKE ?
           OR p.employee_id LIKE ?
           OR e.name LIKE ?
           OR e.job LIKE ?
           OR p.total_amount LIKE ?
    """, (
        "%" + keyword + "%",
        "%" + keyword + "%",
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
        row = tree.item(selected)["values"]

        bersihkan_form()

        entry_payroll_id.insert(0, row[0])
        entry_payroll_date.set_date(row[1])
        entry_employee_id.insert(0, row[2])

        entry_name.config(state="normal")
        entry_job.config(state="normal")
        entry_salary.config(state="normal")
        entry_commission.config(state="normal")
        entry_total_amount.config(state="normal")

        entry_name.insert(0, row[3])
        entry_job.insert(0, row[4])
        entry_salary.insert(0, row[5])
        entry_commission.insert(0, row[6])
        entry_total_amount.insert(0, row[7])

        entry_name.config(state="readonly")
        entry_job.config(state="readonly")
        entry_salary.config(state="readonly")
        entry_commission.config(state="readonly")
        entry_total_amount.config(state="readonly")


def bersihkan_form():
    entry_payroll_id.delete(0, tk.END)
    entry_employee_id.delete(0, tk.END)

    entry_name.config(state="normal")
    entry_job.config(state="normal")
    entry_salary.config(state="normal")
    entry_commission.config(state="normal")
    entry_total_amount.config(state="normal")

    entry_name.delete(0, tk.END)
    entry_job.delete(0, tk.END)
    entry_salary.delete(0, tk.END)
    entry_commission.delete(0, tk.END)
    entry_total_amount.delete(0, tk.END)

    entry_name.config(state="readonly")
    entry_job.config(state="readonly")
    entry_salary.config(state="readonly")
    entry_commission.config(state="readonly")
    entry_total_amount.config(state="readonly")


def reset_data():
    entry_cari.delete(0, tk.END)
    bersihkan_form()
    tampil_data()


root = tk.Tk()
root.title("Form Payroll Relasi Employees")
root.geometry("1100x600")

tk.Label(root, text="Payroll ID").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_payroll_id = tk.Entry(root, width=35)
entry_payroll_id.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Payroll Date").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_payroll_date = DateEntry(root, width=32, date_pattern="yyyy-mm-dd")
entry_payroll_date.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Employee ID").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_employee_id = tk.Entry(root, width=35)
entry_employee_id.grid(row=2, column=1, padx=10, pady=5)
entry_employee_id.bind("<Return>", tampilkan_employee)
entry_employee_id.bind("<FocusOut>", tampilkan_employee)

tk.Label(root, text="Name").grid(row=3, column=0, padx=10, pady=5, sticky="w")
entry_name = tk.Entry(root, width=35, state="readonly")
entry_name.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Job").grid(row=4, column=0, padx=10, pady=5, sticky="w")
entry_job = tk.Entry(root, width=35, state="readonly")
entry_job.grid(row=4, column=1, padx=10, pady=5)

tk.Label(root, text="Salary").grid(row=5, column=0, padx=10, pady=5, sticky="w")
entry_salary = tk.Entry(root, width=35, state="readonly")
entry_salary.grid(row=5, column=1, padx=10, pady=5)

tk.Label(root, text="Commission").grid(row=6, column=0, padx=10, pady=5, sticky="w")
entry_commission = tk.Entry(root, width=35, state="readonly")
entry_commission.grid(row=6, column=1, padx=10, pady=5)

tk.Label(root, text="Total Amount").grid(row=7, column=0, padx=10, pady=5, sticky="w")
entry_total_amount = tk.Entry(root, width=35, state="readonly")
entry_total_amount.grid(row=7, column=1, padx=10, pady=5)

frame_tombol = tk.Frame(root)
frame_tombol.grid(row=8, column=0, columnspan=4, pady=10)

tk.Button(frame_tombol, text="Simpan", width=12, command=simpan_data).grid(row=0, column=0, padx=5)
tk.Button(frame_tombol, text="Update", width=12, command=update_data).grid(row=0, column=1, padx=5)
tk.Button(frame_tombol, text="Delete", width=12, command=delete_data).grid(row=0, column=2, padx=5)
tk.Button(frame_tombol, text="cancel", width=12, command=bersihkan_form).grid(row=0, column=3, padx=5)

tk.Label(root, text="Cari Data").grid(row=9, column=0, padx=10, pady=5, sticky="w")
entry_cari = tk.Entry(root, width=35)
entry_cari.grid(row=9, column=1, padx=10, pady=5)

tk.Button(root, text="Cari", width=12, command=cari_data).grid(row=9, column=2)
tk.Button(root, text="Tampil Semua", width=15, command=reset_data).grid(row=9, column=3)

tree = ttk.Treeview(
    root,
    columns=(
        "Payroll ID",
        "Payroll Date",
        "Employee ID",
        "Name",
        "Job",
        "Salary",
        "Commission",
        "Total Amount"
    ),
    show="headings"
)

tree.grid(row=10, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=120)

tree.bind("<<TreeviewSelect>>", pilih_data)

terapkan_tema(root, "#f0edff", "#d4c9ff", "#6f55c7")
tampil_data()

root.mainloop()
