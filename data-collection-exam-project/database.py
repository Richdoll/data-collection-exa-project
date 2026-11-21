import sqlite3
import pandas as pd

DB_PATH = "data/app_database.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT,
            prix REAL,
            disponibilite TEXT,
            nombre_produits INTEGER,
            note INTEGER,
            nombre_reviews INTEGER,
            description TEXT,
            categorie TEXT,
            tax REAL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gaaraas_auto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marque TEXT,
            modele TEXT,
            annee INTEGER,
            prix REAL,
            kilometrage REAL,
            boite_vitesses TEXT,
            region TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_to_db(df: pd.DataFrame, table_name: str, if_exists: str = "append"):
    conn = sqlite3.connect(DB_PATH)
    df.to_sql(table_name, conn, if_exists=if_exists, index=False)
    conn.close()

def load_from_db(table_name: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
    except Exception:
        df = pd.DataFrame()
    conn.close()
    return df
