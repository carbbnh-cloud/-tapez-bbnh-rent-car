import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

# --- CONFIGURATION SUPABASE ---
# Assurez-vous que ces variables sont bien configurées dans vos Secrets Streamlit ou variables d'environnement
SUPABASE_URL = os.environ.get("https://pwsxxmmlscvazaictocg.supabase.co", "")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB3c3h4bW1sc2N2YXphaWN0b2NnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2ODk2MzUsImV4cCI6MjA5NzI2NTYzNX0.Dhg-fnZ_OMkk59e9w58X6DzZRr-Y3nd8PBq_cc9SH48", "")

# Initialisation sécurisée du client
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erreur d'initialisation Supabase : {e}")
else:
    st.warning("⚠️ Variables SUPABASE_URL ou SUPABASE_KEY manquantes. Veuillez les configurer.")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="BBNH OS — Gestion Premium", 
    layout="wide", 
    page_icon="🏎️",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS AVANCÉ ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        background-color: #0f1115 !important;
        color: #f3f4f6 !important;
    }
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    section[data-testid="stSidebar"] {
        background-color: #07080a !important;
        border-right: 1px solid #1f242e !important;
        min-width: 450px !important;
        max-width: 450px !important;
    }
    .logo-container {
        background: #ffffff;
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 25px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div.stButton > button {
        background: linear-gradient(135deg, #e60000 0%, #b30000 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION D'ENCODAGE DES IMAGES ---
def encoder_image_base64(file_buffer):
    if file_buffer is None: return ""
    try: return base64.b64encode(file_buffer.getvalue()).decode()
    except: return ""

# --- FONCTION D'EXECUTION DES REQUETES SUPABASE ---
def executer(table_name, method, data=None, filters=None, select_cols="*", upsert_on=None):
    if supabase is None:
        return pd.DataFrame() if method == "select" else False
    
    try:
        if method == "insert":
            response = supabase.table(table_name).insert(data).execute()
        elif method == "upsert":
            response = supabase.table(table_name).upsert(data, on_conflict=upsert_on).execute()
        elif method == "update":
            query = supabase.table(table_name).update(data)
            if filters:
                for col, op, val in filters:
                    if op == "eq": query = query.eq(col, val)
            response = query.execute()
        elif method == "delete":
            query = supabase.table(table_name).delete()
            if filters:
                for col, op, val in filters:
                    if op == "eq": query = query.eq(col, val)
            response = query.execute()
        elif method == "select":
            query = supabase.table(table_name).select(select_cols)
            if filters:
                for col, op, val in filters:
                    if op == "eq": query = query.eq(col, val)
                    elif op == "like": query = query.like(col, val)
                    elif op == "lte": query = query.lte(col, val)
                    elif op == "gte": query = query.gte(col, val)
                    elif op == "not_in": query = query.not_(col, "in", val)
            response = query.execute()
            return pd.DataFrame(response.data)
        
        return True
    except Exception as e:
        st.error(f"Erreur Supabase sur la table '{table_name}': {e}")
        return pd.DataFrame() if method == "select" else False

def formater_heure_propre(valeur_excel):
    if pd.isna(valeur_excel): return '00:00'
    if isinstance(valeur_excel, (datetime, time)): return valeur_excel.strftime('%H:%M')
    val_str = str(valeur_excel).strip()
    parts = val_str.split(":")
    if len(parts) >= 2: return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return '00:00'

# Chargement initial des données
df_voitures = executer("stock", "select")
df_c_list = executer("clients", "select", select_cols="Nom, Prénom, CIN")

liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row['Nom']).upper()} {str(row['Prénom'])} (CIN: {row['CIN']})" for _, row in df_c_list.iterrows()] if not df_c_list.empty else ["-- Entrée manuelle --"]
liste_vehicules_opt = [f"{str(row['Matricule']).strip()}" for _, row in df_voitures.iterrows() if not df_voitures.empty and pd.notna(row['Matricule'])] if not df_voitures.empty else []
liste_vehicules_complets_opt = [f"{str(row['Matricule']).strip()} — {str(row.get('Modèle', 'Voiture'))}" for _, row in df_voitures.iterrows() if not df_voitures.empty] if not df_voitures.empty else []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #e60000;'>BBNH RENT</h1>", unsafe_allow_html=True)
    menu_action = st.radio("MENU", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat / Réservation", 
        "🚗 Ajouter un Véhicule",
        "🗑️ Supprimer un Véhicule",
        "⚙️ Modifier un Dossier",
        "❌ Supprimer une opération"
    ])

# --- LOGIQUE PRINCIPALE ---
if menu_action == "🔍 Mode Visionneuse":
    st.title("BBNH WORKSPACE")
    tabs = st.tabs(["🗓️ PLANNING", "🔧 MAINTENANCE", "👥 CRM"])
    
    with tabs[0]:
        st.write("Vue planning des véhicules")
        if not df_voitures.empty:
            st.dataframe(df_voitures)
        else:
            st.info("Aucun véhicule dans la flotte. Veuillez en ajouter un ou vérifier votre connexion Supabase.")

    with tabs[1]:
        st.write("Suivi des vidanges")
        df_v = executer("vidanges", "select")
        if not df_v.empty:
            st.dataframe(df_v)

    with tabs[2]:
        st.write("Gestion des clients")
        if not df_c_list.empty:
            st.dataframe(df_c_list)

elif menu_action == "🚗 Ajouter un Véhicule":
    with st.form("add_car"):
        mat = st.text_input("Matricule *")
        marq = st.text_input("Marque *")
        mod = st.text_input("Modèle *")
        if st.form_submit_button("Enregistrer"):
            if mat and marq:
                res = executer("stock", "upsert", data={"Matricule": mat, "Marque": marq, "Modèle": mod}, upsert_on="Matricule")
                if res: st.success("Véhicule ajouté !"); st.rerun()

elif menu_action == "📝 Nouveau Contrat / Réservation":
    st.subheader("Création de dossier")
    with st.form("new_contract"):
        vehicule = st.selectbox("Véhicule", liste_vehicules_opt)
        client = st.text_input("Nom Client")
        debut = st.date_input("Date Début")
        fin = st.date_input("Date Fin")
        if st.form_submit_button("Créer"):
            data = {
                "Matricule": vehicule,
                "Client": client,
                "Date_Debut": debut.strftime("%Y-%m-%d"),
                "Date_Fin": fin.strftime("%Y-%m-%d"),
                "Statut_Mouvement": "En cours"
            }
            if executer("mouvements", "insert", data=data):
                st.success("Dossier créé !"); st.rerun()

# Note : Les autres sections (Supprimer, Modifier) suivent la même logique d'appel à la fonction executer().
