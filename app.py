import streamlit as st
import pandas as pd
from supabase import create_client, Client
import base64
from datetime import datetime, timedelta, time
import os

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

div[data-testid="stSidebarUserContent"] {
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

div[data-testid="stRadio"] label {
    font-size: 15px !important;
    font-weight: 500 !important;
    padding: 8px 4px !important;
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
    transition: all 0.2s ease;
    border: none !important;
}
.stTabs [data-baseweb="tab"]:hover { background-color: #222733; color: #ffffff; }
.stTabs [aria-selected="true"] { 
    background-color: #e60000 !important;
    color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(230, 0, 0, 0.4);
}

h1 {
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    color: #ffffff !important;
}
h3 { color: #f3f4f6; font-weight: 700 !important; letter-spacing: -0.5px; }

div[data-testid="stForm"] {
    background: rgba(22, 25, 32, 0.8) !important;
    border: 1px solid #2a3142 !important;
    padding: 25px !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2) !important;
}

input, select, textarea, div[data-baseweb="select"] {
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

div[data-testid="stDataFrame"] {
    border: 1px solid #222733 !important;
    border-radius: 14px !important;
}

.contract-table {
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff;
    color: #333333;
    border-radius: 8px;
    overflow: hidden;
    font-size: 13px;
}
.contract-table th {
    background-color: #f8f9fa;
    color: #666;
    font-weight: 600;
    text-align: center;
    padding: 12px 8px;
    border-bottom: 1px solid #eee;
}
.contract-table td {
    padding: 12px 8px;
    border-bottom: 1px solid #eee;
    text-align: center;
    vertical-align: middle;
}
.car-info {
    display: flex;
    flex-direction: column;
    align-items: center;
}
.car-image {
    width: 80px;
    height: auto;
    margin-bottom: 5px;
}
.car-plate {
    font-weight: bold;
    color: #333;
}
.contract-num {
    font-weight: 800;
    font-size: 16px;
}
.status-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 11px;
    text-transform: uppercase;
}
.status-paid { background-color: #e6f7ed; color: #28a745; border: 1px solid #28a745; }
.status-pending { background-color: #fff4e6; color: #fd7e14; border: 1px solid #fd7e14; }

.km-box {
    display: flex;
    flex-direction: column;
    gap: 2px;
    align-items: center;
}
.km-value { font-weight: bold; margin-bottom: 2px; }
.km-indicator {
    width: 80px;
    padding: 2px 4px;
    color: white;
    font-size: 10px;
    font-weight: bold;
    border-radius: 3px;
}
.km-blue { background-color: #0000ff; }
.km-yellow { background-color: #ffff00; color: black; }
.km-purple { background-color: #800080; }
.km-black { background-color: #000000; }
.km-green { background-color: #008000; }
.km-red { background-color: #ff0000; }
.km-orange { background-color: #ffa500; }
</style>
""", unsafe_allow_html=True)

# --- CONFIGURATION SUPABASE ---
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# --- FONCTION D'ENCODAGE DES IMAGES EN TEXTE (BASE64) ---
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception as e:
        return ""

# --- FONCTIONS SUPABASE ---
@st.cache_data(ttl=60)
def get_all_data(table_name):
    """Récupérer toutes les données d'une table"""
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erreur de connexion à la table {table_name}: {e}")
        return pd.DataFrame()

def insert_data(table_name, data_dict):
    """Insérer une ligne"""
    try:
        response = supabase.table(table_name).insert(data_dict).execute()
        return True
    except Exception as e:
        st.error(f"Erreur d'insertion: {e}")
        return False

def update_data(table_name, data_dict, filters):
    """Mettre à jour des données"""
    try:
        response = supabase.table(table_name).update(data_dict).match(filters).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de mise à jour: {e}")
        return False

def delete_data(table_name, filters):
    """Supprimer des données"""
    try:
        response = supabase.table(table_name).delete().match(filters).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de suppression: {e}")
        return False

def formater_heure_propre(valeur_excel):
    if pd.isna(valeur_excel):
        return '00:00'
    if isinstance(valeur_excel, (datetime, time)):
        return valeur_excel.strftime('%H:%M')
    val_str = str(valeur_excel).strip()
    if " " in val_str:
        try: val_str = val_str.split(" ")[1]
        except: pass
    parts = val_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return '00:00'

# --- CHARGEMENT DES DONNÉES ---
df_voitures = get_all_data("stock")
df_clients = get_all_data("clients")
df_mouvs = get_all_data("mouvements")
df_vidanges = get_all_data("vidanges")
df_contrats = get_all_data("contrats")

# --- LISTES POUR SELECTBOX ---
liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row.get('Nom', '')).upper()} {str(row.get('Prénom', ''))} (CIN: {row.get('CIN', '')})" for _, row in df_clients.iterrows()] if not df_clients.empty else ["-- Entrée manuelle --"]

liste_vehicules_opt = [f"{str(row.get('Matricule', '')).strip()}" for _, row in df_voitures.iterrows() if pd.notna(row.get('Matricule')) and str(row.get('Matricule', '')).strip().lower() != 'nan'] if not df_voitures.empty else []

liste_vehicules_complets_opt = [f"{str(row.get('Matricule', '')).strip()} — {str(row.get('Modèle', row.get('Marque', 'Voiture')))}" for _, row in df_voitures.iterrows() if pd.notna(row.get('Matricule'))] if not df_voitures.empty else []

# --- SIDEBAR ---
with st.sidebar:
    logo_path = "IMG_7149 (1).jpeg"
    if os.path.exists(logo_path):
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #e60000; font-weight:800; margin-bottom:0;'>BBNH</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.5; font-size:13px; letter-spacing:4px; margin-bottom:25px;'>RENT A CAR</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-bottom:10px;'>🕹️ CONSOLE D'ACTION :</h3>", unsafe_allow_html=True)
    menu_action = st.radio(" ", [
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
                df_cli = pd.read_excel(f_clients, sheet_name='Base de Données', skiprows=1)
                df_cli = df_cli.loc[:, ~df_cli.columns.str.contains('^Unnamed')]
                # Convertir en liste de dicts et insérer
                data_to_insert = df_cli.to_dict('records')
                for row in data_to_insert:
                    insert_data("clients", row)
                st.success("Données clients synchronisées !")
                st.rerun()
            except Exception as e:
                st.error(f"Erreur : {e}")

        f_loc2 = st.file_uploader("Fichier Base LOC2", type=["xlsx"])
        if f_loc2:
            try:
                df_stock = pd.read_excel(f_loc2, sheet_name='Stock')
                df_mouv_raw = pd.read_excel(f_loc2, sheet_name='MOUVEMENTS')
                df_stock = df_stock.loc[:, ~df_stock.columns.str.contains('^Unnamed')]
                df_mouv_raw = df_mouv_raw.loc[:, ~df_mouv_raw.columns.str.contains('^Unnamed')]
                
                # Mapping des colonnes
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
                    elif "km_fin" in c_clean or "kilometrage_ret" in c_clean or "km_retour" in c_clean: mapping[col] = "KM_Fin"
                    elif "lieu" in c_clean: mapping[col] = "Lieu_Reception"
                
                df_mouv_raw = df_mouv_raw.rename(columns=mapping)ouv_raw = df_mouv_raw.rename(columns=mapping)
