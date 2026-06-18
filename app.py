import streamlit as st
import pandas as pd
import psycopg2
import base64
from datetime import datetime

# --- 1. CONFIGURATION DE CONNEXION ---
def get_db_connection():
    return psycopg2.connect(
        host=st.secrets["SUPABASE_URL"],
        database=st.secrets["SUPABASE_DB"],
        user=st.secrets["SUPABASE_USER"],
        password=st.secrets["SUPABASE_PASSWORD"],
        port=5432, sslmode='require'
    )

def executer(sql, params=(), modifier=False):
    conn = None
    try:
        conn = get_db_connection()
        if modifier:
            cursor = conn.cursor()
            # Adaptation PostgreSQL (%s au lieu de ?)
            sql_pg = sql.replace('?', '%s')
            cursor.execute(sql_pg, params)
            conn.commit()
            cursor.close()
            return True
        else:
            return pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        st.error(f"Erreur DB : {e}")
        return pd.DataFrame()
    finally:
        if conn: conn.close()

# --- 2. CONFIGURATION PAGE ---
st.set_page_config(page_title="BBNH OS — Gestion Premium", layout="wide", page_icon="🏎️")

# (Gardez ici votre bloc CSS original)
st.markdown("<style>/* Votre CSS ici */</style>", unsafe_allow_html=True)

# --- 3. LOGIQUE DES MODULES ---
st.sidebar.title("BBNH CONSOLE")
menu = st.sidebar.radio("Navigation", ["Tableau de Bord", "Planning", "CRM", "Vidanges"])

if menu == "Tableau de Bord":
    st.header("📊 Vue d'ensemble")
    # Exemple : Récupérer les données de la flotte
    df = executer("SELECT * FROM stock")
    st.dataframe(df)

elif menu == "Planning":
    st.header("🗓️ Planning")
    # Récupérer les mouvements
    mouvements = executer("SELECT * FROM mouvements")
    st.write(mouvements)

elif menu == "CRM":
    st.header("👥 Gestion Clients")
    with st.form("client_form"):
        nom = st.text_input("Nom")
        submit = st.form_submit_button("Sauvegarder")
        if submit:
            executer("INSERT INTO clients (nom) VALUES (?)", (nom,), modifier=True)
            st.success("Client ajouté !")

# --- 4. FIN DU SCRIPT ---
# NE PAS APPELER preparer_base() ICI.
