import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
import base64
from datetime import datetime, timedelta, time

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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=300;400;500;600;700;800&display=swap');
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
div[data-testid="stSidebarUserContent"] { padding: 2rem 1.5rem !important; }
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
h1 { font-weight: 800 !important; letter-spacing: -1px !important; color: #ffffff !important; }
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
.car-info { display: flex; flex-direction: column; align-items: center; }
.car-image { width: 80px; height: auto; margin-bottom: 5px; }
.car-plate { font-weight: bold; color: #333; }
.contract-num { font-weight: 800; font-size: 16px; color: #e60000; }
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

# ============================================================
# CONFIGURATION SUPABASE
# ============================================================
@st.cache_resource
def init_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_supabase()

# Noms des tables Supabase
T_CLIENT = "client"
T_VEHICULE = "vehicule"
T_MOUVEMENT = "mouvement"
T_VIDANGE = "vidange"
T_CONTRAT = "carbbnh"

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except:
        return ""

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

# ============================================================
# FONCTIONS DATABASE SUPABASE
# ============================================================
@st.cache_data(ttl=30)
def get_all(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

def insert_row(table_name, data_dict):
    try:
        supabase.table(table_name).insert(data_dict).execute()
        return True
    except Exception as e:
        st.error(f"Erreur insert: {e}")
        return False

def update_row(table_name, data_dict, column, value):
    try:
        supabase.table(table_name).update(data_dict).eq(column, value).execute()
        return True
    except Exception as e:
        st.error(f"Erreur update: {e}")
        return False

def delete_row(table_name, column, value):
    try:
        supabase.table(table_name).delete().eq(column, value).execute()
        return True
    except Exception as e:
        st.error(f"Erreur delete: {e}")
        return False

def delete_all(table_name):
    try:
        supabase.table(table_name).delete().neq("id", 0).execute()
        return True
    except Exception as e:
        st.error(f"Erreur delete all: {e}")
        return False

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
df_voitures = get_all(T_VEHICULE)
df_clients = get_all(T_CLIENT)
df_mouvs = get_all(T_MOUVEMENT)
df_vidanges = get_all(T_VIDANGE)
df_contrats = get_all(T_CONTRAT)

# Synchroniser les vidanges pour chaque véhicule
if not df_voitures.empty:
    for _, car in df_voitures.iterrows():
        mat = str(car.get('Matricule', '')).strip()
        marq = str(car.get('Marque', '')).upper()
        if mat and mat.lower() != 'nan':
            existing = df_vidanges[df_vidanges['Matricule'] == mat] if not df_vidanges.empty else pd.DataFrame()
            if existing.empty:
                insert_row(T_VIDANGE, {
                    "Matricule": mat, "Marque": marq,
                    "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                    "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                    "KM_Dernier_Vidange": 0, "KM_Recent": 0
                })

# Listes pour selectbox
liste_clients_opt = ["-- Entrée manuelle --"] + [
    f"{str(row.get('Nom', '')).upper()} {str(row.get('Prénom', ''))} (CIN: {row.get('CIN', '')})" 
    for _, row in df_clients.iterrows()
] if not df_clients.empty else ["-- Entrée manuelle --"]

liste_vehicules_opt = [
    str(row.get('Matricule', '')).strip() 
    for _, row in df_voitures.iterrows() 
    if pd.notna(row.get('Matricule')) and str(row.get('Matricule', '')).strip().lower() != 'nan'
] if not df_voitures.empty else []

liste_vehicules_complets_opt = [
    f"{str(row.get('Matricule', '')).strip()} — {str(row.get('Modèle', row.get('Marque', 'Voiture')))}" 
    for _, row in df_voitures.iterrows() if pd.notna(row.get('Matricule'))
] if not df_voitures.empty else []

# ============================================================
# SIDEBAR
# ============================================================
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

# ============================================================
# FORMULAIRES SIDEBAR
# ============================================================
if menu_action == "📝 Nouveau Contrat / Réservation":
    st.sidebar.markdown("### 📝 Éditer une nouvelle fiche")
    nature = st.sidebar.selectbox("Nature : ", ["Contrat Location", "Réservation", "Maintenance / Garage"])
    vehicule = st.sidebar.selectbox("Véhicule : ", liste_vehicules_opt) if liste_vehicules_opt else st.sidebar.text_input("Véhicule : ")
    client_b = st.sidebar.selectbox("Client : ", liste_clients_opt)

    nom_m = st.sidebar.text_input("Nom & Prénom (Manuel) : ")
    cin_m = st.sidebar.text_input("N° C.I.N (Manuel) : ")
    dc_m = st.sidebar.date_input("Date Délivrance CIN : ", datetime.now() - timedelta(days=365))
    permis_m = st.sidebar.text_input("N° Permis (Manuel) : ")
    dp_m = st.sidebar.date_input("Date Délivrance Permis : ", datetime.now() - timedelta(days=365))

    f_cin = st.sidebar.file_uploader("Fichier CIN (Image/PDF) : ", type=["png", "jpg", "jpeg", "pdf"])
    f_permis = st.sidebar.file_uploader("Fichier Permis (Image/PDF) : ", type=["png", "jpg", "jpeg", "pdf"])

    st.sidebar.markdown("---")
    d1 = st.sidebar.date_input("Date Réception / Début : ", datetime.now())
    t1 = st.sidebar.time_input("Heure Réception : ", time(9, 0))
    d2 = st.sidebar.date_input("Date Fin / Retour : ", datetime.now() + timedelta(days=2))
    t2 = st.sidebar.time_input("Heure Fin : ", time(12, 0))

    nbr_jours = (d2 - d1).days
    if nbr_jours <= 0: nbr_jours = 1
    st.sidebar.markdown(f"**🔢 Durée estimée :** `{nbr_jours} jour(s)`")

    prix_unitaire = st.sidebar.number_input("💰 Prix Unitaire / Jour (DT) : ", min_value=0, value=100, step=5)
    total_auto = nbr_jours * prix_unitaire
    montant_total = st.sidebar.number_input("💵 Montant Total Calculé (DT) : ", min_value=0, value=int(total_auto))
    caution = st.sidebar.number_input("🛡️ Caution Déposée (DT) : ", value=0)
    reste = montant_total - caution
    st.sidebar.markdown(f"**🔴 Reste à payer :** `{reste} DT`")
    st.sidebar.markdown("---")

    km_debut = st.sidebar.number_input("Kilométrage au Départ : ", min_value=0, value=0, step=1)
    l_reception = st.sidebar.text_input("Lieu de réception : ", value="Siège Monastir")
    no_vol = st.sidebar.text_input("N° de vol : ", value="")
    info_note = st.sidebar.text_area("Note complémentaire : ")
    ref = st.sidebar.text_input("Code Contrat unique : ", f"BBNH-{datetime.now().strftime('%d%H%S')}")

    if st.sidebar.button("⚡ ENREGISTRER ON THE PLANNING"):
        nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[0]
        cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "").strip()
        str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
        str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
        text_type = "Location" if "Contrat" in nature else nature
        
        img_cin_b64 = encoder_image_base64(f_cin)
        img_permis_b64 = encoder_image_base64(f_permis)
        
        if client_b == "-- Entrée manuelle --":
            insert_row(T_CLIENT, {
                "Nom": nom_f, "CIN": cin_f,
                "Date Délivrance CIN": dc_m.strftime("%Y-%m-%d"),
                "N° Permis": permis_m,
                "Date Délivrance Permis": dp_m.strftime("%Y-%m-%d"),
                "Image CIN": img_cin_b64, "Image Permis": img_permis_b64
            })
        
        if "Contrat" in nature:
            insert_row(T_CONTRAT, {
                "Num_Contrat": ref, "Matricule": vehicule, "Client_Nom": nom_f, "CIN_Client": cin_f,
                "Date_Debut": str_d1, "Heure_Debut": str_t1, "Date_Fin": str_d2, "Heure_Fin": str_t2,
                "Tarif_Jour": str(prix_unitaire), "Montant_Total": str(montant_total), "Statut_Contrat": "Actif"
            })
        
        insert_row(T_MOUVEMENT, {
            "Matricule": vehicule, "Type_Statut": text_type,
            "Date_Debut": str_d1, "Heure_Debut": str_t1,
            "Date_Fin": str_d2, "Heure_Fin": str_t2,
            "Client": nom_f, "Prix": str(montant_total),
            "Statut_Mouvement": "En cours", "Caution": str(caution), "Reste": str(reste),
            "Lieu_Reception": l_reception, "No_Vol": no_vol, "Info_Note": info_note,
            "KM_Debut": int(km_debut), "KM_Fin": 0
        })
        
        update_row(T_VIDANGE, {"KM_Recent": int(km_debut), "Date_Mise_A_Jour": str_d1}, "Matricule", vehicule)
        
        st.success("Fiche créée avec succès !")
        st.cache_data.clear()
        st.rerun()

elif menu_action == "🚗 Ajouter un Véhicule à la Flotte":
    with st.sidebar.form("form_bbnh_add_car"):
        st.markdown("### 🚗 Nouveau Véhicule")
        nouveau_matricule = st.text_input("Matricule / Plaque * : ").strip()
        nouvelle_marque = st.text_input("Marque * : ").strip()
        nouveau_modele = st.text_input("Modèle * : ").strip()
        nouvelle_annee = st.text_input("Année : ", value="2026").strip()
        
        if st.form_submit_button("⚡ ENREGISTRER LE VEHICULE"):
            if nouveau_matricule and nouvelle_marque and nouveau_modele:
                combinaison_modele = f"{nouvelle_marque} {nouveau_modele}"
                insert_row(T_VEHICULE, {
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque,
                    "Modèle": nouveau_modele, "Année": nouvelle_annee,
                    "Marque/Model": combinaison_modele
                })
                insert_row(T_VIDANGE, {
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque.upper(),
                    "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                    "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                    "KM_Dernier_Vidange": 0, "KM_Recent": 0
                })
                st.success("Véhicule enregistré !")
                st.cache_data.clear()
                st.rerun()

elif menu_action == "🗑️ Supprimer un Véhicule de la Flotte":
    if liste_vehicules_complets_opt:
        with st.sidebar.form("form_bbnh_delete_car"):
            vehicule_a_retirer = st.selectbox("Choisir le véhicule à supprimer : ", liste_vehicules_complets_opt)
            confirmer_suppression = st.checkbox("Confirmer la suppression définitive")
            if st.form_submit_button("💥 SUPPRIMER LE VÉHICULE"):
                if confirmer_suppression:
                    matricule_pure = str(vehicule_a_retirer).split(" — ")[0].strip()
                    delete_row(T_VEHICULE, "Matricule", matricule_pure)
                    delete_row(T_VIDANGE, "Matricule", matricule_pure)
                    st.success("Véhicule retiré.")
                    st.cache_data.clear()
                    st.rerun()

elif menu_action == "⚙️ Modifier un Dossier (Contrat/Réservation)":
    if 'Statut_Mouvement' in df_mouvs.columns:
        df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours'] if not df_mouvs.empty else pd.DataFrame()
    else:
        df_mouv_actifs = df_mouvs if not df_mouvs.empty else pd.DataFrame()
    
    if not df_mouv_actifs.empty:
        liste_mouv_mod = [f"ID: {r.get('id', idx)} | {r.get('Matricule', '')} — {r.get('Client', '')}" for idx, r in df_mouv_actifs.iterrows()]
        mouv_selectionne = st.sidebar.selectbox("Sélectionner le dossier à éditer :", liste_mouv_mod)
        
        selected_id = mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip()
        row_init = df_mouv_actifs[df_mouv_actifs['id'] == int(selected_id)].iloc[0] if 'id' in df_mouv_actifs.columns else df_mouv_actifs.iloc[0]
        
        df_cli_spec = df_clients[df_clients['Nom'] == str(row_init.get('Client', ''))] if not df_clients.empty else pd.DataFrame()
        row_cli_init = df_cli_spec.iloc[0] if not df_cli_spec.empty else {}
        
        try: init_date_deb = datetime.strptime(str(row_init.get('Date_Debut', '')), "%Y-%m-%d").date()
        except: init_date_deb = datetime.now().date()
        try: init_date_fin = datetime.strptime(str(row_init.get('Date_Fin', '')), "%Y-%m-%d").date()
        except: init_date_fin = datetime.now().date()
        try: init_time_deb = datetime.strptime(formater_heure_propre(row_init.get('Heure_Debut', '')), "%H:%M").time()
        except: init_time_deb = time(9, 0)
        try: init_time_fin = datetime.strptime(formater_heure_propre(row_init.get('Heure_Fin', '')), "%H:%M").time()
        except: init_time_fin = time(12, 0)
        
        try: init_date_cin = datetime.strptime(str(row_cli_init.get('Date Délivrance CIN', '')), "%Y-%m-%d").date()
        except: init_date_cin = datetime.now().date()
        try: init_date_permis = datetime.strptime(str(row_cli_init.get('Date Délivrance Permis', '')), "%Y-%m-%d").date()
        except: init_date_permis = datetime.now().date()
        
        st.sidebar.markdown(f"### ⚙️ Édition Totale du Dossier #{selected_id}")
        mod_nature = st.sidebar.selectbox("Changer de Nature : ", ["Location", "Réservation", "Maintenance / Garage"], index=0)
        idx_v_init = liste_vehicules_opt.index(str(row_init.get('Matricule', '')).strip()) if str(row_init.get('Matricule', '')).strip() in liste_vehicules_opt else 0
        mod_vehicule = st.sidebar.selectbox("Changer de véhicule : ", liste_vehicules_opt, index=idx_v_init)
        
        st.sidebar.markdown("👤 **Informations Conducteur**")
        mod_client = st.sidebar.text_input("Nom & Prénom du Conducteur : ", value=str(row_init.get('Client', '')))
        mod_cin = st.sidebar.text_input("N° CIN : ", value=str(row_cli_init.get('CIN', '')))
        mod_date_cin = st.sidebar.date_input("Date de Délivrance CIN : ", init_date_cin)
        mod_permis = st.sidebar.text_input("N° Permis de Conduire : ", value=str(row_cli_init.get('N° Permis', '')))
        mod_date_permis = st.sidebar.date_input("Date de Délivrance Permis : ", init_date_permis)
        
        st.sidebar.markdown("---")
        c_d1, c_t1 = st.sidebar.columns(2)
        with c_d1: mod_d1 = st.sidebar.date_input("Date Début : ", init_date_deb, key="mod_d1")
        with c_t1: mod_t1 = st.sidebar.time_input("Heure Début : ", init_time_deb, key="mod_t1")
        c_d2, c_t2 = st.sidebar.columns(2)
        with c_d2: mod_d2 = st.sidebar.date_input("Date Fin : ", init_date_fin, key="mod_d2")
        with c_t2: mod_t2 = st.sidebar.time_input("Heure Fin / Retour : ", init_time_fin, key="mod_t2")
        
        mod_nbr_jours = (mod_d2 - mod_d1).days
        if mod_nbr_jours <= 0: mod_nbr_jours = 1
        st.sidebar.markdown(f"**🔢 Durée recalculée :** `{mod_nbr_jours} jour(s)`")
        
        mod_prix_unitaire = st.sidebar.number_input("💰 Prix Unitaire / Jour (DT) : ", min_value=0, value=100, key="mod_pu")
        mod_total_auto = mod_nbr_jours * mod_prix_unitaire
        mod_prix = st.sidebar.number_input("Prix Total Évalué (DT) : ", value=int(mod_total_auto), key="mod_tot")
        mod_caution = st.sidebar.number_input("Caution (DT) : ", value=0, key="mod_cau")
        mod_reste = mod_prix - mod_caution
        st.sidebar.markdown(f"**🔴 Reste à payer recalculé :** `{mod_reste} DT`")
        
        st.sidebar.markdown("---")
        mod_lieu = st.sidebar.text_input("Lieu de Réception : ", value=str(row_init.get('Lieu_Reception', 'Siège Monastir')))
        mod_vol = st.sidebar.text_input("N° Vol : ", value=str(row_init.get('No_Vol', '')))
        mod_km_deb = st.sidebar.number_input("Kilométrage Départ : ", min_value=0, value=int(row_init.get('KM_Debut', 0)))
        mod_note = st.sidebar.text_area("Note Interne : ", value=str(row_init.get('Info_Note', '')))
        
        if st.sidebar.button("💾 ENREGISTRER ABSOLUMENT TOUT"):
            str_mod_d1, str_mod_d2 = mod_d1.strftime("%Y-%m-%d"), mod_d2.strftime("%Y-%m-%d")
            str_mod_t1, str_mod_t2 = mod_t1.strftime("%H:%M"), mod_t2.strftime("%H:%M")
            
            update_row(T_CLIENT, {
                "Nom": mod_client, "Date Délivrance CIN": mod_date_cin.strftime("%Y-%m-%d"),
                "N° Permis": mod_permis, "Date Délivrance Permis": mod_date_permis.strftime("%Y-%m-%d")
            }, "CIN", mod_cin)
            
            update_row(T_MOUVEMENT, {
                "Matricule": mod_vehicule, "Type_Statut": mod_nature, "Client": mod_client,
                "Date_Debut": str_mod_d1, "Heure_Debut": str_mod_t1, "Date_Fin": str_mod_d2, "Heure_Fin": str_mod_t2,
                "Prix": str(mod_prix), "Caution": str(mod_caution), "Reste": str(mod_reste),
                "Lieu_Reception": mod_lieu, "No_Vol": mod_vol, "Info_Note": mod_note, "KM_Debut": int(mod_km_deb)
            }, "id", int(selected_id))
            
            update_row(T_VIDANGE, {"KM_Recent": int(mod_km_deb), "Date_Mise_A_Jour": str_mod_d1}, "Matricule", mod_vehicule)
            
            st.success("Toutes les données ont été mises à jour avec succès !")
            st.cache_data.clear()
            st.rerun()

elif menu_action == "❌ Supprimer une opération":
    if 'Statut_Mouvement' in df_mouvs.columns:
        df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours'] if not df_mouvs.empty else pd.DataFrame()
    else:
        df_mouv_actifs = df_mouvs if not df_mouvs.empty else pd.DataFrame()
    
    if not df_mouv_actifs.empty:
        liste_mouv_del = [f"ID: {r.get('id', idx)} | {r.get('Matricule', '')} — {r.get('Client', '')}" for idx, r in df_mouv_actifs.iterrows()]
        with st.sidebar.form("form_bbnh_delete_mouv"):
            mouv_selectionne = st.selectbox("Choisir l'opération à détruire : ", liste_mouv_del)
            confirmer_action = st.checkbox("Confirmer la suppression")
            if st.form_submit_button("💥 RETIRER DU PLANNING"):
                if confirmer_action:
                    id_to_delete = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
                    delete_row(T_MOUVEMENT, "id", id_to_delete)
                    st.success("Opération effacée !")
                    st.cache_data.clear()
                    st.rerun()

# ============================================================
# ESPACE CENTRAL
# ============================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION</h1>", unsafe_allow_html=True)

# Recherche avancée
with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    with c_search1: search_date_debut = st.date_input("📅 Date de Sortie souhaitée : ", datetime.now(), key="adv_search_start")
    with c_search2: search_date_fin = st.date_input("📅 Date de Retour prévue : ", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")
        
        df_disponibles = df_voitures.copy() if not df_voitures.empty else pd.DataFrame()
        if not df_mouvs.empty and not df_disponibles.empty:
            matricules_indisponibles = set()
            for _, mv in df_mouvs.iterrows():
                statut = mv.get('Statut_Mouvement', 'En cours')
                if statut == 'En cours':
                    try:
                        d_debut_mv = pd.to_datetime(mv.get('Date_Debut', ''), errors='coerce').date()
                        d_fin_mv = pd.to_datetime(mv.get('Date_Fin', ''), errors='coerce').date()
                        if d_debut_mv and d_fin_mv:
                            if not (d_fin_mv < search_date_debut or d_debut_mv > search_date_fin):
                                matricules_indisponibles.add(str(mv.get('Matricule', '')).strip())
                    except: pass
            df_disponibles = df_disponibles[~df_disponibles['Matricule'].isin(matricules_indisponibles)]
        
        if not df_disponibles.empty:
            st.markdown(f"##### 🚗 {len(df_disponibles)} Véhicule(s) disponible(s) du `{str_s_start}` au `{str_s_end}` :")
            df_disponibles_affichage = df_disponibles[['Matricule', 'Marque', 'Modèle', 'Année']].rename(
                columns={'Matricule': '🚘 Matricule / Plaque', 'Marque': 'Marque', 'Modèle': 'Modèle', 'Année': 'Année'}
            )
            st.dataframe(df_disponibles_affichage, use_container_width=True, hide_index=True)
        else:
            st.warning(f"❌ Désolé, aucun véhicule n'est disponible dans la flotte BBNH du {str_s_start} au {str_s_end}.")

st.markdown("<br>", unsafe_allow_html=True)

# Onglets
tab_planning, tab_contrats, tab_logistique, tab_analytics, tab_vidange, tab_crm, tab_admin = st.tabs([
    "🗓️ CORE PLANNING (365 JOURS)", "📄 LISTE DE CONTRAT", "🔑 BOX RECEPTION RETOURS",
    "📊 SUIVI DES PERFORMANCES", "🔧 SUIVI DES VIDANGES", "👥 COMPTE CONDUCTEURS (CRM)", "⚙️ PANNEAU DE CONFIGURATION"
])

# --- TAB 1 : PLANNING ---
with tab_planning:
    st.markdown("### 🗓️ Vue Globale & Filtres Intelligents")
    f_col_car, f_col_date_start, f_col_date_target = st.columns([2, 1.5, 1.5])
    with f_col_car:
        options_recherche_voiture = ["-- Toutes les voitures --"] + liste_vehicules_opt
        vehicule_recherche = st.selectbox("🚘 Filtrer par véhicule :", options_recherche_voiture)
    with f_col_date_start: date_base = st.date_input("Date de début de la grille :", datetime(2026, 1, 1), key="grid_bbnh_date")
    with f_col_date_target: recherche_date = st.date_input("📅 Aller à la date spécifique (Focus) :", datetime(2026, 6, 12))

    array_jours = [date_base + timedelta(days=i) for i in range(365)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    df_voitures_valides = df_voitures[df_voitures['Matricule'].notna() & (df_voitures['Matricule'].str.strip().str.lower() != 'nan')] if not df_voitures.empty else pd.DataFrame()

    if not df_voitures_valides.empty:
        build_matrix = []
        for _, car in df_voitures_valides.iterrows():
            immat = str(car.get('Matricule', '')).strip()
            if vehicule_recherche != "-- Toutes les voitures --" and immat != vehicule_recherche: continue
            modele = str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            ligne = {"Flotte BBNH": f"🚘 {modele} — [{immat}]"}
            for col_j in nom_colonnes: ligne[col_j] = "● Disponible"
            build_matrix.append(ligne)

        if len(build_matrix) > 0:
            df_final_grid = pd.DataFrame(build_matrix)
            if not df_mouvs.empty and not df_final_grid.empty:
                suivi_jours = {}
                for _, mv in df_mouvs.iterrows():
                    if pd.isna(mv.get('Matricule')) or pd.isna(mv.get('Date_Debut')) or pd.isna(mv.get('Date_Fin')): continue
                    m_v = str(mv.get('Matricule', '')).strip()
                    s_v = str(mv.get('Type_Statut', '')).strip().lower()
                    client_v = str(mv.get('Client', '')).strip()
                    h_deb_label = formater_heure_propre(mv.get('Heure_Debut', ''))
                    h_fin_label = formater_heure_propre(mv.get('Heure_Fin', ''))

                    try:
                        d_debut_mv = pd.to_datetime(mv.get('Date_Debut', ''), errors='coerce').date()
                        d_fin_mv = pd.to_datetime(mv.get('Date_Fin', ''), errors='coerce').date()
                        if m_v not in suivi_jours: suivi_jours[m_v] = {}
                        for j in array_jours:
                            if d_debut_mv <= j <= d_fin_mv:
                                key_day = j.strftime("%d/%m")
                                if key_day not in suivi_jours[m_v]:
                                    suivi_jours[m_v][key_day] = {"depart": False, "fin": False, "client_sortant": "", "client_entrant": "", "heure_sortie": "00:00", "heure_retour": "00:00", "desc": "", "type": s_v}
                                if j == d_debut_mv: 
                                    suivi_jours[m_v][key_day]["depart"] = True
                                    suivi_jours[m_v][key_day]["client_sortant"] = client_v
                                    suivi_jours[m_v][key_day]["heure_sortie"] = h_deb_label
                                if j == d_fin_mv: 
                                    suivi_jours[m_v][key_day]["fin"] = True
                                    suivi_jours[m_v][key_day]["client_entrant"] = client_v
                                    suivi_jours[m_v][key_day]["heure_retour"] = h_fin_label
                                
                                if not (suivi_jours[m_v][key_day]["depart"] and suivi_jours[m_v][key_day]["fin"]):
                                    if "garage" in s_v or "maintenance" in s_v: suivi_jours[m_v][key_day]["desc"] = f"🛠️ GARAGE : {client_v}"
                                    elif "réservation" in s_v: suivi_jours[m_v][key_day]["desc"] = f"🔴 [{h_deb_label}➔{h_fin_label}] {client_v}"
                                    else: suivi_jours[m_v][key_day]["desc"] = f"🟢 [{h_deb_label}➔{h_fin_label}] {client_v}"
                    except: pass

            for idx, row in df_final_grid.iterrows():
                mat_extracted = row["Flotte BBNH"].split("[")[-1].replace("]", "").strip()
                if mat_extracted in suivi_jours:
                    for key_day, data in suivi_jours[mat_extracted].items():
                        if key_day in df_final_grid.columns:
                            if data["depart"] and data["fin"]:
                                df_final_grid.at[idx, key_day] = f"🔵 🛬{data['heure_retour']} {data['client_entrant']} / 🛫{data['heure_sortie']} {data['client_sortant']}"
                            elif data["desc"] != "": df_final_grid.at[idx, key_day] = data["desc"]

           def style_bbnh_theme(val):
    val_str = str(val).lower()
    
    # Disponible (blanc)
    if "disponible" in val_str or "●" in val_str:
        return "background-color: #ffffff !important; color: #111827 !important; font-size: 11px !important; font-weight: 600 !important; text-align: center !important; border: 1px solid #e5e7eb !important;"
    
    # Retour + Départ même jour (bleu)
    elif "🛬" in val_str and "🛫" in val_str:
        return "background-color: #1d4ed8 !important; color: #ffffff !important; font-weight: 700 !important; font-size: 10px !important; border: 2px solid #60a5fa !important;"
    
    # Garage / Maintenance (jaune)
    elif "garage" in val_str or "maintenance" in val_str or "🛠️" in val_str:
        return "background-color: #eab308 !important; color: #1e1b4b !important; font-weight: 700 !important; font-size: 11px !important;"
    
    # Réservation (rouge)
    elif "réservation" in val_str or "reservation" in val_str or "🔴" in val_str:
        return "background-color: #dc2626 !important; color: #ffffff !important; font-weight: 600 !important; font-size: 11px !important;"
    
    # Location (vert)
    elif "location" in val_str or "🟢" in val_str:
        return "background-color: #16a34a !important; color: #ffffff !important; font-weight: 600 !important; font-size: 11px !important;"
    
    # Par défaut (noir avec bordure rouge)
    else:
        return "background-color: #090b0e !important; color: #ffffff !important; font-weight: 700 !important; font-size: 12px !important; border-right: 3px solid #e60000 !important;"

            target_col_str = recherche_date.strftime("%d/%m")
            cols_ordonnees = ['Flotte BBNH']
            if target_col_str in nom_colonnes:
                idx_target = nom_colonnes.index(target_col_str)
                cols_ordonnees += nom_colonnes[max(0, idx_target - 2):min(365, idx_target + 12)]
            st.dataframe(df_final_grid[cols_ordonnees].style.map(style_bbnh_theme, subset=[c for c in cols_ordonnees if c != 'Flotte BBNH']), use_container_width=True, height=800)

# ============================================================
# TAB 2 : LISTE DE CONTRAT (VERSION CORRIGÉE)
# ============================================================
with tab_contrats:
    st.markdown("### 📄 Liste Détaillée des Contrats & Mouvements")
    
    # Trier par ID décroissant
    if 'id' in df_mouvs.columns:
        df_contrats_list = df_mouvs.sort_values(by='id', ascending=False)
    else:
        df_contrats_list = df_mouvs
    
    if not df_contrats_list.empty:
        # Construction du tableau HTML
        html_table = """
        <table class="contract-table">
            <thead>
                <tr>
                    <th>🚗 Matricule</th>
                    <th>📞 N° Tel</th>
                    <th>📋 N° Contrat</th>
                    <th>📅 Date Départ</th>
                    <th>📅 Date Retour</th>
                    <th>📆 Jours</th>
                    <th>💰 Montant TTC (DT)</th>
                    <th>💸 Reste (DT)</th>
                    <th>🎁 Extras</th>
                    <th>🛣️ KM Sortie</th>
                    <th>🏁 KM Retour</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for _, row in df_contrats_list.iterrows():
            try:
                # 1. MATRICULE
                matricule = str(row.get('Matricule', 'N/A')).strip()
                
                # 2. NUMÉRO DE TÉLÉPHONE (recherche avec tolérance)
                tel = "N/A"
                client = str(row.get('Client', '')).strip()
                if client and client != 'nan' and client != '' and not df_clients.empty:
                    # Recherche exacte d'abord
                    df_tel = df_clients[df_clients['Nom'] == client]
                    if df_tel.empty:
                        # Recherche partielle si échec
                        df_tel = df_clients[df_clients['Nom'].str.contains(client, case=False, na=False)]
                    
                    if not df_tel.empty:
                        tel_val = df_tel.iloc[0].get('Numéro de téléphone', 'N/A')
                        if pd.notna(tel_val) and str(tel_val).strip() != '' and str(tel_val).lower() != 'nan':
                            tel = str(tel_val)
                
                # 3. N° CONTRAT (formaté #0001)
                if 'id' in row.index and pd.notna(row.get('id')):
                    try:
                        num_contrat = f"#{int(row.get('id', 0)):04d}"
                    except:
                        num_contrat = matricule
                else:
                    num_contrat = matricule
                
                # 4. DATE DÉPART
                try:
                    d_dep = datetime.strptime(str(row.get('Date_Debut', '')), "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    d_dep = str(row.get('Date_Debut', 'N/A'))
                
                # 5. DATE RETOUR
                try:
                    d_ret = datetime.strptime(str(row.get('Date_Fin', '')), "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    d_ret = str(row.get('Date_Fin', 'N/A'))
                
                # 6. NOMBRE DE JOURS
                try:
                    d_dep_dt = datetime.strptime(str(row.get('Date_Debut', '')), "%Y-%m-%d")
                    d_ret_dt = datetime.strptime(str(row.get('Date_Fin', '')), "%Y-%m-%d")
                    jours = (d_ret_dt - d_dep_dt).days
                    if jours <= 0: jours = 1
                except:
                    jours = "?"
                
                # 7. MONTANT TTC
                try:
                    prix_val = row.get('Prix', 0)
                    if pd.isna(prix_val) or str(prix_val).strip() == '' or str(prix_val).lower() == 'nan':
                        prix_val = 0
                    montant = f"{float(prix_val):,.3f}"
                except:
                    montant = "0.000"
                
                # 8. RESTE
                try:
                    reste_val = row.get('Reste', 0)
                    if pd.isna(reste_val) or str(reste_val).strip() == '' or str(reste_val).lower() == 'nan':
                        reste_val = 0
                    reste_val = float(reste_val)
                except:
                    reste_val = 0.0
                
                reste_style = "status-paid" if reste_val <= 0 else "status-pending"
                reste_text = "PAYÉ" if reste_val <= 0 else f"{reste_val:,.3f}"
                
                # 9. EXTRAS (Caution)
                try:
                    caution_val = row.get('Caution', 0)
                    if pd.isna(caution_val) or str(caution_val).strip() == '' or str(caution_val).lower() == 'nan':
                        caution_val = 0
                    caution_display = f"{float(caution_val):,.3f}"
                except:
                    caution_display = "0.000"
                
                # 10. KM SORTIE
                try:
                    km_s = int(row.get('KM_Debut', 0))
                    if pd.isna(km_s): km_s = 0
                except:
                    km_s = 0
                
                # 11. KM RETOUR
                try:
                    km_r = int(row.get('KM_Fin', 0))
                    if pd.isna(km_r): km_r = 0
                except:
                    km_r = 0
                
                # Construction de la ligne HTML
                html_table += f"""
                    <tr>
                        <td>
                            <div class="car-info">
                                <img src="https://img.icons8.com/ios-filled/50/000000/car.png" class="car-image">
                                <div class="car-plate">{matricule}</div>
                                <div style="font-size:10px; color:#666;">Location</div>
                            </div>
                        </td>
                        <td style="color:#007bff; font-weight:bold; font-size:14px;">{tel}</td>
                        <td>
                            <div class="contract-num">{num_contrat}</div>
                            <div style="display:flex; justify-content:center; gap:5px; margin-top:5px;">
                                <span>📄</span> <span>🖨️</span>
                            </div>
                        </td>
                        <td style="font-weight:600;">{d_dep}</td>
                        <td style="font-weight:600;">{d_ret}</td>
                        <td style="font-weight:bold; font-size:16px; color:#e60000;">{jours} j</td>
                        <td style="font-weight:bold; font-size:14px;">{montant}</td>
                        <td><span class="status-badge {reste_style}">✔ {reste_text}</span></td>
                        <td>
                            <div style="background:#f1f3f5; padding:8px; border-radius:4px; font-size:11px;">
                                <span style="color:green;">✔</span><br>
                                <strong>{caution_display} DT</strong>
                            </div>
                        </td>
                        <td>
                            <div class="km-box">
                                <div class="km-value" style="color:#28a745; font-size:16px;">{km_s} Km</div>
                                <div class="km-indicator km-blue">{km_s // 100} Km/Ess</div>
                                <div class="km-indicator km-yellow">{km_s // 200} Km/j</div>
                            </div>
                        </td>
                        <td>
                            <div class="km-box">
                                <div class="km-value" style="color:#dc3545; font-size:16px;">{km_r} Km</div>
                                <div class="km-indicator km-green">{km_r // 200} Km/j</div>
                                <div class="km-indicator km-red">{km_r // 100} Km/Ess</div>
                            </div>
                        </td>
                    </tr>
                """
            except Exception as e:
                # Si une ligne cause une erreur, on la saute
                continue
        
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("Aucun contrat ou mouvement enregistré.")

# --- TAB 3 : RECEPTION LOGISTIQUE ---
with tab_logistique:
    st.markdown("### 🔑 Terminal de Restitution et Clôture")
    if 'Statut_Mouvement' in df_mouvs.columns:
        df_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours'] if not df_mouvs.empty else pd.DataFrame()
    else:
        df_actifs = df_mouvs if not df_mouvs.empty else pd.DataFrame()
    
    if not df_actifs.empty:
        choix_actifs = [f"ID: {r.get('id', idx)} | {r.get('Matricule', '')} — {r.get('Client', '')}" for idx, r in df_actifs.iterrows()]
        col_list, col_details = st.columns([1, 1])
        with col_list:
            target_v = st.selectbox("Sélectionner le véhicule rentrant : ", choix_actifs)
            d_reel = st.date_input("Date de retour physique effective : ", datetime.now())
            t_reel = st.time_input("Heure de retour effective : ", datetime.now().time())
            l_retour = st.text_input("Lieu de retour effectif : ", value="Siège Monastir")
            
            id_mouv_temp = target_v.split(" | ")[0].replace("ID: ", "").strip()
            km_dep_de_base = 0
            if id_mouv_temp:
                res_dep = df_actifs[df_actifs['id'] == int(id_mouv_temp)] if 'id' in df_actifs.columns else df_actifs.iloc[[0]]
                if not res_dep.empty:
                    try: km_dep_de_base = int(float(str(res_dep.iloc[0].get('KM_Debut', 0)).replace(' ', '')))
                    except: km_dep_de_base = 0
            
            km_fin = st.number_input("Kilométrage au Retour : ", min_value=km_dep_de_base, value=km_dep_de_base, step=1)
            
            if st.button("✅ VALIDATION DU RETOUR", use_container_width=True):
                str_t_reel = t_reel.strftime("%H:%M")
                vehicule_rentre = str(res_dep.iloc[0].get('Matricule', '')) if not res_dep.empty else ''
                update_row(T_MOUVEMENT, {"Statut_Mouvement": "Retourné", "Date_Fin": d_reel.strftime("%Y-%m-%d"), "Heure_Fin": str_t_reel, "Lieu_Reception": l_retour, "KM_Fin": int(km_fin)}, "id", int(id_mouv_temp))
                update_row(T_VIDANGE, {"KM_Recent": int(km_fin), "Date_Mise_A_Jour": d_reel.strftime("%Y-%m-%d")}, "Matricule", vehicule_rentre)
                st.success("Le retour a été validé et mis à jour pour le suivi des vidanges !")
                st.cache_data.clear()
                st.rerun()
        with col_details:
            if id_mouv_temp:
                row_sel = df_actifs[df_actifs['id'] == int(id_mouv_temp)].iloc[0] if 'id' in df_actifs.columns else df_actifs.iloc[0]
                diff_km = int(km_fin) - int(km_dep_de_base)
                st.markdown(f"**📊 Distance Parcourue :** <span style='color:#4ade80; font-weight:bold; font-size:22px;'>{diff_km} KM</span>", unsafe_allow_html=True)
                st.write(f"**Reste dû :** {row_sel.get('Reste', '0')} DT")
    else: st.info("Aucun déplacement en cours.")

# --- TAB 4 : PERFORMANCE ---
with tab_analytics:
    st.markdown("### 📊 Chiffre d'Affaires & Synthèse Logistique du Jour")
    day_target = st.date_input("Sélectionner la journée d'analyse :", datetime.now())
    if not df_mouvs.empty:
        df_stats = df_mouvs.copy()
        df_stats['Clean_D'] = pd.to_datetime(df_stats['Date_Debut'], errors='coerce').dt.date
        df_stats['Clean_F'] = pd.to_datetime(df_stats['Date_Fin'], errors='coerce').dt.date
        try:
            df_stats['KM_Debut'] = pd.to_numeric(df_stats['KM_Debut'], errors='coerce').fillna(0).astype(int)
            df_stats['KM_Fin'] = pd.to_numeric(df_stats['KM_Fin'], errors='coerce').fillna(0).astype(int)
        except: pass
        
        if 'Prix' in df_stats.columns:
            df_stats['Val_Prix'] = df_stats['Prix'].astype(str).str.replace(' ', '').str.replace('DT', '').str.replace(',', '.')
            df_stats['Val_Prix'] = pd.to_numeric(df_stats['Val_Prix'], errors='coerce').fillna(0.0)
        else:
            df_stats['Val_Prix'] = 0.0
        
        sorties = df_stats[df_stats['Clean_D'] == day_target]
        entrees = df_stats[df_stats['Clean_F'] == day_target]
        
        k1, k2, k3 = st.columns(3)
        with k1: st.metric("📈 DÉPARTS CONSTATÉS", f"{len(sorties)} Véhicule(s)")
        with k2: st.metric("🔑 RETOURS ENREGISTRÉS", f"{len(entrees)} Véhicule(s)")
        with k3: st.metric("💰 CA DU JOUR (DÉPARTS)", f"{sorties['Val_Prix'].sum():,.2f} DT")
        
        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("### 🛫 1. VOITURES SORTIES (DÉPARTS)")
            if not sorties.empty:
                sorties_final = sorties[['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Prix', 'KM_Debut']].rename(columns={'Matricule': '🚘 Matricule', 'Client': '👤 Client', 'Date_Debut': '📅 DATE SORTIE', 'Date_Fin': '📅 DATE RETOUR PRÉVUE', 'Prix': '💰 PRIX (DT)', 'KM_Debut': '🔢 KM SORTIE'})
                st.dataframe(sorties_final, use_container_width=True, hide_index=True)
            else: st.info("Aucun véhicule n'est parti à cette date.")
        with col_droite:
            st.markdown("### 🛬 2. VOITURES RETOURNÉES (RETOURS)")
            if not entrees.empty:
                entrees['KM Roulé'] = entrees.apply(lambda r: (r['KM_Fin'] - r['KM_Debut']) if r['KM_Fin'] > r['KM_Debut'] else 0, axis=1)
                entrees['Heure_Retour_Propre'] = entrees['Heure_Fin'].apply(formater_heure_propre)
                entrees_final = entrees[['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Heure_Retour_Propre', 'Lieu_Reception', 'Prix', 'KM_Debut', 'KM_Fin', 'KM Roulé']].rename(columns={'Matricule': '🚘 Matricule', 'Client': '👤 Client', 'Date_Debut': '📅 DATE SORTIE', 'Date_Fin': '📅 DATE RETOUR', 'Heure_Retour_Propre': '🕒 HEURE RETOUR', 'Lieu_Reception': '📍 LIEU DE RETOUR', 'Prix': '💰 PRIX TOTAL (DT)', 'KM_Debut': '🔢 KM SORTIE', 'KM_Fin': '🔢 KM RETOUR', 'KM Roulé': '🔥 KM ROULÉ'})
                st.dataframe(entrees_final, use_container_width=True, hide_index=True)
            else: st.info("Aucun retour physique enregistré à cette date.")

# --- TAB 5 : VIDANGES ---
with tab_vidange:
    st.markdown("### 🔧 Tableau de bord de Maintenance & Vidanges Automatisé")
    if not df_vidanges.empty:
        df_v_base = df_vidanges.copy()
        try:
            df_v_base['KM_Dernier_Vidange'] = pd.to_numeric(df_v_base['KM_Dernier_Vidange'], errors='coerce').fillna(0).astype(int)
            df_v_base['KM_Recent'] = pd.to_numeric(df_v_base['KM_Recent'], errors='coerce').fillna(0).astype(int)
        except: pass
        df_v_base['KM cerculer'] = df_v_base['KM_Recent'] - df_v_base['KM_Dernier_Vidange']
        df_v_base['km restant'] = 9000 - df_v_base['KM cerculer']
        
        alertes_critiques = df_v_base[df_v_base['km restant'] <= 1500]
        if not alertes_critiques.empty: st.error(f"⚠️ **ALERTE VIDANGE :** {len(alertes_critiques)} véhicule(s) doivent être vidangés immédiatement !")
        else: st.success("✅ État de la flotte parfait : aucune vidange urgente.")
        
        df_tableau_affichage = df_v_base[['Date_Mise_A_Jour', 'Marque', 'Matricule', 'Date_Dernier_Vidange', 'KM_Dernier_Vidange', 'KM_Recent', 'KM cerculer', 'km restant']].rename(columns={'Date_Mise_A_Jour': 'DATE MIS AJOURS', 'Marque': 'MARQUE', 'Matricule': 'MATRICULE', 'Date_Dernier_Vidange': 'TE DERNIER VIDAN', 'KM_Dernier_Vidange': 'DERNIER VIDA', 'KM_Recent': 'KM RECENT', 'KM cerculer': 'KM cerculer', 'km restant': 'km restant'})
        
        def colorer_vidanges(row):
            val_restant = row['km restant']
            if val_restant <= 500: return ['background-color: #ef4444; color: white; font-weight: bold;'] * len(row)
            elif val_restant <= 1500: return ['background-color: #f97316; color: white; font-weight: bold;'] * len(row)
            return [''] * len(row)

        st.dataframe(df_tableau_affichage.style.apply(colorer_vidanges, axis=1), use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            c_v1, c_v2, c_v3 = st.columns([1.5, 1.5, 2])
            with c_v1:
                v_select = st.selectbox("Sélectionner le véhicule à mettre à jour : ", df_v_base['Matricule'].tolist())
                v_info = df_v_base[df_v_base['Matricule'] == v_select].iloc[0]
                try: init_date_dernier = datetime.strptime(str(v_info.get('Date_Dernier_Vidange', '')), "%Y-%m-%d").date()
                except: init_date_dernier = datetime.now().date()
                date_dernier_manuel = st.date_input("Date du Dernier Vidange (Manuel) : ", value=init_date_dernier)
            with c_v2:
                dernier_km_vidange_input = st.number_input("Dernier KM Vidange (Manuel) : ", min_value=0, value=int(v_info.get('KM_Dernier_Vidange', 0)), step=1)
                nouveau_km_actuel = st.number_input("Kilométrage Actuel / Récent (Manuel) : ", min_value=0, value=int(v_info.get('KM_Recent', 0)), step=1)
            with c_v3:
                date_effective = st.date_input("Date effective de l'opération : ", datetime.now())
                action_sync = st.checkbox("Vidange effectuée aujourd'hui (Synchronise le dernier KM et remet à zéro)", value=False)
            
            if st.button("💾 ENREGISTRER ET RECALCULER DIRECTEMENT", use_container_width=True):
                date_operation_str = date_effective.strftime("%Y-%m-%d")
                date_historique_str = date_dernier_manuel.strftime("%Y-%m-%d")
                if action_sync:
                    update_row(T_VIDANGE, {"KM_Recent": int(nouveau_km_actuel), "KM_Dernier_Vidange": int(nouveau_km_actuel), "Date_Dernier_Vidange": date_operation_str, "Date_Mise_A_Jour": date_operation_str}, "Matricule", v_select)
                else:
                    update_row(T_VIDANGE, {"KM_Recent": int(nouveau_km_actuel), "KM_Dernier_Vidange": int(dernier_km_vidange_input), "Date_Dernier_Vidange": date_historique_str, "Date_Mise_A_Jour": date_operation_str}, "Matricule", v_select)
                st.success("Calculs mis à jour instantanément !")
                st.cache_data.clear()
                st.rerun()

# --- TAB 6 : CRM ---
with tab_crm:
    st.markdown("### 👥 Banque d'Information des Conducteurs & Profils Clients")
    c1, c2 = st.columns([5, 4])
    with c1:
        st.markdown("#### 🔍 Consultation & Actions")
        search_query = st.text_input("Rechercher un profil (Nom, Prénom, CIN) : ", key="crm_search_field")
        if search_query:
            clients_trouves = df_clients[
                (df_clients['Nom'].str.contains(search_query, case=False, na=False)) |
                (df_clients['Prénom'].str.contains(search_query, case=False, na=False)) |
                (df_clients['CIN'].str.contains(search_query, case=False, na=False))
            ] if not df_clients.empty else pd.DataFrame()
            
            if not clients_trouves.empty:
                for idx, cli in clients_trouves.iterrows():
                    cin_client_actuel = str(cli.get('CIN', '')).strip()
                    unique_suffix = f"{idx}_{cin_client_actuel}"
                    with st.expander(f"👤 {str(cli.get('Nom', '')).upper()} {cli.get('Prénom', '')} (CIN: {cin_client_actuel})", expanded=True):
                        st.write(f"**📞 Téléphone :** `{cli.get('Numéro de téléphone', 'N/A')}` | **🚗 N° Permis :** `{cli.get('N° Permis', 'N/A')}`")
                        st.write(f"📅 **Délivrance CIN :** `{cli.get('Date Délivrance CIN', 'N/A')}` | 📅 **Délivrance Permis :** `{cli.get('Date Délivrance Permis', 'N/A')}`")
                        col_img1, col_img2 = st.columns(2)
                        with col_img1:
                            if cli.get('Image CIN'):
                                try: st.image(base64.b64decode(cli['Image CIN']), caption="Pièce d'identité (CIN)", use_container_width=True)
                                except: pass
                        with col_img2:
                            if cli.get('Image Permis'):
                                try: st.image(base64.b64decode(cli['Image Permis']), caption="Permis de conduire", use_container_width=True)
                                except: pass
                        st.markdown("---")
                        col_btn_mod, col_btn_sup = st.columns(2)
                        with col_btn_mod:
                            if st.button(f"✏️ MODIFIER CE PROFIL", key=f"btn_edit_{unique_suffix}"): st.session_state[f"mode_edition_{unique_suffix}"] = True
                        with col_btn_sup:
                            check_sup = st.checkbox("Confirmer la suppression", key=f"chk_del_{unique_suffix}")
                            if st.button(f"🗑️ SUPPRIMER CE CLIENT", key=f"btn_del_{unique_suffix}"):
                                if check_sup:
                                    delete_row(T_CLIENT, "CIN", cin_client_actuel)
                                    st.success(f"Client [CIN: {cin_client_actuel}] supprimé définitivement.")
                                    st.cache_data.clear()
                                    st.rerun()
                                else: st.warning("Veuillez cocher la case de confirmation avant de supprimer.")
                        
                        if st.session_state.get(f"mode_edition_{unique_suffix}", False):
                            st.markdown("<br>", unsafe_allow_html=True)
                            with st.form(key=f"form_reel_edit_{unique_suffix}"):
                                st.markdown("##### 📝 Édition des informations")
                                e_prenom = st.text_input("Prénom", value=str(cli.get('Prénom', '')))
                                e_nom = st.text_input("Nom", value=str(cli.get('Nom', '')))
                                e_tel = st.text_input("Téléphone", value=str(cli.get('Numéro de téléphone', '')))
                                e_permis = st.text_input("N° Permis", value=str(cli.get('N° Permis', '')))
                                try: e_init_d_cin = datetime.strptime(str(cli.get('Date Délivrance CIN', '')), "%Y-%m-%d").date()
                                except: e_init_d_cin = datetime.now().date()
                                try: e_init_d_per = datetime.strptime(str(cli.get('Date Délivrance Permis', '')), "%Y-%m-%d").date()
                                except: e_init_d_per = datetime.now().date()
                                e_d_cin = st.date_input("Date Délivrance CIN", value=e_init_d_cin)
                                e_d_per = st.date_input("Date Délivrance Permis", value=e_init_d_per)
                                f_cin_remplace = st.file_uploader("Remplacer l'image CIN (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_cin_{unique_suffix}")
                                f_per_remplace = st.file_uploader("Remplacer l'image Permis (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_per_{unique_suffix}")
                                if st.form_submit_button("✅ METTRE À JOUR"):
                                    update_data = {"Prénom": e_prenom, "Nom": e_nom, "Numéro de téléphone": e_tel, "N° Permis": e_permis, "Date Délivrance CIN": e_d_cin.strftime("%Y-%m-%d"), "Date Délivrance Permis": e_d_per.strftime("%Y-%m-%d")}
                                    if f_cin_remplace: update_data["Image CIN"] = encoder_image_base64(f_cin_remplace)
                                    if f_per_remplace: update_data["Image Permis"] = encoder_image_base64(f_per_remplace)
                                    update_row(T_CLIENT, update_data, "CIN", cin_client_actuel)
                                    st.success("Profil mis à jour !")
                                    st.session_state[f"mode_edition_{unique_suffix}"] = False
                                    st.cache_data.clear()
                                    st.rerun()

    with c2:
        st.markdown("#### ➕ Ajouter un Nouveau Client")
        with st.form("form_new_client_crm"):
            n_prenom = st.text_input("Prénom *")
            n_nom = st.text_input("Nom *")
            n_cin = st.text_input("N° CIN *")
            n_tel = st.text_input("Téléphone")
            n_permis = st.text_input("N° Permis")
            n_d_cin = st.date_input("Date Délivrance CIN", value=datetime.now() - timedelta(days=365))
            n_d_per = st.date_input("Date Délivrance Permis", value=datetime.now() - timedelta(days=365))
            f_cin_new = st.file_uploader("Image CIN", type=["png", "jpg", "jpeg"])
            f_per_new = st.file_uploader("Image Permis", type=["png", "jpg", "jpeg"])
            if st.form_submit_button("⚡ CRÉER LE PROFIL CLIENT"):
                if n_prenom and n_nom and n_cin:
                    insert_row(T_CLIENT, {"Prénom": n_prenom, "Nom": n_nom, "CIN": n_cin, "Numéro de téléphone": n_tel, "N° Permis": n_permis, "Date Délivrance CIN": n_d_cin.strftime("%Y-%m-%d"), "Date Délivrance Permis": n_d_per.strftime("%Y-%m-%d"), "Image CIN": encoder_image_base64(f_cin_new), "Image Permis": encoder_image_base64(f_per_new)})
                    st.success("Nouveau client enregistré !")
                    st.cache_data.clear()
                    st.rerun()
                else: st.error("Veuillez remplir les champs obligatoires (*)")

# --- TAB 7 : ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Panneau de Configuration Système")
    st.warning("Attention : Ces actions sont irréversibles.")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🗑️ PURGER TOUS LES MOUVEMENTS"):
            if st.checkbox("Confirmer la purge des mouvements"):
                delete_all(T_MOUVEMENT)
                st.success("Tous les mouvements ont été effacés.")
                st.cache_data.clear()
                st.rerun()
    with col_a2:
        if st.button("🗑️ RÉINITIALISER LA BASE CLIENTS"):
            if st.checkbox("Confirmer la purge des clients"):
                delete_all(T_CLIENT)
                st.success("La base clients a été réinitialisée.")
                st.cache_data.clear()
                st.rerun()
