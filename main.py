import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import database

# Initialize DB
database.create_db()

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Pharmacy Assistant | Login")
        self.root.geometry("400x500")
        self.root.configure(bg="#f8f9fa")
        
        # Show Login Page first
        self.show_login_screen()

    def show_login_screen(self):
        self.login_frame = tk.Frame(self.root, bg="white", padx=40, pady=40)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.login_frame, text="🔒 Login", font=("Segoe UI", 20, "bold"), bg="white", fg="#2c3e50").pack(pady=20)
        
        tk.Label(self.login_frame, text="Username", bg="white").pack(anchor="w")
        self.user_en = tk.Entry(self.login_frame, font=("Segoe UI", 12), bd=1, relief="solid")
        self.user_en.pack(fill="x", pady=5)

        tk.Label(self.login_frame, text="Password", bg="white").pack(anchor="w", pady=(10, 0))
        self.pass_en = tk.Entry(self.login_frame, font=("Segoe UI", 12), bd=1, relief="solid", show="*")
        self.pass_en.pack(fill="x", pady=5)

        tk.Button(self.login_frame, text="LOGIN", command=self.handle_login, bg="#2980b9", fg="white", 
                  font=("Segoe UI", 12, "bold"), relief="flat", cursor="hand2", pady=10).pack(fill="x", pady=20)

    def handle_login(self):
        user = self.user_en.get()
        pwd = self.pass_en.get()
        
        if database.verify_login(user, pwd):
            self.login_frame.destroy()
            self.setup_dashboard()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def setup_dashboard(self):
        """Your original UI code goes here"""
        self.root.geometry("1150x750")
        self.root.title("Smart Pharmacy Assistant | Dashboard")
        
        # --- Copy/Paste your original UI structure below ---
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=80)
        header.pack(fill="x")
        tk.Label(header, text="💡 SMART PHARMACY ASSISTANT", bg="#2c3e50", fg="#ecf0f1", font=("Segoe UI", 20, "bold")).pack(pady=20)

        # Formulaire d'entrée
        input_frame = tk.LabelFrame(self.root, text=" Nouveau Produit ", bg="white", font=("Segoe UI", 11, "bold"), padx=20, pady=20)
        input_frame.pack(fill="x", padx=30, pady=15)

        labels = ["Désignation:", "PPA (Vente):", "P. Achat:", "Péremption (Y-M-D):", "N° Lot:", "Quantité (QTT):"]
        self.entries = []
        for i, txt in enumerate(labels):
            tk.Label(input_frame, text=txt, bg="white", font=("Segoe UI", 10)).grid(row=i//3, column=(i%3)*2, sticky="w", padx=5, pady=8)
            en = tk.Entry(input_frame, font=("Segoe UI", 11), relief="solid", bd=1)
            en.grid(row=i//3, column=(i%3)*2+1, padx=10, pady=8)
            self.entries.append(en)

        tk.Button(input_frame, text="AJOUTER STOCK +", command=self.save_medicine, bg="#27ae60", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2", padx=20).grid(row=0, column=6, rowspan=2, padx=20)

        # Zone d'actions
        btn_frame = tk.Frame(self.root, bg="#f8f9fa")
        btn_frame.pack(fill="x", padx=30, pady=5)

        tk.Button(btn_frame, text="🛒 ENREGISTRER VENTE (-1)", command=self.handle_sell, bg="#2980b9", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=25, pady=8).pack(side="left", padx=5)
        tk.Button(btn_frame, text="🗑️ SUPPRIMER PRODUIT", command=self.handle_delete, bg="#e74c3c", fg="white", font=("Segoe UI", 10, "bold"), relief="flat", padx=25, pady=8).pack(side="left", padx=5)

        # Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=30, pady=10)

        self.tree_all = self.create_styled_tree(self.notebook); self.notebook.add(self.tree_all.master, text=" 📋 INVENTAIRE GÉNÉRAL ")
        self.tree_exp = self.create_styled_tree(self.notebook); self.notebook.add(self.tree_exp.master, text=" 🚨 PRODUITS EXPIRÉS ")
        self.tree_low = self.create_styled_tree(self.notebook); self.notebook.add(self.tree_low.master, text=" 📦 RUPTURE DE STOCK ")

        self.refresh_all_tabs()
        self.root.after(1000, self.check_on_startup)

    def create_styled_tree(self, parent):
        frame = tk.Frame(parent, bg="white")
        cols = ("Désignation", "PPA", "P. Achat", "Date Péremption", "N° Lot", "QTT")
        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols: tree.heading(c, text=c); tree.column(c, anchor="center")
        
        tree.tag_configure("danger", background="#ffadad")
        tree.tag_configure("warning", background="#ffd6a5")
        tree.tag_configure("reorder", background="#9bf6ff")
        
        vsb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        frame.pack(fill="both", expand=True)
        return tree

    # --- Methods migrated from your original code (Updated with 'self') ---
    def refresh_all_tabs(self):
        for tree, f_type in [(self.tree_all, "all"), (self.tree_exp, "expired"), (self.tree_low, "low_stock")]:
            for item in tree.get_children(): tree.delete(item)
            today = datetime.now().date()
            for row in database.get_all_medicines():
                name, ppa, p_achat, exp_str, n_lot, qty, limit = row
                try:
                    exp_date = datetime.strptime(exp_str, '%Y-%m-%d').date()
                    days_left = (exp_date - today).days
                    tag = "normal"
                    if days_left <= 0: tag = "danger"
                    elif days_left <= 30: tag = "warning"
                    elif qty <= limit: tag = "reorder"
                    
                    show = (f_type == "all") or (f_type == "expired" and days_left <= 0) or (f_type == "low_stock" and qty <= limit)
                    if show: tree.insert('', 'end', values=(name, f"{ppa:.2f}", f"{p_achat:.2f}", exp_str, n_lot, qty), tags=(tag,))
                except: continue

    def save_medicine(self):
        try:
            data = [en.get() for en in self.entries]
            
            # 1. Check if Name is empty
            if not data[0]: 
                messagebox.showerror("Erreur", "Le nom (Désignation) est obligatoire")
                return
            
            # 2. Check if Date is empty or wrong format
            try:
                datetime.strptime(data[3], '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erreur Date", "Format de date invalide!\nUtilisez: AAAA-MM-JJ (ex: 2026-05-20)")
                return

            # 3. Check if Prices and Quantity are valid numbers
            try:
                ppa = float(data[1])
                p_achat = float(data[2])
                qty = int(data[5])
            except ValueError:
                messagebox.showerror("Erreur Nombre", "PPA, P.Achat et Quantité doivent être des chiffres.")
                return
            
            # If everything is okay, save to database
            database.add_medicine(data[0], ppa, p_achat, data[3], data[4], qty)
            
            messagebox.showinfo("Succès", f"{data[0]} ajouté avec succès")
            
            # Clear entries
            for en in self.entries: en.delete(0, tk.END)
            self.refresh_all_tabs()

        except Exception as e:
            messagebox.showerror("Erreur Critique", f"Une erreur imprévue est survenue: {e}")

    def handle_sell(self):
        current_tab = self.notebook.select()
        tab_id = self.notebook.index(current_tab)
        active_tree = self.tree_all if tab_id == 0 else (self.tree_exp if tab_id == 1 else self.tree_low)
        sel = active_tree.selection()
        if sel:
            data = active_tree.item(sel)['values']
            if int(data[5]) > 0:
                database.sell_medicine(data[0], data[4])
                self.refresh_all_tabs()
            else: messagebox.showwarning("Stock épuisé", "Quantité nulle !")

    def handle_delete(self):
        sel = self.tree_all.selection()
        if sel:
            data = self.tree_all.item(sel)['values']
            if messagebox.askyesno("Confirmation", f"Supprimer {data[0]} ?"):
                database.delete_medicine(data[0], data[4])
                self.refresh_all_tabs()

    def check_on_startup(self):
        today = datetime.now().date()
        all_meds = database.get_all_medicines()
        expired, low = 0, 0
        for row in all_meds:
            try:
                exp_date = datetime.strptime(row[3], '%Y-%m-%d').date()
                if exp_date <= today: expired += 1
                if row[5] <= row[6]: low += 1
            except: continue
        if expired > 0 or low > 0:
            messagebox.showwarning("Système d'Alerte", f"🔴 Produits expirés : {expired}\n🔵 Stock faible : {low}")

if __name__ == "__main__":
    root = tk.Tk()
    # Apply global styles
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TNotebook", background="#f8f9fa", borderwidth=0)
    style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[15, 5])
    style.configure("Treeview", font=("Segoe UI", 10), rowheight=32)
    style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#2c3e50", foreground="white")
    
    app = PharmacyApp(root)
    root.mainloop()