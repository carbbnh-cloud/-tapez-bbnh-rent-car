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

# --- STYLE CSS (MÊME DESIGN) ---
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
.stTabs [data-baseweb="tab"]:hover { background-color: #222733; color: #ffffff; }
.stTabs [aria-selected="true"] { 
    background-color: #e60000 !important;
    color: #ffffff !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #e60000 0%, #b30000 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 28px !important;
    font-weight: 700 !important;
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
}
.car-info { display: flex; flex-direction: column; align-items: center; }
.car-image { width: 80px; height: auto; margin-bottom: 5px; }
.car-plate { font-weight: bold; color: #333; }
.status-badge {
    padding: 4px 10px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 11px;
}
.status-paid { background-color: #e6f7ed; color: #28a745; }
.status-pending { background-color: #fff4e6; color: #fd7e14; }
.km-box { display: flex; flex-direction: column; gap: 2px; align-items: center; }
.km-value { font-weight: bold; }
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

# --- NOMS DES TABLES SUPABASE (CORRECTS) ---
TABLE_CLIENT = "client"
TABLE_VEHICULE = "vehicule"
TABLE_MOUVEMENT = "mouvement"
TABLE_VIDANGE = "vidange"
TABLE_CONTRAT = "carbbnh"

# --- FONCTIONS SUPABASE ---
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except:
        return ""

@st.cache_data(ttl=60)
def get_all_data(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erreur table {table_name}: {e}")
        return pd.DataFrame()

def insert_data(table_name, data_dict):
    try:
        supabase.table(table_name).insert(data_dict).execute()
        return True
    except Exception as e:
        st.error(f"Erreur insert: {e}")
        return False

def update_data(table_name, data_dict, filters):
    try:
        supabase.table(table_name).update(data_dict).match(filters).execute()
        return True
    except Exception as e:
        st.error(f"Erreur update: {e}")
        return False

def delete_data(table_name, filters):
    try:
        supabase.table(table_name).delete().match(filters).execute()
        return True
    except Exception as e:
        st.error(f"Erreur delete: {e}")
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
df_voitures = get_all_data(TABLE_VEHICULE)
df_clients = get_all_data(TABLE_CLIENT)
df_mouvs = get_all_data(TABLE_MOUVEMENT)
df_vidanges = get_all_data(TABLE_VIDANGE)
df_contrats = get_all_data(TABLE_CONTRAT)

# --- LISTES SELECTBOX ---
liste_clients_opt = ["-- Entrée manuelle --"] + [
    f"{str(row.get('Nom', '')).upper()} {str(row.get('Prénom', ''))} (CIN: {row.get('CIN', '')})" 
    for _, row in df_clients.iterrows()
] if not df_clients.empty else ["-- Entrée manuelle --"]

liste_vehicules_opt = [
    str(row.get('Matricule', '')).strip() 
    for _, row in df_voitures.iterrows() 
    if pd.notna(row.get('Matricule'))
] if not df_voitures.empty else []

liste_vehicules_complets_opt = [
    f"{str(row.get('Matricule', '')).strip()} — {str(row.get('Modèle', row.get('Marque', 'Voiture')))}" 
    for _, row in df_voitures.iterrows()
] if not df_voitures.empty else []

# --- SIDEBAR ---
with st.sidebar:
    logo_path = "IMG_7149 (1).jpeg"
    if os.path.exists(logo_path):
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #e60000; font-weight:800;'>BBNH</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.5; font-size:13px; letter-spacing:4px;'>RENT A CAR</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-bottom:10px;'>🕹️ CONSOLE D'ACTION :</h3>", unsafe_allow_html=True)
    menu_action = st.radio(" ", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat / Réservation", 
        "🚗 Ajouter un Véhicule à la Flotte",
        "🗑️ Supprimer un Véhicule de la Flotte",
        "⚙️ Modifier un Dossier",
        "❌ Supprimer une opération"
    ], label_visibility="collapsed")

    st.markdown("<br><hr>", unsafe_allow_html=True)

# --- NOUVEAU CONTRAT ---
if menu_action == "📝 Nouveau Contrat / Réservation":
    st.sidebar.markdown("### 📝 Nouvelle fiche")
    nature = st.sidebar.selectbox("Nature : ", ["Contrat Location", "Réservation", "Maintenance / Garage"])
    vehicule = st.sidebar.selectbox("Véhicule : ", liste_vehicules_opt) if liste_vehicules_opt else st.sidebar.text_input("Véhicule : ")
    client_b = st.sidebar.selectbox("Client : ", liste_clients_opt)

    nom_m = st.sidebar.text_input("Nom & Prénom : ")
    cin_m = st.sidebar.text_input("N° C.I.N : ")
    dc_m = st.sidebar.date_input("Date Délivrance CIN : ", datetime.now() - timedelta(days=365))
    permis_m = st.sidebar.text_input("N° Permis : ")
    dp_m = st.sidebar.date_input("Date Délivrance Permis : ", datetime.now() - timedelta(days=365))

    f_cin = st.sidebar.file_uploader("Fichier CIN : ", type=["png", "jpg", "jpeg", "pdf"])
    f_permis = st.sidebar.file_uploader("Fichier Permis : ", type=["png", "jpg", "jpeg", "pdf"])

    st.sidebar.markdown("---")
    d1 = st.sidebar.date_input("Date Début : ", datetime.now())
    t1 = st.sidebar.time_input("Heure Début : ", time(9, 0))
    d2 = st.sidebar.date_input("Date Fin : ", datetime.now() + timedelta(days=2))
    t2 = st.sidebar.time_input("Heure Fin : ", time(12, 0))

    nbr_jours = max(1, (d2 - d1).days)
    st.sidebar.markdown(f"**Durée :** `{nbr_jours} jour(s)`")

    prix_unitaire = st.sidebar.number_input("Prix / Jour (DT) : ", min_value=0, value=100, step=5)
    montant_total = st.sidebar.number_input("Montant Total (DT) : ", min_value=0, value=nbr_jours * prix_unitaire)
    caution = st.sidebar.number_input("Caution (DT) : ", value=0)
    reste = montant_total - caution
    st.sidebar.markdown(f"**Reste à payer :** `{reste} DT`")

    km_debut = st.sidebar.number_input("Kilométrage Départ : ", min_value=0, value=0)
    l_reception = st.sidebar.text_input("Lieu : ", value="Siège Monastir")
    no_vol = st.sidebar.text_input("N° vol : ")
    info_note = st.sidebar.text_area("Note : ")

    if st.sidebar.button("⚡ ENREGISTRER"):
        nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[0]
        cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "").strip()
        str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
        str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
        
        img_cin_b64 = encoder_image_base64(f_cin)
        img_permis_b64 = encoder_image_base64(f_permis)
        
        # Insert client if manual
        if client_b == "-- Entrée manuelle --":
            insert_data(TABLE_CLIENT, {
                "Nom": nom_f, "CIN": cin_f,
                "Date Délivrance CIN": dc_m.strftime("%Y-%m-%d"),
                "N° Permis": permis_m,
                "Date Délivrance Permis": dp_m.strftime("%Y-%m-%d"),
                "Image CIN": img_cin_b64,
                "Image Permis": img_permis_b64
            })
        
        # Insert movement
        insert_data(TABLE_MOUVEMENT, {
            "Matricule": vehicule,
            "Type_Statut": "Location" if "Contrat" in nature else nature,
            "Date_Debut": str_d1,
            "Heure_Debut": str_t1,
            "Date_Fin": str_d2,
            "Heure_Fin": str_t2,
            "Client": nom_f,
            "Prix": str(montant_total),
            "Statut_Mouvement": "En cours",
            "Caution": str(caution),
            "Reste": str(reste),
            "Lieu_Reception": l_reception,
            "No_Vol": no_vol,
            "Info_Note": info_note,
            "KM_Debut": int(km_debut),
            "KM_Fin": 0
        })
        
        # Update vidange
        update_data(TABLE_VIDANGE, {"KM_Recent": int(km_debut), "Date_Mise_A_Jour": str_d1}, {"Matricule": vehicule})
        
        st.success("Enregistré avec succès !")
        st.rerun()

# --- AFFICHAGE PRINCIPAL ---
st.markdown("<h1>BBNH WORKSPACE</h1>", unsafe_allow_html=True)

# Tabs
tab_planning, tab_contrats, tab_vidange = st.tabs(["🗓️ PLANNING", "📄 CONTRATS", "🔧 VIDANGES"])

with tab_planning:
    st.markdown("### 🗓️ Planning 365 jours")
    if not df_voitures.empty:
        st.dataframe(df_voitures, use_container_width=True)
    else:
        st.info("Aucun véhicule")

with tab_contrats:
    st.markdown("### 📄 Contrats en cours")
    if not df_mouvs.empty:
        st.dataframe(df_mouvs, use_container_width=True)
    else:
        st.info("Aucun contrat")

with tab_vidange:
    st.markdown("### 🔧 Vidanges")
    if not df_vidanges.empty:
        st.dataframe(df_vidanges, use_container_width=True)
    else:
        st.info("Aucune vidange")
