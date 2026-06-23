import sqlite3

def create_db():
    """Initialisation de la base de données et des tables"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    
    # 1. Table Inventaire
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            ppa REAL,
            p_achat REAL,
            expiry_date DATE,
            n_lot TEXT,
            quantity INTEGER,
            min_limit INTEGER DEFAULT 5
        )
    ''')
    
    # 2. Table Utilisateurs (Login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    
    # Ajouter un compte admin par défaut si la table est vide
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users VALUES (?, ?)", ('admin', 'admin123'))
    
    conn.commit()
    conn.close()

# --- Fonctions de GESTION UTILISATEURS ---

def verify_login(username, password):
    """Vérifier les identifiants de connexion"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def add_user(username, password):
    """Ajouter un nouvel utilisateur (pour l'admin)"""
    try:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# --- Fonctions de GESTION STOCK ---

def add_medicine(name, ppa, p_achat, expiry, n_lot, qty):
    """Ajouter un médicament au stock"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO inventory 
                   (name, ppa, p_achat, expiry_date, n_lot, quantity) 
                   VALUES (?, ?, ?, ?, ?, ?)''',
                   (name, ppa, p_achat, expiry, n_lot, qty))
    conn.commit()
    conn.close()

def get_all_medicines():
    """Récupérer la liste complète des produits"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, ppa, p_achat, expiry_date, n_lot, quantity, min_limit FROM inventory")
    data = cursor.fetchall()
    conn.close()
    return data

def sell_medicine(name, n_lot):
    """Vendre un produit (Quantité - 1)"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE inventory 
                      SET quantity = quantity - 1 
                      WHERE name = ? AND n_lot = ? AND quantity > 0''', 
                   (name, n_lot))
    conn.commit()
    conn.close()

def delete_medicine(name, n_lot):
    """Supprimer définitivement un produit"""
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM inventory WHERE name = ? AND n_lot = ?", (name, n_lot))
    conn.commit()
    conn.close()