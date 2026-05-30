import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import hashlib
import os


def hash_file(path, algorithm):
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def safe_file_exists(path):
    return path and os.path.isfile(path)


def compare_files(file_asli, file_mod):
    md5_asli = hash_file(file_asli, "md5")
    sha_asli = hash_file(file_asli, "sha256")

    md5_mod = hash_file(file_mod, "md5")
    sha_mod = hash_file(file_mod, "sha256")

    hasil_md5 = "SAMA" if md5_asli == md5_mod else "BERBEDA"
    hasil_sha = "SAMA" if sha_asli == sha_mod else "BERBEDA"

    return {
        "md5_asli": md5_asli,
        "sha_asli": sha_asli,
        "md5_mod": md5_mod,
        "sha_mod": sha_mod,
        "hasil_md5": hasil_md5,
        "hasil_sha": hasil_sha,
    }


def build_analysis(hasil_sha, hasil_md5):
    lines = []
    lines.append("=== ANALISIS ===")
    lines.append(f"- Perbandingan MD5: {hasil_md5}")
    lines.append(f"- Perbandingan SHA-256: {hasil_sha}")

    if hasil_sha == "SAMA":
        lines.append("\nKesimpulan (Integritas):")
        lines.append(" > SHA-256 menunjukkan kemungkinan besar file tidak berubah.")
    else:
        lines.append("\nKesimpulan (Integritas):")
        lines.append(" > SHA-256 menunjukkan file telah berubah / tidak identik.")

    lines.append("\nAlasan / Catatan Keamanan:")
    lines.append("1) MD5 tidak lagi direkomendasikan karena rentan collision (hash bisa sama untuk data berbeda).")
    lines.append("2) Keunggulan SHA-256: lebih kuat terhadap collision dan output lebih panjang/aman untuk integritas.")

    return "\n".join(lines)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pengecekan Integritas File (MD5 & SHA-256) - GUI")
        self.geometry("980x680")

        self.file_asli = tk.StringVar()
        self.file_mod = tk.StringVar()

        self._build_ui()

    def _build_ui(self):
        padding = 12

        # Frame input asli
        frm_asli = ttk.LabelFrame(self, text="File Asli")
        frm_asli.pack(fill="x", padx=padding, pady=(padding, 8))

        entry_asli = ttk.Entry(frm_asli, textvariable=self.file_asli)
        entry_asli.pack(side="left", fill="x", expand=True, padx=(padding, 8), pady=10)

        btn_pilih_asli = ttk.Button(frm_asli, text="Pilih File Asli", command=self.choose_asli)
        btn_pilih_asli.pack(side="left", padx=(0, padding), pady=10)

        # Frame input dimodifikasi
        frm_mod = ttk.LabelFrame(self, text="File Dimodifikasi")
        frm_mod.pack(fill="x", padx=padding, pady=8)

        entry_mod = ttk.Entry(frm_mod, textvariable=self.file_mod)
        entry_mod.pack(side="left", fill="x", expand=True, padx=(padding, 8), pady=10)

        btn_pilih_mod = ttk.Button(frm_mod, text="Pilih File Dimodifikasi", command=self.choose_mod)
        btn_pilih_mod.pack(side="left", padx=(0, padding), pady=10)

        # Tombol proses
        frm_btn = ttk.Frame(self)
        frm_btn.pack(fill="x", padx=padding, pady=10)

        btn_proses = ttk.Button(frm_btn, text="Hitung & Bandingkan", command=self.run_compare)
        btn_proses.pack(side="left")

        btn_clear = ttk.Button(frm_btn, text="Bersihkan Output", command=self.clear_output)
        btn_clear.pack(side="left", padx=10)

        # Output area
        frm_out = ttk.LabelFrame(self, text="Output (Hash & Analisis)")
        frm_out.pack(fill="both", expand=True, padx=padding, pady=(6, padding))

        self.text = tk.Text(frm_out, wrap="word", font=("Consolas", 10))
        self.text.pack(fill="both", expand=True, padx=10, pady=10)

        # Scrollbar
        scroll = ttk.Scrollbar(self.text, command=self.text.yview)
        self.text.configure(yscrollcommand=scroll.set)
        scroll.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")

    def choose_asli(self):
        path = filedialog.askopenfilename(title="Pilih File Asli")
        if path:
            self.file_asli.set(path)

    def choose_mod(self):
        path = filedialog.askopenfilename(title="Pilih File Dimodifikasi")
        if path:
            self.file_mod.set(path)

    def clear_output(self):
        self.text.delete("1.0", tk.END)

    def run_compare(self):
        file_asli = self.file_asli.get().strip()
        file_mod = self.file_mod.get().strip()

        if not safe_file_exists(file_asli):
            messagebox.showerror("Error", "File Asli belum dipilih atau tidak ditemukan.")
            return
        if not safe_file_exists(file_mod):
            messagebox.showerror("Error", "File Dimodifikasi belum dipilih atau tidak ditemukan.")
            return

        try:
            out = compare_files(file_asli, file_mod)
        except Exception as e:
            messagebox.showerror("Error", f"Gagal menghitung hash.\nDetail: {e}")
            return

        analysis = build_analysis(out["hasil_sha"], out["hasil_md5"])

        self.text.delete("1.0", tk.END)
        self.text.insert(tk.END, "=== HASIL HASH ===\n\n")

        self.text.insert(tk.END, "[File Asli]\n")
        self.text.insert(tk.END, f"Path     : {file_asli}\n")
        self.text.insert(tk.END, f"MD5      : {out['md5_asli']}\n")
        self.text.insert(tk.END, f"SHA-256 : {out['sha_asli']}\n\n")

        self.text.insert(tk.END, "[File Dimodifikasi]\n")
        self.text.insert(tk.END, f"Path     : {file_mod}\n")
        self.text.insert(tk.END, f"MD5      : {out['md5_mod']}\n")
        self.text.insert(tk.END, f"SHA-256 : {out['sha_mod']}\n\n")

        self.text.insert(tk.END, "=== PERBANDINGAN ===\n")
        self.text.insert(tk.END, f"MD5     : {out['hasil_md5']}\n")
        self.text.insert(tk.END, f"SHA-256 : {out['hasil_sha']}\n\n")

        self.text.insert(tk.END, analysis)


if __name__ == "__main__":
    app = App()
    app.mainloop()