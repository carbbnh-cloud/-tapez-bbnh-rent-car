import streamlit as st
import pandas as pd
import psycopg2
import os
import base64
from datetime import datetime

# --- CONFIGURATION (SUPABASE) ---
# Assurez-vous que vos Secrets sont bien définis dans Streamlit Cloud
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["SUPABASE_URL"],
        database=st.secrets["SUPABASE_DB"],
        user=st.secrets["SUPABASE_USER"],
        password=st.secrets["SUPABASE_PASSWORD"],
        port=5432,
        sslmode='require'
    )

def executer(sql, params=(), modifier=False):
    conn = None
    try:
        conn = get_db_connection()
        if modifier:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
            cursor.close()
            return True
        else:
            return pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        st.error(f"Erreur Supabase : {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

# --- SUPPRIMEZ LA FONCTION "preparer_base()" ---
# Ne l'appelez plus à la fin de votre script (l. 277).
# Les tables doivent être créées une seule fois dans l'éditeur SQL de Supabase.

# --- DESIGN & LOGIQUE ---
st.set_page_config(page_title="BBNH OS — Gestion Premium", layout="wide", page_icon="🏎️")

# [Insérez ici tout votre bloc CSS original]

# --- MODIFICATION DE VOS REQUÊTES ---
# Partout où vous aviez "INSERT OR REPLACE", remplacez par :
# executer("INSERT INTO table (...) VALUES (...) ON CONFLICT (id) DO UPDATE ...", params, modifier=True)
