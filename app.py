import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

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

# --- CONFIGURATION SUPABASE CLIENT ---
SUPABASE_URL = st.secrets.get("https://pwsxxmmlscvazaictocg.supabase.co/rest/v1/", "")
SUPABASE_KEY = st.secrets.get("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB3c3h4bW1sc2N2YXphaWN0b2NnIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2ODk2MzUsImV4cCI6MjA5NzI2NTYzNX0.Dhg-fnZ_OMkk59e9w58X6DzZRr-Y3nd8PBq_cc9SH48", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("⚠️ Les identifiants Supabase ne sont pas configurés dans `st.secrets`.")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- FONCTIONS DE GESTION CRUD SUPABASE ---
def get_all(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        return pd.DataFrame()

def insert_row(table_name, data):
    try:
        supabase.table(table_name).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur d'insertion : {e}")
        return False

def upsert_row(table_name, data):
    try:
        supabase.table(table_name).upsert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur d'enregistrement : {e}")
        return False

def update_row(table_name, data, match_dict):
    try:
        supabase.table(table_name).update(data).match(match_dict).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de mise à jour : {e}")
        return False

def delete_row(table_name, match_dict):
    try:
        supabase.table(table_name).delete().match(match_dict).execute()
        return True
    except Exception as e:
        st.error(f"Erreur de suppression : {e}")
        return False

def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception as e:
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

# Chargement synchrone des listes depuis le Cloud
df_voitures = get_all("stock")
df_c_list = get_all("clients")
df_vidanges_all = get_all("vidanges")

liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row['Nom']).upper()} {str(row['Prénom'])} (CIN: {row['CIN']})" for _, row in df_c_list.iterrows()] if not df_c_list.empty else ["-- Entrée manuelle --"]
liste_vehicules_opt = [f"{str(row['Matricule']).strip()}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule']) and str(row['Matricule']).strip().lower() != 'nan'] if not df_voitures.empty else []
liste_vehicules_complets_opt = [f"{str(row['Matricule']).strip()} — {str(row.get('Modèle', row.get('Marque', 'Voiture')))}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule'])] if not df_voitures.empty else []

# Auto-alimentation de la table des vidanges cloud
if not df_voitures.empty:
    for _, car in df_voitures.iterrows():
        mat = str(car.get('Matricule', '')).strip()
        marq = str(car.get('Marque', '')).upper()
        if mat and mat.lower() != 'nan':
            exists = False
            if not df_vidanges_all.empty:
                exists = mat in df_vidanges_all['Matricule'].values
            if not exists:
                upsert_row("vidanges", {
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
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo_path, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #e60000; font-weight:800; margin-bottom:0;'>BBNH</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.5; font-size:13px; letter-spacing:4px; margin-bottom:25px;'>RENT A CAR</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-bottom:10px;'>🕹️ CONSOLE D'ACTION :</h3>", unsafe_allow_html=True)
    menu_action = st.radio("", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat / Réservation", 
        "🚗 Ajouter un Véhicule à la Flotte",
        "🗑️ Supprimer un Véhicule de la Flotte",
        "⚙️ Modifier un Dossier (Contrat/Réservation)",
        "❌ Supprimer une opération"
    ], label_visibility="collapsed")

# Chargement global des mouvements
df_mouvs = get_all("mouvements")

# --- PROCESSUS DES FORMULAIRES DE LA SIDEBAR ---
if menu_action == "📝 Nouveau Contrat / Réservation":
    st.sidebar.markdown("### 📝 Éditer une nouvelle fiche")
    nature = st.sidebar.selectbox("Nature :", ["Contrat Location", "Réservation", "Maintenance / Garage"])
    vehicule = st.sidebar.selectbox("Véhicule :", liste_vehicules_opt)
    client_b = st.sidebar.selectbox("Client :", liste_clients_opt)
    
    nom_m = st.sidebar.text_input("Nom & Prénom (Manuel) :")
    cin_m = st.sidebar.text_input("N° C.I.N (Manuel) :")
    dc_m = st.sidebar.date_input("Date Délivrance CIN :", datetime.now() - timedelta(days=365))
    permis_m = st.sidebar.text_input("N° Permis (Manuel) :")
    dp_m = st.sidebar.date_input("Date Délivrance Permis :", datetime.now() - timedelta(days=365))
    
    f_cin = st.sidebar.file_uploader("Fichier CIN (Image) :", type=["png", "jpg", "jpeg"])
    f_permis = st.sidebar.file_uploader("Fichier Permis (Image) :", type=["png", "jpg", "jpeg"])
    
    st.sidebar.markdown("---")
    d1 = st.sidebar.date_input("Date Réception / Début :", datetime.now())
    t1 = st.sidebar.time_input("Heure Réception :", time(9, 0))
    d2 = st.sidebar.date_input("Date Fin / Retour :", datetime.now() + timedelta(days=2))
    t2 = st.sidebar.time_input("Heure Fin :", time(12, 0))
    
    nbr_jours = max(1, (d2 - d1).days)
    st.sidebar.markdown(f"**🔢 Durée estimée :** `{nbr_jours} jour(s)`")
    prix_unitaire = st.sidebar.number_input("💰 Prix Unitaire / Jour (DT) :", min_value=0, value=100, step=5)
    
    total_auto = nbr_jours * prix_unitaire
    montant_total = st.sidebar.number_input("💵 Montant Total (DT) :", min_value=0, value=int(total_auto))
    caution = st.sidebar.number_input("🛡️ Caution Déposée (DT) :", value=0)
    reste = montant_total - caution
    st.sidebar.markdown(f"**🔴 Reste à payer :** `{reste} DT`")
    
    km_debut = st.sidebar.number_input("Kilométrage au Départ :", min_value=0, value=0, step=1)
    l_reception = st.sidebar.text_input("Lieu de réception :", value="Siège Monastir")
    no_vol = st.sidebar.text_input("N° de vol :", value="")
    info_note = st.sidebar.text_area("Note complémentaire :")
    ref = st.sidebar.text_input("Code Contrat unique :", f"BBNH-{datetime.now().strftime('%d%H%S')}")
    
    if st.sidebar.button("⚡ ENREGISTRER SUR SUPABASE"):
        nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN:")[0]
        cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "")
        str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
        str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
        text_type = "Location" if "Contrat" in nature else nature
        
        img_cin_b64 = encoder_image_base64(f_cin)
        img_permis_b64 = encoder_image_base64(f_permis)
        
        if client_b == "-- Entrée manuelle --":
            upsert_row("clients", {
                "Nom": nom_f, "CIN": cin_f, "Date Délivrance CIN": dc_m.strftime("%Y-%m-%d"),
                "N° Permis": permis_m, "Date Délivrance Permis": dp_m.strftime("%Y-%m-%d"),
                "Image CIN": img_cin_b64, "Image Permis": img_permis_b64
            })
        
        if "Contrat" in nature:
            insert_row("contrats", {
                "Num_Contrat": ref, "Matricule": vehicule, "Client_Nom": nom_f, "CIN_Client": cin_f,
                "Date_Debut": str_d1, "Heure_Debut": str_t1, "Date_Fin": str_d2, "Heure_Fin": str_t2,
                "Tarif_Jour": str(prix_unitaire), "Montant_Total": str(montant_total), "Statut_Contrat": "Actif"
            })
        
        insert_row("mouvements", {
            "Matricule": vehicule, "Type_Statut": text_type, "Date_Debut": str_d1, "Heure_Debut": str_t1,
            "Date_Fin": str_d2, "Heure_Fin": str_t2, "Client": nom_f, "Prix": str(montant_total),
            "Statut_Mouvement": "En cours", "Caution": str(caution), "Reste": str(reste),
            "Lieu_Reception": l_reception, "No_Vol": no_vol, "Info_Note": info_note, "KM_Debut": int(km_debut), "KM_Fin": 0
        })
        
        update_row("vidanges", {"KM_Recent": int(km_debut), "Date_Mise_A_Jour": str_d1}, {"Matricule": vehicule})
        st.success("Fiche synchronisée avec succès dans le Cloud !")
        st.rerun()

elif menu_action == "🚗 Ajouter un Véhicule à la Flotte":
    with st.sidebar.form("form_add_car_supabase"):
        st.markdown("### 🚗 Nouveau Véhicule Cloud")
        nouveau_matricule = st.text_input("Matricule / Plaque * :").strip()
        nouvelle_marque = st.text_input("Marque * :").strip()
        nouveau_modele = st.text_input("Modèle * :").strip()
        nouvelle_annee = st.text_input("Année :", value="2026").strip()
        
        if st.form_submit_button("⚡ ENREGISTRER LE VÉHICULE"):
            if nouveau_matricule and nouvelle_marque and nouveau_modele:
                combinaison_modele = f"{nouvelle_marque} {nouveau_modele}"
                upsert_row("stock", {
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque,
                    "Modèle": nouveau_modele, "Année": nouvelle_annee, "Marque/Model": combinaison_modele
                })
                upsert_row("vidanges", {
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque.upper(),
                    "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                    "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                    "KM_Dernier_Vidange": 0, "KM_Recent": 0
                })
                st.success("Véhicule inséré dans la flotte global !")
                st.rerun()

elif menu_action == "🗑️ Supprimer un Véhicule de la Flotte":
    if liste_vehicules_complets_opt:
        with st.sidebar.form("form_delete_car_cloud"):
            vehicule_a_retirer = st.selectbox("Choisir le véhicule à supprimer :", liste_vehicules_complets_opt)
            confirmer_suppression = st.checkbox("Confirmer la suppression définitive")
            if st.form_submit_button("💥 SUPPRIMER LE VÉHICULE"):
                if confirmer_suppression:
                    matricule_pure = str(vehicule_a_retirer).split(" — ")[0].strip()
                    delete_row("stock", {"Matricule": matricule_pure})
                    delete_row("vidanges", {"Matricule": matricule_pure})
                    st.success("Véhicule supprimé de la base Supabase.")
                    st.rerun()

elif menu_action == "⚙️ Modifier un Dossier (Contrat/Réservation)":
    if not df_mouvs.empty:
        df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        if not df_mouv_actifs.empty:
            liste_mouv_mod = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouv_actifs.iterrows()]
            mouv_selectionne = st.sidebar.selectbox("Sélectionner le dossier à éditer :", liste_mouv_mod)
            id_to_edit = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
            row_init = df_mouv_actifs[df_mouv_actifs['ID'] == id_to_edit].iloc[0]
            
            df_cli_spec = df_c_list[df_c_list['Nom'] == str(row_init['Client'])] if not df_c_list.empty else pd.DataFrame()
            row_cli_init = df_cli_spec.iloc[0] if not df_cli_spec.empty else {}
            
            try: init_date_deb = datetime.strptime(str(row_init['Date_Debut']), "%Y-%m-%d").date()
            except: init_date_deb = datetime.now().date()
            try: init_date_fin = datetime.strptime(str(row_init['Date_Fin']), "%Y-%m-%d").date()
            except: init_date_fin = datetime.now().date()
            
            st.sidebar.markdown(f"### ⚙️ Édition Totale du Dossier #{id_to_edit}")
            mod_nature = st.sidebar.selectbox("Changer de Nature :", ["Location", "Réservation", "Maintenance / Garage"])
            mod_client = st.sidebar.text_input("Nom & Prénom du Conducteur :", value=str(row_init['Client']))
            mod_cin = st.sidebar.text_input("N° CIN :", value=str(row_cli_init.get('CIN', '')))
            
            mod_d1 = st.sidebar.date_input("Date Début :", init_date_deb)
            mod_d2 = st.sidebar.date_input("Date Fin :", init_date_fin)
            mod_prix = st.sidebar.number_input("Prix Total Évalué (DT) :", value=int(float(row_init.get('Prix', 0))))
            mod_caution = st.sidebar.number_input("Caution (DT) :", value=int(float(row_init.get('Caution', 0))))
            mod_reste = mod_prix - mod_caution
            
            if st.sidebar.button("💾 ENREGISTRER ABSOLUMENT TOUT DANS LE CLOUD"):
                update_row("mouvements", {
                    "Client": mod_client, "Date_Debut": mod_d1.strftime("%Y-%m-%d"),
                    "Date_Fin": mod_d2.strftime("%Y-%m-%d"), "Prix": str(mod_prix),
                    "Caution": str(mod_caution), "Reste": str(mod_reste)
                }, {"ID": id_to_edit})
                st.success("Dossier mis à jour globalement sur Supabase !")
                st.rerun()

elif menu_action == "❌ Supprimer une opération":
    if not df_mouvs.empty:
        df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        if not df_mouv_actifs.empty:
            liste_mouv_del = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouv_actifs.iterrows()]
            with st.sidebar.form("form_delete_mouv_cloud"):
                mouv_selectionne = st.selectbox("Choisir l'opération à détruire :", liste_mouv_del)
                confirmer_action = st.checkbox("Confirmer la suppression")
                if st.form_submit_button("💥 RETIRER DE SUPABASE"):
                    if confirmer_action:
                        id_to_delete = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
                        delete_row("mouvements", {"ID": id_to_delete})
                        st.success("Opération effacée de la base globale !")
                        st.rerun()

# =========================================================================
# ESPACE CENTRAL DE TRAVAIL INTERACTIF
# =========================================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION (SUPABASE CLOUD)</h1>", unsafe_allow_html=True)

# --- RECHERCHE AVANCÉE PAR PÉRIODE ---
with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    with c_search1: search_date_debut = st.date_input("📅 Date de Sortie souhaitée :", datetime.now(), key="adv_search_start")
    with c_search2: search_date_fin = st.date_input("📅 Date de Retour prévue :", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)
        
    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")
        if search_date_debut > search_date_fin:
            st.error("⚠️ La date de sortie ne peut pas être supérieure à la date de retour.")
        else:
            if not df_mouvs.empty:
                df_occupes = df_mouvs[(df_mouvs['Statut_Mouvement'] == 'En cours') & (df_mouvs['Date_Debut'] <= str_s_end) & (df_mouvs['Date_Fin'] >= str_s_start)]
                mats_occupes = df_occupes['Matricule'].unique()
            else:
                mats_occupes = []
                
            df_disponibles = df_voitures[~df_voitures['Matricule'].isin(mats_occupes)] if not df_voitures.empty else pd.DataFrame()
            
            if not df_disponibles.empty:
                st.markdown(f"##### 🚗 {len(df_disponibles)} Véhicule(s) disponible(s) :")
                st.dataframe(df_disponibles[['Matricule', 'Marque', 'Modèle', 'Année']], use_container_width=True, hide_index=True)
            else:
                st.warning("❌ Aucun véhicule n'est disponible dans la flotte BBNH sur cette période.")

# --- INTERFACE DES ONGLETS CONTENUS ---
tab_planning, tab_contrats, tab_logistique, tab_analytics, tab_vidange, tab_crm, tab_admin = st.tabs([
    "🗓️ CORE PLANNING", "📄 LISTE DE CONTRATS", "🔑 BOX RECEPTION RETOURS", 
    "📊 SUIVI DES PERFORMANCES", "🔧 SUIVI DES VIDANGES", "👥 COMPTE CONDUCTEURS (CRM)", "⚙️ PANNEAU CONFIG"
])

# --- TAB 1 : PLANNING ---
with tab_planning:
    st.markdown("### 🗓️ Vue Grille des Disponibilités (30 Jours)")
    options_recherche_voiture = ["-- Toutes les voitures --"] + liste_vehicules_opt
    vehicule_recherche = st.selectbox("🚘 Filtrer par véhicule :", options_recherche_voiture)
    
    date_base = st.date_input("Date initiale de la grille :", datetime.now().date())
    array_jours = [date_base + timedelta(days=i) for i in range(30)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    
    build_matrix = []
    if not df_voitures.empty:
        for _, car in df_voitures.iterrows():
            immat = str(car.get('Matricule', '')).strip()
            if vehicule_recherche != "-- Toutes les voitures --" and immat != vehicule_recherche:
                continue
            ligne = {"Flotte BBNH": f"🚘 {car.get('Modèle', 'Voiture')} — [{immat}]"}
            for col_j in nom_colonnes:
                ligne[col_j] = "● Disponible"
                
            if not df_mouvs.empty:
                df_mv_car = df_mouvs[(df_mouvs['Matricule'] == immat) & (df_mouvs['Statut_Mouvement'] == 'En cours')]
                for _, mv in df_mv_car.iterrows():
                    try:
                        sd = datetime.strptime(str(mv['Date_Debut']), "%Y-%m-%d").date()
                        ed = datetime.strptime(str(mv['Date_Fin']), "%Y-%m-%d").date()
                        curr = sd
                        while curr <= ed:
                            col_name = curr.strftime("%d/%m")
                            if col_name in ligne:
                                ligne[col_name] = f"🔴 {mv['Client']}"
                            curr += timedelta(days=1)
                    except: pass
            build_matrix.append(ligne)
            
        st.dataframe(pd.DataFrame(build_matrix), use_container_width=True, hide_index=True)

# --- TAB 2 : CONTRATS ---
with tab_contrats:
    st.markdown("### 📄 Liste Globale des Contrats")
    if not df_mouvs.empty:
        html_table = '<table class="contract-table"><thead><tr><th>ID</th><th>Véhicule</th><th>Client</th><th>Période</th><th>Montant</th><th>Statut</th></tr></thead><tbody>'
        for _, r in df_mouvs.iterrows():
            badge = "status-paid" if r.get('Statut_Mouvement') == 'Clôturé' else "status-pending"
            html_table += f"""<tr>
                <td class="contract-num">#{r.get('ID')}</td>
                <td><b>{r.get('Matricule')}</b></td>
                <td>{r.get('Client')}</td>
                <td>Du {r.get('Date_Debut')} au {r.get('Date_Fin')}</td>
                <td><strong style='color:#e60000;'>{r.get('Prix')} DT</strong></td>
                <td><span class="status-badge {badge}">{r.get('Statut_Mouvement')}</span></td>
            </tr>"""
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)

# --- TAB 3 : RECEPTION RETOURS ---
with tab_logistique:
    st.markdown("### 🔑 Box Réception & Clôture de Retour")
    if not df_mouvs.empty:
        df_encours = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        if not df_encours.empty:
            liste_retours = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_encours.iterrows()]
            mouv_retour = st.selectbox("Véhicule à réceptionner :", liste_retours)
            id_retour = int(mouv_retour.split(" | ")[0].replace("ID: ", "").strip())
            row_ret = df_encours[df_encours['ID'] == id_retour].iloc[0]
            
            with st.form("form_cloture_cloud"):
                km_retour = st.number_input("Kilométrage Retour :", min_value=int(row_ret.get('KM_Debut', 0)), value=int(row_ret.get('KM_Debut', 0))+100)
                if st.form_submit_button("🏁 VALIDER LE RETOUR ET CONCHLURE"):
                    update_row("mouvements", {"Statut_Mouvement": "Clôturé", "KM_Fin": int(km_retour)}, {"ID": id_retour})
                    update_row("vidanges", {"KM_Recent": int(km_retour), "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")}, {"Matricule": str(row_ret['Matricule']).strip()})
                    st.success("Dossier archivé et clôturé avec succès !")
                    st.rerun()

# --- TAB 4 : ANALYTICS ---
with tab_analytics:
    st.markdown("### 📊 Chiffres Clés")
    if not df_mouvs.empty:
        df_mouvs['Prix_N'] = pd.to_numeric(df_mouvs['Prix'], errors='coerce').fillna(0)
        ca = df_mouvs['Prix_N'].sum()
        st.metric("Chiffre d'Affaires Global (Cloud)", f"{ca:,.2f} DT")
        st.bar_chart(df_mouvs.groupby('Matricule')['Prix_N'].sum())

# --- TAB 5 : VIDANGES ---
with tab_vidange:
    st.markdown("### 🔧 État Technique des Moteurs")
    if not df_vidanges_all.empty:
        html_v = '<table class="contract-table"><thead><tr><th>Matricule</th><th>Marque</th><th>Dernière Vidange</th><th>Actuel</th><th>Statut</th></tr></thead><tbody>'
        for _, r in df_vidanges_all.iterrows():
            diff = int(r.get('KM_Recent', 0)) - int(r.get('KM_Dernier_Vidange', 0))
            restant = 10000 - diff
            lbl = "km-green" if restant > 2000 else "km-red"
            html_v += f"""<tr>
                <td><b>{r.get('Matricule')}</b></td>
                <td>{r.get('Marque')}</td>
                <td>{r.get('KM_Dernier_Vidange')} KM</td>
                <td>{r.get('KM_Recent')} KM</td>
                <td><div class="km-indicator {lbl}">{restant} KM Restants</div></td>
            </tr>"""
        html_v += "</tbody></table>"
        st.markdown(html_v, unsafe_allow_html=True)

# --- TAB 6 : CRM CONDUCTEURS ---
with tab_crm:
    st.markdown("### 👥 CRM Conducteurs Premium")
    if not df_c_list.empty:
        for _, cli in df_c_list.iterrows():
            with st.expander(f"👤 {str(cli.get('Nom')).upper()} - CIN: {cli.get('CIN')}"):
                st.write(f"📞 Téléphone : {cli.get('Numéro de téléphone', 'N/A')}")
                st.write(f"🪪 N° Permis : {cli.get('N° Permis', 'N/A')}")
                if cli.get('Image CIN'):
                    try: st.image(base64.b64decode(cli['Image CIN']), width=300)
                    except: pass

# --- TAB 7 : CONFIGURATION ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Panneau de Purge")
    st.warning("Action destructive directe sur Supabase Cloud.")
    if st.button("🗑️ PURGER LES MOUVEMENTS"):
        supabase.table("mouvements").delete().neq("ID", 0).execute()
        st.success("Toutes les lignes de mouvements ont été purgées !")
        st.rerun()
