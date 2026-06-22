import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

# --- Supabase Configuration ---
SUPABASE_URL = "https://pwsxxmmlscvazaictocg.supabase.co"
SUPABASE_KEY = "sb_secret_jAKK2jDQXxud_ovVzE2w-Q_4TxiQpjn" # NOTE: For client-side applications, it's recommended to use the 'anon public' key.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- LOGIQUE DE LOGIN (Placer ici tout en haut de app.py) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style=\'text-align: center;\'>🔒 Accès BBNH OS</h1>", unsafe_allow_html=True)
    
    # Formulaire de login
    login = st.text_input("Nom d\'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    
    if st.button("Connexion"):
        # Vérification de vos identifiants
        if login == "carbbnh" and password == "oussamabnh":
            st.session_state.authenticated = True
            st.rerun() # Rafraîchit la page pour accéder à l\'application
        else:
            st.error("Nom d\'utilisateur ou mot de passe incorrect !")
            
    st.stop() # Bloque l\'exécution du reste de l\'application si non connecté

# --- FIN DU BLOC LOGIN ---
# Le reste de votre code (set_page_config, CSS, Tabs...) suit normalement ici.
# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="BBNH OS — Gestion Premium", 
    layout="wide", 
    page_icon="🏎️",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS AVANCÉ : CHARTE GRAPHIQUE BBNH ---
st.markdown("""
    <style>
    @import url(\'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap\');
    
    html, body, [data-testid=\"stAppViewContainer\"] {
        font-family: \'Plus Jakarta Sans\', sans-serif !important;
        background-color: #0f1115 !important;
        color: #f3f4f6 !important;
    }
    
    .main .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    
    /* --- CORRECTION POUR LA SIDEBAR --- */
    section[data-testid=\"stSidebar\"] {
        background-color: #07080a !important;
        border-right: 1px solid #1f242e !important;
        min-width: 450px !important;
        max-width: 450px !important;
    }

    /* --- REGLE RESPONSIVE POUR MOBILE --- */
    @media (max-width: 600px) {
        section[data-testid=\"stSidebar\"] {
            min-width: 100% !important;
            max-width: 100% !important;
        }
    }

    div[data-testid=\"stSidebarUserContent\"] {
        padding: 2rem 1.5rem !important;
    }

    .logo-container {
        background: #ffffff;
        padding: 16px;
        border-radius: 16px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05);
        margin-bottom: 25px;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    div[data-testid=\"stRadio\"] label {
        font-size: 15px !important;
        font-weight: 500 !important;
        padding: 8px 4px !important;
    }
    
    .stTabs [data-baseweb=\"tab-list\"] {
        gap: 8px; 
        background-color: #161920; 
        padding: 6px; 
        border-radius: 14px;
        border: 1px solid #222733;
        margin-bottom: 25px;
    }
    .stTabs [data-baseweb=\"tab\"] {
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: 600;
        color: #9ca3af;
        transition: all 0.2s ease;
        border: none !important;
    }
    .stTabs [data-baseweb=\"tab\"]:hover { background-color: #222733; color: #ffffff; }
    .stTabs [aria-selected=\"true\"] { 
        background-color: #e60000 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 15px rgba(230, 0, 0, 0.5);
    }
    
    h1 {
        font-weight: 800 !important;
        letter-spacing: -1px !important;
        color: #ffffff !important;
    }
    h3 { color: #f3f4f6; font-weight: 700 !important; letter-spacing: -0.5px; }
    
    div[data-testid=\"stForm\"] {
        background: rgba(22, 25, 32, 0.8) !important;
        border: 1px solid #2a3142 !important;
        padding: 25px !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
    }
    
    input, select, textarea, div[data-baseweb=\"select\"] {
        background-color: #1a1e26 !important;
        color: #ffffff !important;
        border: 1px solid #2a3142 !important;
        border-radius: 10px !important;
        font-size: 14px !important;
    }
    
    div.stButton > button {
        background: linear-gradient(135deg, #e60000 0%, #b30000 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 14px 28px !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        font-size: 14px !important;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover { 
        transform: translateY(-1px); 
        box-shadow: 0 5px 15px rgba(230, 0, 0, 0.5); 
    }
    
    div[data-testid=\"stDataFrame\"] {
        border: 1px solid #222733 !important;
        border-radius: 14px !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- FONCTION D\'ENCODAGE DES IMAGES EN TEXTE (BASE64) ---
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception as e:
        return ""

# --- FONCTION D\'EXECUTION DES REQUETES SUPABASE ---
def executer(table_name, method, data=None, query_filters=None, modifier=False):
    try:
        if method == "select":
            query = supabase.from_(table_name).select("*")
            if query_filters:
                for col, op, val in query_filters:
                    if op == "eq": query = query.eq(col, val)
                    elif op == "like": query = query.ilike(col, val)
                    elif op == "in": query = query.in_(col, val)
                    elif op == "lte": query = query.lte(col, val)
                    elif op == "gte": query = query.gte(col, val)
            response = query.execute()
            return pd.DataFrame(response.data)
        
        elif method == "insert":
            response = supabase.from_(table_name).insert(data).execute()
            return response.data
            
        elif method == "update":
            query = supabase.from_(table_name)
            if query_filters:
                for col, op, val in query_filters:
                    if op == "eq": query = query.eq(col, val)
            response = query.update(data).execute()
            return response.data
            
        elif method == "delete":
            query = supabase.from_(table_name)
            if query_filters:
                for col, op, val in query_filters:
                    if op == "eq": query = query.eq(col, val)
            response = query.delete().execute()
            return response.data
            
    except Exception as e:
        st.error(f"Erreur Supabase : {e}")
        return pd.DataFrame() if method == "select" else False

# --- Initialisation des données (à adapter pour Supabase) ---
# Ces appels devront être adaptés pour utiliser la nouvelle fonction executer avec les tables Supabase
# Par exemple, au lieu de executer("SELECT * FROM stock"), ce sera executer("vehicule", "select")

# Initialisation des tables (Supabase gère déjà la structure, pas besoin de CREATE TABLE IF NOT EXISTS ici)
# La fonction preparer_base() n'est plus nécessaire car Supabase gère le schéma.

# Exemple d'adaptation des appels existants
df_voitures = executer("vehicule", "select") # 'stock' devient 'vehicule'
df_c_list = executer("client", "select", query_filters=[("Nom", "neq", None), ("Prénom", "neq", None), ("CIN", "neq", None)]) # 'clients' devient 'client'

liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row[\'Nom\']).upper()} {str(row[\'Prénom\'])} (CIN: {row[\'CIN\']})" for _, row in df_c_list.iterrows()] if not df_c_list.empty else ["-- Entrée manuelle --"]
liste_vehicules_opt = [f"{str(row[\'Matricule\']).strip()}" for _, row in df_voitures.iterrows() if pd.notna(row[\'Matricule\']) and str(row[\'Matricule\']).strip().lower() != \'nan\'] if not df_voitures.empty else []
liste_vehicules_complets_opt = [f"{str(row[\'Matricule\']).strip()} — {str(row.get(\'Modèle\', row.get(\'Marque\', \'Voiture\')))}" for _, row in df_voitures.iterrows() if pd.notna(row[\'Matricule\'])] if not df_voitures.empty else []

for _, car in df_voitures.iterrows():
    mat = str(car.get(\'Matricule\', \'\')).strip()
    marq = str(car.get(\'Marque\', \'\')).upper()
    if mat and mat.lower() != \'nan\':
        # Vérifier si la vidange existe déjà pour éviter les doublons
        existing_vidange = executer("vidange", "select", query_filters=[("Matricule", "eq", mat)])
        if existing_vidange.empty:
            executer("vidange", "insert", data={
                "Matricule": mat,
                "Marque": marq,
                "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                "KM_Dernier_Vidange": 0,
                "KM_Recent": 0
            })

# =========================================================================
# BARRE LATÉRALE (SIDEBAR)
# =========================================================================
with st.sidebar:
    logo_path = "IMG_7149 (1).jpeg"
    if os.path.exists(logo_path):
        st.markdown(\'<div class=\"logo-container\">\', unsafe_allow_html=True)
        st.image(logo_path, use_container_width=True)
        st.markdown(\'</div>\', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style=\'text-align: center; color: #e60000; font-weight:800; margin-bottom:0;\'>BBNH</h1>", unsafe_allow_html=True)
        st.markdown("<p style=\'text-align: center; opacity: 0.5; font-size:13px; letter-spacing:4px; margin-bottom:25px;\'>RENT A CAR</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style=\'margin-bottom:10px;\'>🕹️ CONSOLE D\'ACTION :</h3>", unsafe_allow_html=True)
    menu_action = st.radio("", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat / Réservation", 
        "🚗 Ajouter un Véhicule à la Flotte",
        "🗑️ Supprimer un Véhicule de la Flotte",
        "⚙️ Modifier un Dossier (Contrat/Réservation)",
        "❌ Supprimer une opération"
    ], label_visibility="collapsed")
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.sidebar.expander("📥 IMPORTS EXCEL AUTOMATIQUES", expanded=False):
        f_clients = st.file_uploader("Fichier Clients (BBNH)", type=["xlsx"])
        if f_clients:
            try:
                df_cli = pd.read_excel(f_clients, sheet_name=\'Base de Données\', skiprows=1)
                df_cli = df_cli.loc[:, ~df_cli.columns.str.contains(\'^Unnamed\')]
                # Conversion du DataFrame en liste de dictionnaires pour l'insertion Supabase
                data_to_insert = df_cli.to_dict(orient=\'records\')
                # Supprimer toutes les données existantes avant l'insertion pour simuler 'replace'
                executer("client", "delete", query_filters=[("CIN", "neq", None)]) # Supprime tout
                executer("client", "insert", data=data_to_insert)
                st.success("Données clients synchronisées !")
                st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        f_loc2 = st.file_uploader("Fichier Base LOC2", type=["xlsx"])
        if f_loc2:
            try:
                df_vehicule = pd.read_excel(f_loc2, sheet_name=\'Stock\') # 'stock' devient 'vehicule'
                df_mouv_raw = pd.read_excel(f_loc2, sheet_name=\'MOUVEMENTS\')
                df_vehicule = df_vehicule.loc[:, ~df_vehicule.columns.str.contains(\'^Unnamed\')]
                df_mouv_raw = df_mouv_raw.loc[:, ~df_mouv_raw.columns.str.contains(\'^Unnamed\')]
                
                # Insertion des véhicules
                data_to_insert_vehicule = df_vehicule.to_dict(orient=\'records\')
                executer("vehicule", "delete", query_filters=[("Matricule", "neq", None)])
                executer("vehicule", "insert", data=data_to_insert_vehicule)

                # Insertion des mouvements (avec adaptation des noms de colonnes)
                mapping = {}
                for col in df_mouv_raw.columns:
                    c_clean = str(col).strip().lower().replace(" ", "_").replace("é", "e").replace("è", "e")
                    if "matri" in c_clean: mapping[col] = "Matricule"
                    elif "type" in c_clean or "statut" in c_clean: mapping[col] = "Type_Statut"
                    elif "deb" in c_clean and "heur" not in c_clean: mapping[col] = "Date_Debut"
                    elif "fin" in c_clean and "heur" not in c_clean: mapping[col] = "Date_Fin"
                    elif "heur" in c_clean and "deb" in c_clean: mapping[col] = "Heure_Debut"
                    elif "heur" in c_clean and "fin" in c_clean: mapping[col] = "Heure_Fin"
                    elif "client" in c_clean or "nom" in c_clean: mapping[col] = "Client"
                    elif "prix" in c_clean or "montant" in c_clean or "total" in c_clean: mapping[col] = "Prix"
                    elif "km_deb" in c_clean or "kilometrage_deb" in c_clean or "km_depart" in c_clean: mapping[col] = "KM_Debut"
                    elif "km_fin" in c_clean or "kilometrage_re" in c_clean: mapping[col] = "KM_Fin"
                    elif "caution" in c_clean: mapping[col] = "Caution"
                    elif "reste" in c_clean: mapping[col] = "Reste"
                    elif "lieu_reception" in c_clean: mapping[col] = "Lieu_Reception"
                    elif "no_vol" in c_clean: mapping[col] = "No_Vol"
                    elif "info_note" in c_clean: mapping[col] = "Info_Note"
                
                df_mouv_raw = df_mouv_raw.rename(columns=mapping)
                data_to_insert_mouvement = df_mouv_raw.to_dict(orient=\'records\')
                executer("mouvement", "delete", query_filters=[("Matricule", "neq", None)])
                executer("mouvement", "insert", data=data_to_insert_mouvement)

                st.success("Données stock et mouvements synchronisées !")
                st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

def formater_heure_propre(valeur_excel):
    if pd.isna(valeur_excel):
        return \'00:00\'
    if isinstance(valeur_excel, (datetime, time)):
        return valeur_excel.strftime(\'%H:%M\')
    val_str = str(valeur_excel).strip()
    if " " in val_str:
        try: val_str = val_str.split(" ")[1]
        except: pass
    parts = val_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return \'00:00\'

# =========================================================================
# ESPACE CENTRAL DE TRAVAIL INTERACTIF
# =========================================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION</h1>", unsafe_allow_html=True)

# --- RECHERCHE AVANCÉE PAR PÉRIODE ---
with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    
    with c_search1:
        search_date_debut = st.date_input("📅 Date de Sortie souhaitée :", datetime.now(), key="adv_search_start")
    with c_search2:
        search_date_fin = st.date_input("📅 Date de Retour prévue :", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style=\'height:28px;\'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")
        
        if search_date_debut > search_date_fin:            st.err
(Content truncated due to size limit. Use line ranges to read remaining content)
