import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = os.environ.get("https://pwsxxmmlscvazaictocg.supabase.co/rest/v1/", "")
SUPABASE_KEY = os.environ.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB3c3h4bW1sc2N2YXphaWN0b2NnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2ODk2MzUsImV4cCI6MjA5NzI2NTYzNX0.Dhg-fnZ_OMkk59e9w58X6DzZRr-Y3nd8PBq_cc9SH48Y", "")

# Initialisation sécurisée du client
supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        st.error(f"Erreur d'initialisation Supabase : {e}")
else:
    st.warning("⚠️ Variables SUPABASE_URL ou SUPABASE_KEY manquantes dans les secrets ou l'environnement.")

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="BBNH OS — Gestion Premium", 
    layout="wide", 
    page_icon="🏎️",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS AVANCÉ (CHARTE GRAPHIQUE BBNH) ---
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
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
        margin-bottom: 25px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; 
        background-color: #161920; 
        padding: 6px; 
        border-radius: 14px;
        border: 1px solid #222733;
        margin-bottom: 25px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        color: #9ca3af;
        border: none !important;
    }
    .stTabs [aria-selected="true"] { 
        background-color: #e60000 !important;
        color: #ffffff !important;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #e60000 0%, #b30000 100%) !important;
        color: white !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
    }
    
    div[data-testid="stDataFrame"] {
        border: 1px solid #222733 !important;
        border-radius: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def encoder_image_base64(file_buffer):
    if file_buffer is None: return ""
    try: return base64.b64encode(file_buffer.getvalue()).decode()
    except: return ""

def formater_heure_propre(valeur_excel):
    if pd.isna(valeur_excel): return '00:00'
    if isinstance(valeur_excel, (datetime, time)): return valeur_excel.strftime('%H:%M')
    val_str = str(valeur_excel).strip()
    parts = val_str.split(":")
    if len(parts) >= 2: return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return '00:00'

# --- FONCTION D'EXECUTION SUPABASE ---
def executer(table_name, method, data=None, filters=None, select_cols="*", upsert_on=None):
    if supabase is None: return pd.DataFrame() if method == "select" else False
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
        st.error(f"Erreur Supabase ({table_name}): {e}")
        return pd.DataFrame() if method == "select" else False

# --- CHARGEMENT INITIAL ---
df_voitures = executer("stock", "select")
df_c_list = executer("clients", "select", select_cols="Nom, Prénom, CIN")

liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row['Nom']).upper()} {str(row['Prénom'])} (CIN: {row['CIN']})" for _, row in df_c_list.iterrows()] if not df_c_list.empty else ["-- Entrée manuelle --"]
liste_vehicules_opt = [f"{str(row['Matricule']).strip()}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule'])] if not df_voitures.empty else []

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #e60000;'>BBNH RENT A CAR</h1>", unsafe_allow_html=True)
    menu_action = st.radio("MENU PRINCIPAL", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat / Réservation", 
        "🚗 Gestion de la Flotte",
        "⚙️ Modifier un Dossier",
        "❌ Supprimer une opération",
        "📥 Imports Excel"
    ])

# --- MODE VISIONNEUSE ---
if menu_action == "🔍 Mode Visionneuse":
    st.title("📊 Tableau de Bord BBNH")
    tab_planning, tab_vidange, tab_crm = st.tabs(["🗓️ PLANNING", "🔧 MAINTENANCE", "👥 CRM"])

    with tab_planning:
        st.subheader("Planning Global")
        if not df_voitures.empty:
            df_mouvements = executer("mouvements", "select")
            st.dataframe(df_mouvements, use_container_width=True)
        else: st.info("Aucun véhicule trouvé.")

    with tab_vidange:
        st.subheader("Suivi des Vidanges")
        df_v = executer("vidanges", "select")
        if not df_v.empty:
            st.dataframe(df_v, use_container_width=True)
        else: st.info("Aucune donnée de vidange.")

    with tab_crm:
        st.subheader("Base Clients")
        df_clients_full = executer("clients", "select")
        if not df_clients_full.empty:
            st.dataframe(df_clients_full, use_container_width=True)
        else: st.info("Aucun client enregistré.")

# --- NOUVEAU CONTRAT ---
elif menu_action == "📝 Nouveau Contrat / Réservation":
    st.title("📝 Nouveau Dossier")
    with st.form("form_new_op"):
        c1, c2 = st.columns(2)
        with c1: 
            nature = st.selectbox("Type d'opération", ["Location", "Réservation", "Maintenance"])
            vehicule = st.selectbox("Véhicule", liste_vehicules_opt)
        with c2:
            client_sel = st.selectbox("Client", liste_clients_opt)
            nom_manuel = st.text_input("Nom si manuel")
        
        d1 = st.date_input("Date Début", datetime.now())
        d2 = st.date_input("Date Fin", datetime.now() + timedelta(days=1))
        
        prix = st.number_input("Prix Total (DT)", value=0)
        km_dep = st.number_input("KM Départ", value=0)
        
        if st.form_submit_button("⚡ CRÉER LE DOSSIER"):
            client_final = nom_manuel if client_sel == "-- Entrée manuelle --" else client_sel
            data = {
                "Matricule": vehicule,
                "Type_Statut": nature,
                "Client": client_final,
                "Date_Debut": d1.strftime("%Y-%m-%d"),
                "Date_Fin": d2.strftime("%Y-%m-%d"),
                "Prix": str(prix),
                "KM_Debut": int(km_dep),
                "Statut_Mouvement": "En cours"
            }
            if executer("mouvements", "insert", data=data):
                st.success("Dossier enregistré !"); st.rerun()

# --- GESTION FLOTTE ---
elif menu_action == "🚗 Gestion de la Flotte":
    st.title("🚗 Gestion des Véhicules")
    with st.expander("➕ Ajouter un véhicule"):
        with st.form("add_car"):
            mat = st.text_input("Matricule *")
            marq = st.text_input("Marque *")
            mod = st.text_input("Modèle")
            if st.form_submit_button("Enregistrer"):
                if mat and marq:
                    executer("stock", "upsert", data={"Matricule": mat, "Marque": marq, "Modèle": mod}, upsert_on="Matricule")
                    executer("vidanges", "upsert", data={"Matricule": mat, "Marque": marq, "KM_Recent": 0, "KM_Dernier_Vidange": 0}, upsert_on="Matricule")
                    st.success("Véhicule ajouté !"); st.rerun()
    
    with st.expander("🗑️ Supprimer un véhicule"):
        veh_del = st.selectbox("Véhicule à supprimer", liste_vehicules_opt)
        if st.button("Confirmer la suppression"):
            executer("stock", "delete", filters=[["Matricule", "eq", veh_del]])
            executer("vidanges", "delete", filters=[["Matricule", "eq", veh_del]])
            st.success("Véhicule supprimé !"); st.rerun()

# --- IMPORTS EXCEL ---
elif menu_action == "📥 Imports Excel":
    st.title("📥 Importation de données")
    f_clients = st.file_uploader("Fichier Clients", type=["xlsx"])
    if f_clients:
        try:
            df = pd.read_excel(f_clients)
            for _, row in df.iterrows():
                executer("clients", "upsert", data=row.to_dict(), upsert_on="CIN")
            st.success("Clients importés !")
        except Exception as e: st.error(f"Erreur : {e}")

# --- RECHERCHE DE DISPONIBILITÉ (ESPACE CENTRAL) ---
st.markdown("---")
st.subheader("🔍 Vérifier la disponibilité")
c1, c2 = st.columns(2)
sd1 = c1.date_input("Du", datetime.now(), key="check_d1")
sd2 = c2.date_input("Au", datetime.now() + timedelta(days=1), key="check_d2")

if st.button("Vérifier"):
    occupe = executer("mouvements", "select", select_cols="Matricule", 
                      filters=[["Statut_Mouvement", "eq", "En cours"], 
                               ["Date_Debut", "lte", sd2.strftime("%Y-%m-%d")], 
                               ["Date_Fin", "gte", sd1.strftime("%Y-%m-%d")]])
    mats_occupe = occupe['Matricule'].tolist() if not occupe.empty else []
    dispo = executer("stock", "select", filters=[["Matricule", "not_in", mats_occupe]]) if mats_occupe else df_voitures
    
    if not dispo.empty:
        st.write(f"✅ {len(dispo)} véhicules disponibles :")
        st.dataframe(dispo)
    else:
        st.warning("❌ Aucun véhicule disponible sur cette période.")
