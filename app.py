import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
import base64
from datetime import datetime, timedelta, time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Compatibilité Streamlit (rerun) ---
if hasattr(st, "rerun"):
    rerun = st.rerun
elif hasattr(st, "experimental_rerun"):
    rerun = st.experimental_rerun
else:
    def rerun(): pass

# --- Compatibilité pandas (style.map vs applymap) ---
def style_apply(df_style, func, **kwargs):
    try:
        return df_style.map(func, **kwargs)
    except AttributeError:
        return df_style.applymap(func, **kwargs)

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="BBNH OS — Gestion Premium",
    layout="wide",
    page_icon="🏎️",
    initial_sidebar_state="expanded"
)

# --- STYLE CSS ---
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
    background: #ffffff; padding: 16px; border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
    margin-bottom: 25px; display: flex; justify-content: center; align-items: center;
}
.stTabs [data-baseweb="tab-list"] {
    gap: 8px; background-color: #161920; padding: 6px;
    border-radius: 14px; border: 1px solid #222733; margin-bottom: 25px;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 20px; border-radius: 10px; font-weight: 600;
    color: #9ca3af; transition: all 0.2s ease; border: none !important;
}
.stTabs [data-baseweb="tab"]:hover { background-color: #222733; color: #ffffff; }
.stTabs [aria-selected="true"] {
    background-color: #e60000 !important; color: #ffffff !important;
    box-shadow: 0 4px 15px rgba(230, 0, 0, 0.4);
}
h1 { font-weight: 800 !important; letter-spacing: -1px !important; color: #ffffff !important; }
h3 { color: #f3f4f6; font-weight: 700 !important; letter-spacing: -0.5px; }
div[data-testid="stForm"] {
    background: rgba(22, 25, 32, 0.8) !important;
    border: 1px solid #2a3142 !important; padding: 25px !important;
    border-radius: 16px !important;
}
div.stButton > button {
    background: linear-gradient(135deg, #e60000 0%, #b30000 100%) !important;
    color: white !important; border: none !important; border-radius: 10px !important;
    padding: 14px 28px !important; font-weight: 700 !important;
    font-size: 14px !important; transition: all 0.2s ease;
}
div.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 15px rgba(230, 0, 0, 0.5);
}
.contract-table {
    width: 100%; border-collapse: collapse; background-color: #ffffff;
    color: #333333; border-radius: 8px; overflow: hidden; font-size: 13px;
}
.contract-table th {
    background-color: #f8f9fa; color: #666; font-weight: 600;
    text-align: center; padding: 12px 8px; border-bottom: 1px solid #eee;
}
.contract-table td {
    padding: 12px 8px; border-bottom: 1px solid #eee;
    text-align: center; vertical-align: middle;
}
.car-info { display: flex; flex-direction: column; align-items: center; }
.car-image { width: 80px; height: auto; margin-bottom: 5px; }
.car-plate { font-weight: bold; color: #333; }
.contract-num { font-weight: 800; font-size: 16px; }
.status-badge {
    padding: 4px 10px; border-radius: 20px; font-weight: bold;
    font-size: 11px; text-transform: uppercase;
}
.status-paid { background-color: #e6f7ed; color: #28a745; border: 1px solid #28a745; }
.status-pending { background-color: #fff4e6; color: #fd7e14; border: 1px solid #fd7e14; }
.status-reservation { background-color: #e0e7ff; color: #4f46e5; border: 1px solid #4f46e5; }
.status-contrat { background-color: #dcfce7; color: #166534; border: 1px solid #166534; }
.km-box { display: flex; flex-direction: column; gap: 2px; align-items: center; }
.km-value { font-weight: bold; margin-bottom: 2px; }
.km-indicator {
    width: 80px; padding: 2px 4px; color: white;
    font-size: 10px; font-weight: bold; border-radius: 3px;
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
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception as e:
        st.error(f"❌ Erreur connexion Supabase : {e}")
        return None

supabase = init_supabase()

if supabase is None:
    st.error("🔴 **Connexion Supabase impossible**")
    st.markdown("""
    ### 📋 Configuration requise
    Créez un fichier `.streamlit/secrets.toml` avec :
    ```toml
    SUPABASE_URL = "https://VOTRE_PROJET.supabase.co"
    SUPABASE_KEY = "votre_cle_anon_ou_service_role"
    ```
    """)
    st.stop()

# Noms des tables
T_CLIENT = "client"
T_VEHICULE = "vehicule"
T_MOUVEMENT = "mouvement"
T_VIDANGE = "vidange"
T_CONTRAT = "carbbnh"

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================
def safe_str(val, default=""):
    if val is None:
        return default
    if isinstance(val, float) and pd.isna(val):
        return default
    s = str(val).strip()
    if s.lower() in ('nan', 'none', ''):
        return default
    return s

def safe_int(val, default=0):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        s = str(val).replace(' ', '').replace(',', '.')
        return int(float(s))
    except Exception:
        return default

def safe_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        s = str(val).replace(' ', '').replace(',', '.')
        return float(s)
    except Exception:
        return default

def safe_id(val, default=-1):
    try:
        if val is None:
            return default
        if isinstance(val, float) and pd.isna(val):
            return default
        return int(float(str(val)))
    except Exception:
        return default

def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception:
        return ""

def formater_heure_propre(valeur):
    if valeur is None or (isinstance(valeur, float) and pd.isna(valeur)):
        return '00:00'
    if isinstance(valeur, (datetime, time)):
        return valeur.strftime('%H:%M')
    val_str = safe_str(valeur, '00:00')
    if " " in val_str:
        try:
            val_str = val_str.split(" ")[1]
        except Exception:
            pass
    parts = val_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return '00:00'

def parse_date(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date() if hasattr(val, 'date') else val
    if hasattr(val, 'date') and callable(val.date):
        try:
            return val.date()
        except Exception:
            pass
    s = safe_str(val)
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).date()
        except Exception:
            pass
    try:
        return pd.to_datetime(s).date()
    except Exception:
        return None

def parse_client_label(label):
    try:
        if not label or label == "-- Entrée manuelle --":
            return "", ""
        if " (CIN: " in label:
            parts = label.split(" (CIN: ")
            nom_prenom = parts[0].strip()
            cin = parts[1].replace(")", "").strip()
            return nom_prenom, cin
        return label.strip(), ""
    except Exception:
        return safe_str(label), ""

def normaliser_type(val):
    """Normalise un type de statut pour comparaison tolérante"""
    try:
        s = str(val).strip().lower()
        s = s.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        return s
    except Exception:
        return ""

def est_une_reservation(type_statut):
    """Détecte si un type de statut est une réservation (tolérant)"""
    norm = normaliser_type(type_statut)
    return 'reserv' in norm or 'resa' in norm or 'booking' in norm

# ============================================================
# ⚡ FONCTIONS DATABASE OPTIMISÉES
# ============================================================
@st.cache_data(ttl=600, show_spinner=False)
def get_all_tables():
    """⚡ Charge TOUTES les tables en PARALLÈLE"""
    tables = [T_VEHICULE, T_CLIENT, T_MOUVEMENT, T_VIDANGE, T_CONTRAT]
    results = {}

    def fetch(table_name):
        try:
            response = supabase.table(table_name).select("*").execute()
            return table_name, pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception:
            return table_name, pd.DataFrame()

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(fetch, t): t for t in tables}
        for future in as_completed(futures):
            table_name, df = future.result()
            results[table_name] = df
    return results

def get_all(table_name):
    all_data = get_all_tables()
    return all_data.get(table_name, pd.DataFrame())

def insert_row(table_name, data_dict):
    try:
        clean_data = {k: v for k, v in data_dict.items()
                     if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).insert(clean_data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur insert ({table_name}): {e}")
        return False

def update_row(table_name, data_dict, column, value):
    try:
        clean_data = {k: v for k, v in data_dict.items()
                     if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).update(clean_data).eq(column, value).execute()
        return True
    except Exception as e:
        st.error(f"Erreur update ({table_name}): {e}")
        return False

def delete_row(table_name, column, value):
    try:
        supabase.table(table_name).delete().eq(column, value).execute()
        return True
    except Exception as e:
        st.error(f"Erreur delete ({table_name}): {e}")
        return False

def delete_all(table_name):
    try:
        try:
            supabase.table(table_name).delete().neq("id", 0).execute()
        except Exception:
            try:
                supabase.table(table_name).delete().gte("id", 0).execute()
            except Exception:
                df = get_all(table_name)
                if not df.empty and 'id' in df.columns:
                    for id_val in df['id'].tolist():
                        try:
                            supabase.table(table_name).delete().eq("id", id_val).execute()
                        except Exception:
                            pass
        return True
    except Exception as e:
        st.error(f"Erreur delete all ({table_name}): {e}")
        return False

def upsert_vidange(matricule, marque, km_recent=0):
    try:
        response = supabase.table(T_VIDANGE).select("Matricule").eq("Matricule", matricule).execute()
        if response.data and len(response.data) > 0:
            supabase.table(T_VIDANGE).update({
                "KM_Recent": int(km_recent),
                "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")
            }).eq("Matricule", matricule).execute()
        else:
            supabase.table(T_VIDANGE).insert({
                "Matricule": matricule,
                "Marque": safe_str(marque).upper(),
                "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                "KM_Dernier_Vidange": 0,
                "KM_Recent": int(km_recent)
            }).execute()
        return True
    except Exception as e:
        st.warning(f"Upsert vidange échoué: {e}")
        return False

# ============================================================
# 🆕 FONCTION AMÉLIORÉE : TRANSFORMER RÉSERVATION EN CONTRAT
# ============================================================
def transformer_reservation_en_contrat(id_mouvement):
    """Transforme un mouvement (réservation) en contrat location - Version améliorée"""
    try:
        all_data = get_all_tables()
        df_mouvs = all_data[T_MOUVEMENT]
        df_clients = all_data[T_CLIENT]
        
        if df_mouvs.empty or 'id' not in df_mouvs.columns:
            return False, "Aucun mouvement trouvé dans la base"
        
        # Trouver le mouvement
        row_matches = df_mouvs[df_mouvs['id'].apply(lambda x: safe_id(x)) == id_mouvement]
        if row_matches.empty:
            return False, f"Mouvement ID {id_mouvement} introuvable"
        
        row = row_matches.iloc[0]
        
        # Vérifier que c'est bien une réservation
        type_statut = safe_str(row.get('Type_Statut', ''))
        if not est_une_reservation(type_statut):
            return False, f"Ce mouvement n'est pas une réservation (type: {type_statut})"
        
        # 1. CRÉER D'ABORD le contrat dans la table carbbnh
        ref_contrat = f"BBNH-{datetime.now().strftime('%d%m%H%M')}-{id_mouvement}"
        
        # Récupérer le CIN du client automatiquement
        cin_client = ""
        client_nom = safe_str(row.get('Client', ''))
        if not df_clients.empty and client_nom and 'Nom' in df_clients.columns:
            match_cli = df_clients[df_clients['Nom'].astype(str).str.strip() == client_nom.strip()]
            if not match_cli.empty:
                cin_client = safe_str(match_cli.iloc[0].get('CIN', ''))
        
        # Calculer le tarif journalier
        prix_total = safe_float(row.get('Prix', 0))
        d_deb = parse_date(row.get('Date_Debut'))
        d_fin = parse_date(row.get('Date_Fin'))
        nb_jours = max(1, (d_fin - d_deb).days) if d_deb and d_fin else 1
        tarif_jour = prix_total / nb_jours if prix_total > 0 else 0
        
        ok_contrat = insert_row(T_CONTRAT, {
            "Num_Contrat": ref_contrat,
            "Matricule": safe_str(row.get('Matricule', '')),
            "Client_Nom": client_nom,
            "CIN_Client": cin_client,
            "Date_Debut": safe_str(row.get('Date_Debut', '')),
            "Heure_Debut": safe_str(row.get('Heure_Debut', '')),
            "Date_Fin": safe_str(row.get('Date_Fin', '')),
            "Heure_Fin": safe_str(row.get('Heure_Fin', '')),
            "Tarif_Jour": str(tarif_jour),
            "Montant_Total": str(prix_total),
            "Statut_Contrat": "Actif"
        })
        
        if not ok_contrat:
            return False, "❌ Échec de création du contrat. Transformation annulée."
        
        # 2. ENSUITE mettre à jour le mouvement : Réservation → Location
        ok_update = update_row(T_MOUVEMENT, {
            "Type_Statut": "Location"
        }, "id", int(id_mouvement))
        
        if not ok_update:
            # Rollback : supprimer le contrat créé
            delete_row(T_CONTRAT, "Num_Contrat", ref_contrat)
            return False, "❌ Échec de mise à jour du mouvement. Contrat supprimé."
        
        return True, f"✅ Transformé en contrat **{ref_contrat}**"
        
    except Exception as e:
        return False, f"❌ Erreur système : {str(e)}"

# ============================================================
# ⚡ CHARGEMENT DES DONNÉES
# ============================================================
all_data = get_all_tables()
df_voitures = all_data[T_VEHICULE]
df_clients  = all_data[T_CLIENT]
df_mouvs    = all_data[T_MOUVEMENT]
df_vidanges = all_data[T_VIDANGE]
df_contrats = all_data[T_CONTRAT]

# Listes pour selectbox
def build_liste_clients():
    opts = ["-- Entrée manuelle --"]
    if not df_clients.empty and 'Nom' in df_clients.columns:
        for _, row in df_clients.iterrows():
            nom = safe_str(row.get('Nom', ''))
            prenom = safe_str(row.get('Prénom', ''))
            cin = safe_str(row.get('CIN', ''))
            if nom:
                opts.append(f"{nom.upper()} {prenom} (CIN: {cin})")
    return opts

def build_liste_vehicules():
    if df_voitures.empty or 'Matricule' not in df_voitures.columns:
        return []
    return [safe_str(r.get('Matricule')) for _, r in df_voitures.iterrows() if safe_str(r.get('Matricule'))]

def build_liste_vehicules_complets():
    if df_voitures.empty or 'Matricule' not in df_voitures.columns:
        return []
    res = []
    for _, r in df_voitures.iterrows():
        mat = safe_str(r.get('Matricule'))
        modele = safe_str(r.get('Modèle', r.get('Marque', 'Voiture')))
        if mat:
            res.append(f"{mat} — {modele}")
    return res

liste_clients_opt = build_liste_clients()
liste_vehicules_opt = build_liste_vehicules()
liste_vehicules_complets_opt = build_liste_vehicules_complets()

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
        "❌ Supprimer une opération",
        "🔄 Transformer Réservation → Contrat"
    ], label_visibility="collapsed")

    st.markdown("<br><hr>", unsafe_allow_html=True)

# ============================================================
# FORMULAIRES SIDEBAR
# ============================================================

# --- 📝 NOUVEAU CONTRAT ---
if menu_action == "📝 Nouveau Contrat / Réservation":
    st.sidebar.markdown("### 📝 Éditer une nouvelle fiche")
    nature = st.sidebar.selectbox("Nature : ", ["Contrat Location", "Réservation", "Maintenance / Garage"])

    if liste_vehicules_opt:
        vehicule = st.sidebar.selectbox("Véhicule : ", liste_vehicules_opt)
    else:
        vehicule = st.sidebar.text_input("Véhicule (matricule) : ")

    client_b = st.sidebar.selectbox("Client : ", liste_clients_opt)

    nom_m = st.sidebar.text_input("Nom & Prénom (Manuel) : ")
    cin_m = st.sidebar.text_input("N° C.I.N (Manuel) : ")
    dc_m = st.sidebar.date_input("Date Délivrance CIN : ", datetime.now() - timedelta(days=365))
    permis_m = st.sidebar.text_input("N° Permis (Manuel) : ")
    dp_m = st.sidebar.date_input("Date Délivrance Permis : ", datetime.now() - timedelta(days=365))

    f_cin = st.sidebar.file_uploader("Fichier CIN (Image) : ", type=["png", "jpg", "jpeg"])
    f_permis = st.sidebar.file_uploader("Fichier Permis (Image) : ", type=["png", "jpg", "jpeg"])

    st.sidebar.markdown("---")
    d1 = st.sidebar.date_input("Date Réception / Début : ", datetime.now())
    t1 = st.sidebar.time_input("Heure Réception : ", time(9, 0))
    d2 = st.sidebar.date_input("Date Fin / Retour : ", datetime.now() + timedelta(days=2))
    t2 = st.sidebar.time_input("Heure Fin : ", time(12, 0))

    nbr_jours = max(1, (d2 - d1).days)
    st.sidebar.markdown(f"**🔢 Durée estimée :** `{nbr_jours} jour(s)`")

    prix_unitaire = st.sidebar.number_input("💰 Prix Unitaire / Jour (DT) : ", min_value=0, value=100, step=5)
    montant_total = st.sidebar.number_input("💵 Montant Total (DT) : ", min_value=0, value=int(nbr_jours * prix_unitaire))
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
        try:
            if client_b == "-- Entrée manuelle --":
                nom_f = nom_m
                cin_f = cin_m
            else:
                nom_f, cin_f = parse_client_label(client_b)
                if nom_m:
                    nom_f = nom_m
                if cin_m:
                    cin_f = cin_m

            if not vehicule or not vehicule.strip():
                st.error("❌ Le véhicule est obligatoire")
            elif not nom_f or not nom_f.strip():
                st.error("❌ Le nom du client est obligatoire")
            else:
                str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
                str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
                text_type = "Location" if "Contrat" in nature else nature

                img_cin_b64 = encoder_image_base64(f_cin)
                img_permis_b64 = encoder_image_base64(f_permis)

                if cin_f and cin_f.strip():
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

                ok_mouv = insert_row(T_MOUVEMENT, {
                    "Matricule": vehicule, "Type_Statut": text_type,
                    "Date_Debut": str_d1, "Heure_Debut": str_t1,
                    "Date_Fin": str_d2, "Heure_Fin": str_t2,
                    "Client": nom_f, "Prix": str(montant_total),
                    "Statut_Mouvement": "En cours", "Caution": str(caution), "Reste": str(reste),
                    "Lieu_Reception": l_reception, "No_Vol": no_vol, "Info_Note": info_note,
                    "KM_Debut": int(km_debut), "KM_Fin": 0
                })

                if ok_mouv:
                    upsert_vidange(vehicule, "", int(km_debut))
                    st.success(f"✅ Fiche créée avec succès ! (Type: **{text_type}**)")
                    if est_une_reservation(text_type):
                        st.info("💡 Vous pouvez transformer cette réservation en contrat via le menu **🔄 Transformer Réservation → Contrat**")
                    get_all_tables.clear()
                    rerun()
                else:
                    st.error("❌ Échec de création du mouvement")
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            traceback.print_exc()

# --- 🚗 AJOUTER VÉHICULE ---
elif menu_action == "🚗 Ajouter un Véhicule à la Flotte":
    with st.sidebar.form("form_bbnh_add_car"):
        st.markdown("### 🚗 Nouveau Véhicule")
        nouveau_matricule = st.text_input("Matricule / Plaque * : ").strip()
        nouvelle_marque = st.text_input("Marque * : ").strip()
        nouveau_modele = st.text_input("Modèle * : ").strip()
        nouvelle_annee = st.text_input("Année : ", value="2026").strip()

        if st.form_submit_button("⚡ ENREGISTRER LE VEHICULE"):
            if nouveau_matricule and nouvelle_marque and nouveau_modele:
                ok_v = insert_row(T_VEHICULE, {
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque,
                    "Modèle": nouveau_modele, "Année": nouvelle_annee,
                    "Marque/Model": f"{nouvelle_marque} {nouveau_modele}"
                })
                if ok_v:
                    upsert_vidange(nouveau_matricule, nouvelle_marque, 0)
                    st.success("✅ Véhicule enregistré !")
                    get_all_tables.clear()
                    rerun()
            else:
                st.error("❌ Tous les champs obligatoires doivent être remplis")

# --- 🗑️ SUPPRIMER VÉHICULE ---
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
                    st.success("✅ Véhicule retiré.")
                    get_all_tables.clear()
                    rerun()
    else:
        st.sidebar.info("Aucun véhicule dans la flotte.")

# --- ⚙️ MODIFIER DOSSIER ---
elif menu_action == "⚙️ Modifier un Dossier (Contrat/Réservation)":
    df_mouv_all = df_mouvs.copy() if not df_mouvs.empty else pd.DataFrame()

    if not df_mouv_all.empty and 'id' in df_mouv_all.columns:
        liste_mouv_mod = []
        id_map = {}
        for idx, r in df_mouv_all.iterrows():
            try:
                raw_id = r.get('id', idx)
                if pd.isna(raw_id):
                    continue
                real_id = safe_id(raw_id)
                if real_id < 0:
                    continue
                mat = safe_str(r.get('Matricule', ''))
                cli = safe_str(r.get('Client', ''))
                statut = safe_str(r.get('Statut_Mouvement', ''))
                type_stat = safe_str(r.get('Type_Statut', ''))
                label = f"ID: {real_id} | {mat} — {cli} [{type_stat} / {statut}]"
                liste_mouv_mod.append(label)
                id_map[label] = real_id
            except Exception:
                continue

        if liste_mouv_mod:
            if "mod_selected_label" not in st.session_state:
                st.session_state["mod_selected_label"] = liste_mouv_mod[0]
            if st.session_state["mod_selected_label"] not in liste_mouv_mod:
                st.session_state["mod_selected_label"] = liste_mouv_mod[0]

            mouv_selectionne = st.sidebar.selectbox(
                "Sélectionner le dossier à éditer :",
                liste_mouv_mod,
                key="mod_selectbox",
                index=liste_mouv_mod.index(st.session_state["mod_selected_label"])
            )
            st.session_state["mod_selected_label"] = mouv_selectionne

            selected_id = id_map.get(mouv_selectionne, -1)
            if selected_id < 0:
                st.sidebar.error("❌ ID invalide")
            else:
                row_matches = df_mouv_all[df_mouv_all['id'].apply(lambda x: safe_id(x)) == selected_id]

                if row_matches.empty:
                    st.sidebar.error(f"❌ Dossier #{selected_id} introuvable")
                else:
                    row_init = row_matches.iloc[0]

                    client_name = safe_str(row_init.get('Client', ''))
                    df_cli_spec = pd.DataFrame()
                    if not df_clients.empty and client_name and 'Nom' in df_clients.columns:
                        df_cli_spec = df_clients[df_clients['Nom'].astype(str).str.strip() == client_name.strip()]
                        if df_cli_spec.empty:
                            df_cli_spec = df_clients[df_clients['Nom'].astype(str).str.contains(client_name, case=False, na=False)]

                    row_cli_init = df_cli_spec.iloc[0].to_dict() if not df_cli_spec.empty else {}

                    init_date_deb = parse_date(row_init.get('Date_Debut')) or datetime.now().date()
                    init_date_fin = parse_date(row_init.get('Date_Fin')) or (datetime.now() + timedelta(days=1)).date()

                    try:
                        init_time_deb = datetime.strptime(formater_heure_propre(row_init.get('Heure_Debut')), "%H:%M").time()
                    except Exception:
                        init_time_deb = time(9, 0)
                    try:
                        init_time_fin = datetime.strptime(formater_heure_propre(row_init.get('Heure_Fin')), "%H:%M").time()
                    except Exception:
                        init_time_fin = time(12, 0)

                    init_date_cin = parse_date(row_cli_init.get('Date Délivrance CIN')) or datetime.now().date()
                    init_date_permis = parse_date(row_cli_init.get('Date Délivrance Permis')) or datetime.now().date()

                    init_nature = safe_str(row_init.get('Type_Statut', 'Location'))
                    init_vehicule = safe_str(row_init.get('Matricule', ''))
                    init_client = safe_str(row_init.get('Client', ''))
                    init_cin = safe_str(row_cli_init.get('CIN', ''))
                    init_permis = safe_str(row_cli_init.get('N° Permis', ''))
                    init_lieu = safe_str(row_init.get('Lieu_Reception', 'Siège Monastir'))
                    init_vol = safe_str(row_init.get('No_Vol', ''))
                    init_note = safe_str(row_init.get('Info_Note', ''))
                    init_km_deb = safe_int(row_init.get('KM_Debut', 0))
                    init_prix = safe_float(row_init.get('Prix', 0))
                    init_caution = safe_float(row_init.get('Caution', 0))

                    nature_options = ["Location", "Réservation", "Maintenance / Garage"]
                    try:
                        idx_nature = nature_options.index(init_nature)
                    except ValueError:
                        idx_nature = 0

                    idx_v_init = 0
                    if init_vehicule and init_vehicule in liste_vehicules_opt:
                        idx_v_init = liste_vehicules_opt.index(init_vehicule)

                    st.sidebar.markdown(f"### ⚙️ Édition Dossier #{selected_id}")

                    mod_nature = st.sidebar.selectbox("Nature : ", nature_options, index=idx_nature, key=f"mod_nature_{selected_id}")
                    mod_vehicule = st.sidebar.selectbox(
                        "Véhicule : ",
                        liste_vehicules_opt if liste_vehicules_opt else [init_vehicule],
                        index=idx_v_init, key=f"mod_veh_{selected_id}"
                    )

                    st.sidebar.markdown("👤 **Informations Conducteur**")
                    mod_client = st.sidebar.text_input("Nom & Prénom : ", value=init_client, key=f"mod_cli_{selected_id}")
                    mod_cin = st.sidebar.text_input("N° CIN : ", value=init_cin, key=f"mod_cin_{selected_id}")
                    mod_date_cin = st.sidebar.date_input("Date Délivrance CIN : ", init_date_cin, key=f"mod_dc_{selected_id}")
                    mod_permis = st.sidebar.text_input("N° Permis : ", value=init_permis, key=f"mod_perm_{selected_id}")
                    mod_date_permis = st.sidebar.date_input("Date Délivrance Permis : ", init_date_permis, key=f"mod_dp_{selected_id}")

                    st.sidebar.markdown("---")
                    c_d1, c_t1 = st.sidebar.columns(2)
                    with c_d1:
                        mod_d1 = st.sidebar.date_input("Date Début : ", init_date_deb, key=f"mod_d1_{selected_id}")
                    with c_t1:
                        mod_t1 = st.sidebar.time_input("Heure Début : ", init_time_deb, key=f"mod_t1_{selected_id}")
                    c_d2, c_t2 = st.sidebar.columns(2)
                    with c_d2:
                        mod_d2 = st.sidebar.date_input("Date Fin : ", init_date_fin, key=f"mod_d2_{selected_id}")
                    with c_t2:
                        mod_t2 = st.sidebar.time_input("Heure Fin : ", init_time_fin, key=f"mod_t2_{selected_id}")

                    mod_nbr_jours = max(1, (mod_d2 - mod_d1).days)
                    st.sidebar.markdown(f"**🔢 Durée :** `{mod_nbr_jours} jour(s)`")

                    init_jours_orig = max(1, (init_date_fin - init_date_deb).days)
                    init_prix_unit_calc = int(init_prix / init_jours_orig) if init_prix > 0 else 100

                    mod_prix_unitaire = st.sidebar.number_input(
                        "💰 Prix / Jour (DT) : ", min_value=0,
                        value=init_prix_unit_calc if init_prix_unit_calc > 0 else 100,
                        key=f"mod_pu_{selected_id}"
                    )
                    mod_prix = st.sidebar.number_input(
                        "Prix Total (DT) : ",
                        value=int(mod_nbr_jours * mod_prix_unitaire),
                        key=f"mod_tot_{selected_id}"
                    )
                    mod_caution = st.sidebar.number_input(
                        "Caution (DT) : ", value=int(init_caution),
                        key=f"mod_cau_{selected_id}"
                    )
                    mod_reste = mod_prix - mod_caution
                    st.sidebar.markdown(f"**🔴 Reste :** `{mod_reste} DT`")

                    st.sidebar.markdown("---")
                    mod_lieu = st.sidebar.text_input("Lieu Réception : ", value=init_lieu, key=f"mod_lieu_{selected_id}")
                    mod_vol = st.sidebar.text_input("N° Vol : ", value=init_vol, key=f"mod_vol_{selected_id}")
                    mod_km_deb = st.sidebar.number_input("KM Départ : ", min_value=0, value=init_km_deb, key=f"mod_km_{selected_id}")
                    mod_note = st.sidebar.text_area("Note : ", value=init_note, key=f"mod_note_{selected_id}")

                    if st.sidebar.button("💾 ENREGISTRER LES MODIFICATIONS", key=f"mod_save_{selected_id}"):
                        try:
                            str_mod_d1 = mod_d1.strftime("%Y-%m-%d")
                            str_mod_d2 = mod_d2.strftime("%Y-%m-%d")
                            str_mod_t1 = mod_t1.strftime("%H:%M")
                            str_mod_t2 = mod_t2.strftime("%H:%M")

                            if mod_cin and mod_cin.strip():
                                if row_cli_init:
                                    update_row(T_CLIENT, {
                                        "Nom": mod_client,
                                        "Date Délivrance CIN": mod_date_cin.strftime("%Y-%m-%d"),
                                        "N° Permis": mod_permis,
                                        "Date Délivrance Permis": mod_date_permis.strftime("%Y-%m-%d")
                                    }, "CIN", mod_cin)
                                else:
                                    insert_row(T_CLIENT, {
                                        "Nom": mod_client, "CIN": mod_cin,
                                        "N° Permis": mod_permis,
                                        "Date Délivrance CIN": mod_date_cin.strftime("%Y-%m-%d"),
                                        "Date Délivrance Permis": mod_date_permis.strftime("%Y-%m-%d")
                                    })

                            ok_update = update_row(T_MOUVEMENT, {
                                "Matricule": mod_vehicule,
                                "Type_Statut": mod_nature,
                                "Client": mod_client,
                                "Date_Debut": str_mod_d1,
                                "Heure_Debut": str_mod_t1,
                                "Date_Fin": str_mod_d2,
                                "Heure_Fin": str_mod_t2,
                                "Prix": str(mod_prix),
                                "Caution": str(mod_caution),
                                "Reste": str(mod_reste),
                                "Lieu_Reception": mod_lieu,
                                "No_Vol": mod_vol,
                                "Info_Note": mod_note,
                                "KM_Debut": int(mod_km_deb)
                            }, "id", int(selected_id))

                            if ok_update:
                                upsert_vidange(mod_vehicule, "", int(mod_km_deb))
                                st.sidebar.success("✅ Données mises à jour avec succès !")
                                get_all_tables.clear()
                                rerun()
                            else:
                                st.sidebar.error("❌ Échec de la mise à jour")
                        except Exception as e:
                            st.sidebar.error(f"❌ Erreur : {e}")
                            traceback.print_exc()
        else:
            st.sidebar.info("📭 Aucun dossier à modifier.")
    else:
        st.sidebar.info("📭 Aucun dossier enregistré dans la base.")

# --- ❌ SUPPRIMER OPÉRATION ---
elif menu_action == "❌ Supprimer une opération":
    df_mouv_actifs = pd.DataFrame()
    if not df_mouvs.empty:
        if 'Statut_Mouvement' in df_mouvs.columns:
            df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        else:
            df_mouv_actifs = df_mouvs.copy()

    if not df_mouv_actifs.empty and 'id' in df_mouv_actifs.columns:
        liste_mouv_del = []
        id_map_del = {}
        for _, r in df_mouv_actifs.iterrows():
            try:
                raw_id = r.get('id')
                if pd.isna(raw_id):
                    continue
                real_id = safe_id(raw_id)
                if real_id < 0:
                    continue
                label = f"ID: {real_id} | {safe_str(r.get('Matricule', ''))} — {safe_str(r.get('Client', ''))}"
                liste_mouv_del.append(label)
                id_map_del[label] = real_id
            except Exception:
                continue

        if liste_mouv_del:
            with st.sidebar.form("form_bbnh_delete_mouv"):
                mouv_selectionne = st.selectbox("Choisir l'opération : ", liste_mouv_del)
                confirmer_action = st.checkbox("Confirmer la suppression")
                if st.form_submit_button("💥 RETIRER DU PLANNING"):
                    if confirmer_action:
                        id_to_delete = id_map_del.get(mouv_selectionne, -1)
                        if id_to_delete >= 0:
                            delete_row(T_MOUVEMENT, "id", id_to_delete)
                            st.success("✅ Opération effacée !")
                            get_all_tables.clear()
                            rerun()
                        else:
                            st.error("❌ ID invalide")
        else:
            st.sidebar.info("📭 Aucune opération à supprimer.")
    else:
        st.sidebar.info("Aucune opération à supprimer.")

# --- 🆕 TRANSFORMER RÉSERVATION → CONTRAT (VERSION AMÉLIORÉE) ---
elif menu_action == "🔄 Transformer Réservation → Contrat":
    st.sidebar.markdown("### 🔄 Transformer une Réservation en Contrat")
    st.sidebar.info("💡 Cette action convertit une **Réservation** en **Contrat Location** officiel dans la base de données.")
    
    # Filtrage intelligent des réservations
    df_reservations = pd.DataFrame()
    if not df_mouvs.empty and 'Type_Statut' in df_mouvs.columns:
        # Filtrer uniquement les réservations actives
        mask_resa = df_mouvs['Type_Statut'].astype(str).str.contains(
            'reserv|resa|booking', 
            case=False, 
            na=False, 
            regex=True
        )
        
        if 'Statut_Mouvement' in df_mouvs.columns:
            mask_actif = df_mouvs['Statut_Mouvement'] == 'En cours'
            df_reservations = df_mouvs[mask_resa & mask_actif]
        else:
            df_reservations = df_mouvs[mask_resa]
    
    if not df_reservations.empty and 'id' in df_reservations.columns:
        st.sidebar.success(f"🟣 **{len(df_reservations)} réservation(s)** trouvée(s)")
        
        liste_resa = []
        id_map_resa = {}
        for _, r in df_reservations.iterrows():
            try:
                raw_id = r.get('id')
                if pd.isna(raw_id):
                    continue
                real_id = safe_id(raw_id)
                if real_id < 0:
                    continue
                
                mat = safe_str(r.get('Matricule', ''))
                cli = safe_str(r.get('Client', ''))
                d_deb = safe_str(r.get('Date_Debut', ''))
                d_fin = safe_str(r.get('Date_Fin', ''))
                
                label = f"ID {real_id} | {mat} — {cli} ({d_deb} → {d_fin})"
                liste_resa.append(label)
                id_map_resa[label] = real_id
            except Exception:
                continue
        
        if liste_resa:
            with st.sidebar.form("form_transform_resa"):
                resa_selectionnee = st.selectbox(
                    "📋 Choisir la réservation à transformer : ", 
                    liste_resa,
                    help="Sélectionnez la réservation que vous souhaitez convertir en contrat"
                )
                
                # Afficher les détails de la réservation sélectionnée
                if resa_selectionnee:
                    id_resa = id_map_resa.get(resa_selectionnee, -1)
                    if id_resa >= 0:
                        row_resa = df_reservations[df_reservations['id'].apply(lambda x: safe_id(x)) == id_resa].iloc[0]
                        st.markdown("---")
                        st.markdown("**📝 Détails de la réservation :**")
                        st.write(f"🚗 **Véhicule :** {safe_str(row_resa.get('Matricule', 'N/A'))}")
                        st.write(f"👤 **Client :** {safe_str(row_resa.get('Client', 'N/A'))}")
                        st.write(f"📅 **Période :** {safe_str(row_resa.get('Date_Debut', ''))} → {safe_str(row_resa.get('Date_Fin', ''))}")
                        st.write(f"💰 **Montant :** {safe_float(row_resa.get('Prix', 0)):,.2f} DT")
                        st.markdown("---")
                
                confirmer_transformation = st.checkbox(
                    "⚠️ Je confirme la transformation (cette action est irréversible)",
                    help="La réservation sera convertie en contrat location officiel"
                )
                
                if st.form_submit_button("🔄 TRANSFORMER EN CONTRAT", use_container_width=True, type="primary"):
                    if confirmer_transformation:
                        id_resa = id_map_resa.get(resa_selectionnee, -1)
                        if id_resa >= 0:
                            with st.spinner("Transformation en cours..."):
                                ok, msg = transformer_reservation_en_contrat(id_resa)
                                if ok:
                                    st.success(msg)
                                    get_all_tables.clear()
                                    rerun()
                                else:
                                    st.error(msg)
                        else:
                            st.error("❌ ID invalide")
                    else:
                        st.warning("⚠️ Veuillez cocher la case de confirmation pour continuer")
        else:
            st.sidebar.info("📭 Aucune réservation valide à transformer.")
    else:
        st.sidebar.warning("🔴 Aucune réservation trouvée dans la base de données.")
        st.sidebar.info("💡 Créez d'abord une réservation via le menu **📝 Nouveau Contrat / Réservation**")

# ============================================================
# ESPACE CENTRAL
# ============================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION</h1>", unsafe_allow_html=True)

# Recherche avancée
with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    with c_search1:
        search_date_debut = st.date_input("📅 Date de Sortie : ", datetime.now(), key="adv_search_start")
    with c_search2:
        search_date_fin = st.date_input("📅 Date de Retour : ", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")

        df_disponibles = df_voitures.copy() if not df_voitures.empty else pd.DataFrame()
        if not df_mouvs.empty and not df_disponibles.empty and 'Matricule' in df_disponibles.columns:
            matricules_indisponibles = set()
            for _, mv in df_mouvs.iterrows():
                if safe_str(mv.get('Statut_Mouvement')) != 'En cours':
                    continue
                d_debut_mv = parse_date(mv.get('Date_Debut'))
                d_fin_mv = parse_date(mv.get('Date_Fin'))
                if d_debut_mv and d_fin_mv:
                    if not (d_fin_mv < search_date_debut or d_debut_mv > search_date_fin):
                        matricules_indisponibles.add(safe_str(mv.get('Matricule')))
            df_disponibles = df_disponibles[~df_disponibles['Matricule'].astype(str).str.strip().isin(matricules_indisponibles)]

        if not df_disponibles.empty:
            st.markdown(f"##### 🚗 {len(df_disponibles)} Véhicule(s) disponible(s) du `{str_s_start}` au `{str_s_end}` :")
            cols_aff = [c for c in ['Matricule', 'Marque', 'Modèle', 'Année'] if c in df_disponibles.columns]
            df_disp_aff = df_disponibles[cols_aff].rename(columns={
                'Matricule': '🚘 Matricule', 'Marque': 'Marque', 'Modèle': 'Modèle', 'Année': 'Année'
            })
            st.dataframe(df_disp_aff, use_container_width=True, hide_index=True)
        else:
            st.warning(f"❌ Aucun véhicule disponible du {str_s_start} au {str_s_end}.")

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
    with f_col_date_start:
        date_base = st.date_input("Date de début de la grille :", datetime(2026, 1, 1), key="grid_bbnh_date")
    with f_col_date_target:
        recherche_date = st.date_input("📅 Aller à la date spécifique (Focus) :", datetime(2026, 6, 26))

    array_jours = [date_base + timedelta(days=i) for i in range(365)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    df_voitures_valides = df_voitures[df_voitures['Matricule'].notna() & (df_voitures['Matricule'].astype(str).str.strip() != '')] if not df_voitures.empty else pd.DataFrame()

    if not df_voitures_valides.empty:
        build_matrix = []
        voiture_filter = vehicule_recherche != "-- Toutes les voitures --"
        for _, car in df_voitures_valides.iterrows():
            immat = safe_str(car.get('Matricule'))
            if voiture_filter and immat != vehicule_recherche:
                continue
            modele = safe_str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            ligne = {"Flotte BBNH": f"🚘 {modele} — [{immat}]"}
            for col_j in nom_colonnes:
                ligne[col_j] = "● Disponible"
            build_matrix.append(ligne)

        if build_matrix:
            df_final_grid = pd.DataFrame(build_matrix)

            suivi_jours = {}
            if not df_mouvs.empty:
                mv_list = []
                for _, mv in df_mouvs.iterrows():
                    m_v = safe_str(mv.get('Matricule'))
                    if not m_v:
                        continue
                    d_debut_mv = parse_date(mv.get('Date_Debut'))
                    d_fin_mv = parse_date(mv.get('Date_Fin'))
                    if not (d_debut_mv and d_fin_mv):
                        continue
                    s_v = safe_str(mv.get('Type_Statut')).lower()
                    client_v = safe_str(mv.get('Client'))
                    h_deb_label = formater_heure_propre(mv.get('Heure_Debut'))
                    h_fin_label = formater_heure_propre(mv.get('Heure_Fin'))
                    mv_list.append((m_v, d_debut_mv, d_fin_mv, s_v, client_v, h_deb_label, h_fin_label))

                for m_v, d_debut_mv, d_fin_mv, s_v, client_v, h_deb_label, h_fin_label in mv_list:
                    if m_v not in suivi_jours:
                        suivi_jours[m_v] = {}

                    current_day = d_debut_mv
                    while current_day <= d_fin_mv:
                        key_day = current_day.strftime("%d/%m")
                        if key_day not in suivi_jours[m_v]:
                            suivi_jours[m_v][key_day] = {
                                "depart": False, "fin": False,
                                "client_sortant": "", "client_entrant": "",
                                "heure_sortie": "00:00", "heure_retour": "00:00",
                                "desc": ""
                            }
                        if current_day == d_debut_mv:
                            suivi_jours[m_v][key_day]["depart"] = True
                            suivi_jours[m_v][key_day]["client_sortant"] = client_v
                            suivi_jours[m_v][key_day]["heure_sortie"] = h_deb_label
                        if current_day == d_fin_mv:
                            suivi_jours[m_v][key_day]["fin"] = True
                            suivi_jours[m_v][key_day]["client_entrant"] = client_v
                            suivi_jours[m_v][key_day]["heure_retour"] = h_fin_label
                        if not (suivi_jours[m_v][key_day]["depart"] and suivi_jours[m_v][key_day]["fin"]):
                            if "garage" in s_v or "maintenance" in s_v:
                                suivi_jours[m_v][key_day]["desc"] = f"🛠️ GARAGE : {client_v}"
                            elif "réservation" in s_v or "reservation" in s_v:
                                suivi_jours[m_v][key_day]["desc"] = f"🟣 [{h_deb_label}➔{h_fin_label}] {client_v}"
                            else:
                                suivi_jours[m_v][key_day]["desc"] = f"🟢 [{h_deb_label}➔{h_fin_label}] {client_v}"
                        current_day += timedelta(days=1)

            for idx, row in df_final_grid.iterrows():
                mat_extracted = row["Flotte BBNH"].split("[")[-1].replace("]", "").strip()
                if mat_extracted in suivi_jours:
                    for key_day, data in suivi_jours[mat_extracted].items():
                        if key_day in df_final_grid.columns:
                            if data["depart"] and data["fin"]:
                                df_final_grid.at[idx, key_day] = f"🔵 🛬{data['heure_retour']} {data['client_entrant']} / 🛫{data['heure_sortie']} {data['client_sortant']}"
                            elif data["desc"]:
                                df_final_grid.at[idx, key_day] = data["desc"]

            def style_bbnh_theme(val):
                val_str = str(val)
                if "● Disponible" in val_str:
                    return "background-color: #ffffff; color: #111827; font-size: 11px; font-weight: 600; text-align: center; border: 1px solid #e5e7eb;"
                elif "🔵" in val_str:
                    return "background-color: #1d4ed8; color: #ffffff; font-weight: 700; font-size: 10px; border: 2px solid #60a5fa;"
                elif "🛠️" in val_str:
                    return "background-color: #eab308; color: #1e1b4b; font-weight: 700; font-size: 11px;"
                elif "🟣" in val_str:
                    return "background-color: #8b5cf6; color: #ffffff; font-weight: 600; font-size: 11px;"
                elif "🔴" in val_str:
                    return "background-color: #dc2626; color: #ffffff; font-weight: 600; font-size: 11px;"
                elif "🟢" in val_str:
                    return "background-color: #16a34a; color: #ffffff; font-weight: 600; font-size: 11px;"
                return "background-color: #090b0e; color: #ffffff; font-weight: 700; font-size: 12px; border-right: 3px solid #e60000;"

            target_col_str = recherche_date.strftime("%d/%m")
            cols_ordonnees = ['Flotte BBNH']
            if target_col_str in nom_colonnes:
                idx_target = nom_colonnes.index(target_col_str)
                cols_ordonnees += nom_colonnes[max(0, idx_target - 2):min(365, idx_target + 12)]

            styled_df = df_final_grid[cols_ordonnees].style
            styled_df = style_apply(styled_df, style_bbnh_theme, subset=[c for c in cols_ordonnees if c != 'Flotte BBNH'])
            st.dataframe(styled_df, use_container_width=True, height=800)

# --- TAB 2 : LISTE DE CONTRAT ---
with tab_contrats:
    st.markdown("### 📄 Liste Détaillée des Contrats & Mouvements")
    
    # Compteur de réservations
    df_resa_count = pd.DataFrame()
    if not df_mouvs.empty and 'Type_Statut' in df_mouvs.columns:
        mask_resa = df_mouvs['Type_Statut'].astype(str).str.contains('reserv|resa|booking', case=False, na=False, regex=True)
        if 'Statut_Mouvement' in df_mouvs.columns:
            mask_actif = df_mouvs['Statut_Mouvement'] == 'En cours'
            df_resa_count = df_mouvs[mask_resa & mask_actif]
        else:
            df_resa_count = df_mouvs[mask_resa]
    
    if not df_resa_count.empty:
        st.info(f"🟣 **{len(df_resa_count)} réservation(s) en attente de transformation en contrat**")
    
    if not df_mouvs.empty and 'id' in df_mouvs.columns:
        df_contrats_list = df_mouvs.sort_values(by='id', ascending=False)
    else:
        df_contrats_list = df_mouvs

    if not df_contrats_list.empty:
        tel_index = {}
        if not df_clients.empty and 'Nom' in df_clients.columns and 'Numéro de téléphone' in df_clients.columns:
            for _, c_row in df_clients.iterrows():
                c_nom = safe_str(c_row.get('Nom'))
                c_tel = c_row.get('Numéro de téléphone')
                if c_nom and c_tel and not (isinstance(c_tel, float) and pd.isna(c_tel)):
                    tel_index[c_nom.lower()] = str(c_tel)

        html_table = """
        <table class="contract-table">
            <thead><tr>
                <th>Type</th><th>Voiture</th><th>Tél</th><th>N° Contrat</th>
                <th>D.Départ</th><th>D.Retour</th><th>Jours</th>
                <th>Montant TTC(DT)</th><th>Reste(DT)</th>
                <th>KM Sortie</th><th>KM Retour</th>
            </tr></thead><tbody>
        """
        
        for _, row in df_contrats_list.iterrows():
            try:
                matricule = safe_str(row.get('Matricule'), 'N/A')
                client = safe_str(row.get('Client'))
                tel = tel_index.get(client.lower(), "N/A") if client else "N/A"
                
                type_statut = safe_str(row.get('Type_Statut', '')).lower()
                is_reservation = est_une_reservation(type_statut)
                
                if is_reservation:
                    type_badge = '<span class="status-badge status-reservation">🟣 RÉSERVATION</span>'
                else:
                    type_badge = '<span class="status-badge status-contrat">🟢 CONTRAT</span>'

                raw_id = row.get('id')
                if pd.notna(raw_id):
                    num_contrat = f"{int(float(str(raw_id)))}"
                else:
                    num_contrat = matricule

                d_dep_dt = parse_date(row.get('Date_Debut')) or datetime.now().date()
                d_ret_dt = parse_date(row.get('Date_Fin')) or datetime.now().date()
                d_dep = d_dep_dt.strftime("%d/%m/%Y")
                d_ret = d_ret_dt.strftime("%d/%m/%Y")
                jours = max(1, (d_ret_dt - d_dep_dt).days)

                h_dep = formater_heure_propre(row.get('Heure_Debut'))
                h_ret = formater_heure_propre(row.get('Heure_Fin'))

                montant = f"{safe_float(row.get('Prix')):,.3f}"
                reste_val = safe_float(row.get('Reste'))
                reste_style = "status-paid" if reste_val <= 0 else "status-pending"
                reste_text = "PAYÉ" if reste_val <= 0 else f"{reste_val:,.3f} DT"
                km_s = safe_int(row.get('KM_Debut'))
                km_r = safe_int(row.get('KM_Fin'))

                km_ess_s = f"{km_s // 100} Km/Ess"
                km_j_s = f"{km_s // 200} Km/j"
                km_j_r = f"{km_r // 200} Km/j"

                html_table += f"""
                    <tr>
                        <td>{type_badge}</td>
                        <td>
                            <div class="car-info">
                                <img src="https://img.icons8.com/ios-filled/50/000000/car.png" class="car-image">
                                <div class="car-plate">{matricule}</div>
                            </div>
                        </td>
                        <td style="color:#007bff; font-weight:bold;">{tel}</td>
                        <td><div class="contract-num">{num_contrat}</div></td>
                        <td>{d_dep}<br>{h_dep}</td>
                        <td>{d_ret}<br>{h_ret}</td>
                        <td>{jours} j</td>
                        <td style="font-weight:bold;">{montant}</td>
                        <td><span class="status-badge {reste_style}">✔ {reste_text}</span></td>
                        <td>
                            <div class="km-box">
                                <div class="km-value" style="color:#28a745;">{km_s} Km</div>
                                <div class="km-indicator km-blue">{km_ess_s}</div>
                                <div class="km-indicator km-yellow">{km_j_s}</div>
                            </div>
                        </td>
                        <td>
                            <div class="km-box">
                                <div class="km-value" style="color:#dc3545;">{km_r} Km</div>
                                <div class="km-indicator km-green">{km_j_r}</div>
                            </div>
                        </td>
                    </tr>
                """
            except Exception:
                continue
        html_table += "</tbody></table>"
        st.markdown(html_table, unsafe_allow_html=True)
        
        # 🆕 Section Actions Rapides AMÉLIORÉE
        st.markdown("---")
        st.markdown("### ⚡ Actions Rapides sur les Réservations")
        
        if not df_resa_count.empty and 'id' in df_resa_count.columns:
            st.info(f"🟣 **{len(df_resa_count)} réservation(s)** en attente de transformation")
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown("**🔄 Transformer une réservation en contrat :**")
                options_resa = []
                id_map_resa_tab = {}
                for _, r in df_resa_count.iterrows():
                    try:
                        rid = safe_id(r.get('id'))
                        if rid < 0:
                            continue
                        mat = safe_str(r.get('Matricule', ''))
                        cli = safe_str(r.get('Client', ''))
                        d_deb = safe_str(r.get('Date_Debut', ''))
                        label = f"ID {rid} | {mat} — {cli} ({d_deb})"
                        options_resa.append(label)
                        id_map_resa_tab[label] = rid
                    except Exception:
                        continue
                
                if options_resa:
                    resa_choice = st.selectbox("Choisir la réservation :", options_resa, key="tab_resa_choice")
                    
                    col_btn1, col_btn2 = st.columns([1, 1])
                    with col_btn1:
                        if st.button("🔄 TRANSFORMER EN CONTRAT", key="btn_transform_tab", type="primary"):
                            id_resa = id_map_resa_tab.get(resa_choice, -1)
                            if id_resa >= 0:
                                with st.spinner("Transformation en cours..."):
                                    ok, msg = transformer_reservation_en_contrat(id_resa)
                                    if ok:
                                        st.success(msg)
                                        get_all_tables.clear()
                                        rerun()
                                    else:
                                        st.error(msg)
                            else:
                                st.error("❌ ID invalide")
                    
                    with col_btn2:
                        if st.button("✏️ MODIFIER CETTE RÉSERVATION", key="btn_edit_resa_tab"):
                            st.info("💡 Utilisez le menu **⚙️ Modifier un Dossier** dans la barre latérale pour modifier cette réservation")
                else:
                    st.info("Aucune réservation à transformer")
            else:
                st.info("Aucune réservation à transformer")
            
            with col2:
                st.markdown("**📊 Statistiques :**")
                st.metric("Total Réservations", len(df_resa_count))
                st.metric("Contrats Actifs", len(df_mouvs) - len(df_resa_count) if not df_mouvs.empty else 0)
        else:
            st.success("✅ Aucune réservation en attente - Tous les contrats sont à jour !")
        
    else:
        st.info("Aucun contrat ou mouvement enregistré pour le moment.")

# --- TAB 3 : RECEPTION LOGISTIQUE ---
with tab_logistique:
    st.markdown("### 🔑 Terminal de Restitution et Clôture")
    df_actifs = pd.DataFrame()
    if not df_mouvs.empty:
        if 'Statut_Mouvement' in df_mouvs.columns:
            df_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        else:
            df_actifs = df_mouvs.copy()

    if not df_actifs.empty and 'id' in df_actifs.columns:
        choix_actifs = []
        id_map_retour = {}
        for _, r in df_actifs.iterrows():
            try:
                raw_id = r.get('id')
                if pd.isna(raw_id):
                    continue
                real_id = safe_id(raw_id)
                if real_id < 0:
                    continue
                type_stat = safe_str(r.get('Type_Statut', ''))
                label = f"ID: {real_id} | {safe_str(r.get('Matricule', ''))} — {safe_str(r.get('Client', ''))} [{type_stat}]"
                choix_actifs.append(label)
                id_map_retour[label] = real_id
            except Exception:
                continue

        if choix_actifs:
            col_list, col_details = st.columns([1, 1])
            with col_list:
                target_v = st.selectbox("Sélectionner le véhicule rentrant : ", choix_actifs)
                d_reel = st.date_input("Date de retour physique effective : ", datetime.now())
                t_reel = st.time_input("Heure de retour effective : ", datetime.now().time())
                l_retour = st.text_input("Lieu de retour effectif : ", value="Siège Monastir")

                id_mouv_temp = id_map_retour.get(target_v, -1)
                res_dep = df_actifs[df_actifs['id'].apply(lambda x: safe_id(x)) == id_mouv_temp] if id_mouv_temp >= 0 else pd.DataFrame()
                km_dep_de_base = safe_int(res_dep.iloc[0].get('KM_Debut')) if not res_dep.empty else 0
                km_fin = st.number_input("Kilométrage au Retour : ", min_value=km_dep_de_base, value=km_dep_de_base, step=1)

                if st.button("✅ VALIDATION DU RETOUR", use_container_width=True):
                    if id_mouv_temp < 0:
                        st.error("❌ ID invalide")
                    else:
                        try:
                            vehicule_rentre = safe_str(res_dep.iloc[0].get('Matricule')) if not res_dep.empty else ''
                            update_row(T_MOUVEMENT, {
                                "Statut_Mouvement": "Retourné",
                                "Date_Fin": d_reel.strftime("%Y-%m-%d"),
                                "Heure_Fin": t_reel.strftime("%H:%M"),
                                "Lieu_Reception": l_retour,
                                "KM_Fin": int(km_fin)
                            }, "id", int(id_mouv_temp))
                            upsert_vidange(vehicule_rentre, "", int(km_fin))
                            st.success("✅ Le retour a été validé !")
                            get_all_tables.clear()
                            rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
            with col_details:
                if not res_dep.empty:
                    row_sel = res_dep.iloc[0]
                    diff_km = int(km_fin) - int(km_dep_de_base)
                    st.markdown(f"**📊 Distance Parcourue :** <span style='color:#4ade80; font-weight:bold; font-size:22px;'>{diff_km} KM</span>", unsafe_allow_html=True)
                    st.write(f"**Reste dû :** {row_sel.get('Reste', '0')} DT")
        else:
            st.info("Aucun déplacement en cours.")
    else:
        st.info("Aucun déplacement en cours.")

# --- TAB 4 : PERFORMANCE ---
with tab_analytics:
    st.markdown("### 📊 Chiffre d'Affaires & Synthèse Logistique du Jour")
    day_target = st.date_input("Sélectionner la journée d'analyse :", datetime.now())
    if not df_mouvs.empty:
        df_stats = df_mouvs.copy()
        df_stats['Clean_D'] = pd.to_datetime(df_stats['Date_Debut'], errors='coerce').dt.date
        df_stats['Clean_F'] = pd.to_datetime(df_stats['Date_Fin'], errors='coerce').dt.date
        df_stats['KM_Debut'] = pd.to_numeric(df_stats['KM_Debut'], errors='coerce').fillna(0).astype(int)
        df_stats['KM_Fin'] = pd.to_numeric(df_stats['KM_Fin'], errors='coerce').fillna(0).astype(int)
        df_stats['Val_Prix'] = df_stats['Prix'].apply(safe_float)

        sorties = df_stats[df_stats['Clean_D'] == day_target]
        entrees = df_stats[df_stats['Clean_F'] == day_target]

        k1, k2, k3 = st.columns(3)
        with k1:
            st.metric("📈 DÉPARTS CONSTATÉS", f"{len(sorties)} Véhicule(s)")
        with k2:
            st.metric("🔑 RETOURS ENREGISTRÉS", f"{len(entrees)} Véhicule(s)")
        with k3:
            st.metric("💰 CA DU JOUR (DÉPARTS)", f"{sorties['Val_Prix'].sum():,.2f} DT")

        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("### 🛫 1. VOITURES SORTIES (DÉPARTS)")
            if not sorties.empty:
                cols = [c for c in ['Matricule', 'Client', 'Type_Statut', 'Date_Debut', 'Date_Fin', 'Prix', 'KM_Debut'] if c in sorties.columns]
                sorties_final = sorties[cols].rename(columns={
                    'Matricule': '🚘 Matricule', 'Client': '👤 Client',
                    'Type_Statut': '📋 Type', 'Date_Debut': '📅 DATE SORTIE',
                    'Date_Fin': '📅 DATE RETOUR', 'Prix': '💰 PRIX (DT)', 'KM_Debut': '🔢 KM SORTIE'
                })
                st.dataframe(sorties_final, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun véhicule n'est parti à cette date.")
        with col_droite:
            st.markdown("### 🛬 2. VOITURES RETOURNÉES (RETOURS)")
            if not entrees.empty:
                entrees_c = entrees.copy()
                entrees_c['KM Roulé'] = entrees_c['KM_Fin'] - entrees_c['KM_Debut']
                entrees_c['Heure_Retour_Propre'] = entrees_c['Heure_Fin'].apply(formater_heure_propre)
                cols = [c for c in ['Matricule', 'Client', 'Type_Statut', 'Date_Fin', 'Heure_Retour_Propre', 'Lieu_Reception', 'Prix', 'KM Roulé'] if c in entrees_c.columns]
                entrees_final = entrees_c[cols].rename(columns={
                    'Matricule': '🚘 Matricule', 'Client': '👤 Client',
                    'Type_Statut': '📋 Type', 'Date_Fin': '📅 DATE RETOUR',
                    'Heure_Retour_Propre': '🕒 HEURE RETOUR', 'Lieu_Reception': '📍 LIEU',
                    'Prix': '💰 PRIX (DT)', 'KM Roulé': '🔥 KM ROULÉ'
                })
                st.dataframe(entrees_final, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun retour physique enregistré à cette date.")

# --- TAB 5 : VIDANGES ---
with tab_vidange:
    st.markdown("### 🔧 Tableau de bord de Maintenance & Vidanges Automatisé")
    if not df_vidanges.empty:
        df_v = df_vidanges.copy()
        df_v['KM_Dernier_Vidange'] = pd.to_numeric(df_v['KM_Dernier_Vidange'], errors='coerce').fillna(0).astype(int)
        df_v['KM_Recent'] = pd.to_numeric(df_v['KM_Recent'], errors='coerce').fillna(0).astype(int)
        df_v['KM cerculer'] = df_v['KM_Recent'] - df_v['KM_Dernier_Vidange']
        df_v['km restant'] = 9000 - df_v['KM cerculer']

        alertes_critiques = df_v[df_v['km restant'] <= 1500]
        if not alertes_critiques.empty:
            st.error(f"⚠️ **ALERTE VIDANGE :** {len(alertes_critiques)} véhicule(s) doivent être vidangés immédiatement !")
        else:
            st.success("✅ État de la flotte parfait : aucune vidange urgente.")

        cols_aff = [c for c in ['Date_Mise_A_Jour', 'Marque', 'Matricule', 'Date_Dernier_Vidange', 'KM_Dernier_Vidange', 'KM_Recent', 'KM cerculer', 'km restant'] if c in df_v.columns]
        df_tableau_affichage = df_v[cols_aff].rename(columns={
            'Date_Mise_A_Jour': 'DATE MIS AJOURS', 'Marque': 'MARQUE', 'Matricule': 'MATRICULE',
            'Date_Dernier_Vidange': 'TE DERNIER VIDAN', 'KM_Dernier_Vidange': 'DERNIER VIDA',
            'KM_Recent': 'KM RECENT', 'KM cerculer': 'KM cerculer', 'km restant': 'km restant'
        })

        def colorer_vidanges(row):
            val_restant = row['km restant']
            if val_restant <= 500:
                return ['background-color: #ef4444; color: white; font-weight: bold;'] * len(row)
            elif val_restant <= 1500:
                return ['background-color: #f97316; color: white; font-weight: bold;'] * len(row)
            return [''] * len(row)

        styled = df_tableau_affichage.style.apply(colorer_vidanges, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            if 'Matricule' in df_v.columns and not df_v.empty:
                c_v1, c_v2, c_v3 = st.columns([1.5, 1.5, 2])
                with c_v1:
                    v_select = st.selectbox("Sélectionner le véhicule à mettre à jour : ", df_v['Matricule'].tolist())
                    v_info = df_v[df_v['Matricule'] == v_select].iloc[0]
                    init_date_dernier = parse_date(v_info.get('Date_Dernier_Vidange')) or datetime.now().date()
                    date_dernier_manuel = st.date_input("Date du Dernier Vidange (Manuel) : ", value=init_date_dernier)
                with c_v2:
                    dernier_km_vidange_input = st.number_input("Dernier KM Vidange (Manuel) : ", min_value=0, value=safe_int(v_info.get('KM_Dernier_Vidange')), step=1)
                    nouveau_km_actuel = st.number_input("Kilométrage Actuel / Récent (Manuel) : ", min_value=0, value=safe_int(v_info.get('KM_Recent')), step=1)
                with c_v3:
                    date_effective = st.date_input("Date effective de l'opération : ", datetime.now())
                    action_sync = st.checkbox("Vidange effectuée aujourd'hui (Synchronise le dernier KM et remet à zéro)", value=False)

                if st.button("💾 ENREGISTRER ET RECALCULER DIRECTEMENT", use_container_width=True):
                    date_operation_str = date_effective.strftime("%Y-%m-%d")
                    date_historique_str = date_dernier_manuel.strftime("%Y-%m-%d")
                    if action_sync:
                        update_row(T_VIDANGE, {
                            "KM_Recent": int(nouveau_km_actuel), "KM_Dernier_Vidange": int(nouveau_km_actuel),
                            "Date_Dernier_Vidange": date_operation_str, "Date_Mise_A_Jour": date_operation_str
                        }, "Matricule", v_select)
                    else:
                        update_row(T_VIDANGE, {
                            "KM_Recent": int(nouveau_km_actuel), "KM_Dernier_Vidange": int(dernier_km_vidange_input),
                            "Date_Dernier_Vidange": date_historique_str, "Date_Mise_A_Jour": date_operation_str
                        }, "Matricule", v_select)
                    st.success("✅ Calculs mis à jour instantanément !")
                    get_all_tables.clear()
                    rerun()

# --- TAB 6 : COMPTE CONDUCTEURS / CRM ---
with tab_crm:
    st.markdown("### 👥 Banque d'Information des Conducteurs & Profils Clients")
    c1, c2 = st.columns([5, 4])
    with c1:
        st.markdown("#### 🔍 Consultation & Actions")
        search_query = st.text_input("Rechercher un profil (Nom, Prénom, CIN) : ", key="crm_search_field")

        if search_query and not df_clients.empty:
            mask = df_clients['Nom'].str.contains(search_query, case=False, na=False)
            if 'Prénom' in df_clients.columns:
                mask = mask | df_clients['Prénom'].str.contains(search_query, case=False, na=False)
            if 'CIN' in df_clients.columns:
                mask = mask | df_clients['CIN'].str.contains(search_query, case=False, na=False)

            clients_trouves = df_clients[mask]

            if not clients_trouves.empty:
                for idx, cli in clients_trouves.iterrows():
                    cin_client_actuel = safe_str(cli.get('CIN'))
                    unique_suffix = f"{idx}_{cin_client_actuel}"

                    if f"mode_edition_{unique_suffix}" not in st.session_state:
                        st.session_state[f"mode_edition_{unique_suffix}"] = False
                    if f"chk_del_{unique_suffix}" not in st.session_state:
                        st.session_state[f"chk_del_{unique_suffix}"] = False

                    with st.expander(f"👤 {safe_str(cli.get('Nom')).upper()} {safe_str(cli.get('Prénom'))} (CIN: {cin_client_actuel})", expanded=True):
                        st.write(f"**📞 Téléphone :** `{cli.get('Numéro de téléphone', 'N/A')}` | **🚗 N° Permis :** `{cli.get('N° Permis', 'N/A')}`")

                        col_img1, col_img2 = st.columns(2)
                        with col_img1:
                            img_cin = cli.get('Image CIN')
                            if img_cin and not (isinstance(img_cin, float) and pd.isna(img_cin)):
                                try:
                                    st.image(base64.b64decode(img_cin), caption="Pièce d'identité (CIN)", use_container_width=True)
                                except Exception:
                                    pass
                        with col_img2:
                            img_per = cli.get('Image Permis')
                            if img_per and not (isinstance(img_per, float) and pd.isna(img_per)):
                                try:
                                    st.image(base64.b64decode(img_per), caption="Permis de conduire", use_container_width=True)
                                except Exception:
                                    pass

                        st.markdown("---")
                        col_btn_mod, col_btn_sup = st.columns(2)

                        with col_btn_mod:
                            if st.button(f"✏️ MODIFIER CE PROFIL", key=f"btn_edit_{unique_suffix}"):
                                st.session_state[f"mode_edition_{unique_suffix}"] = True
                                rerun()

                        with col_btn_sup:
                            check_sup = st.checkbox("Confirmer la suppression", key=f"chk_del_{unique_suffix}")
                            if st.button(f"🗑️ SUPPRIMER CE CLIENT", key=f"btn_del_{unique_suffix}"):
                                if check_sup:
                                    delete_row(T_CLIENT, "CIN", cin_client_actuel)
                                    st.success(f"✅ Client [CIN: {cin_client_actuel}] supprimé définitivement.")
                                    get_all_tables.clear()
                                    rerun()
                                else:
                                    st.warning("Veuillez cocher la case de confirmation avant de supprimer.")

                        if st.session_state.get(f"mode_edition_{unique_suffix}", False):
                            st.markdown("<br>", unsafe_allow_html=True)
                            with st.form(key=f"form_reel_edit_{unique_suffix}"):
                                st.markdown("##### 📝 Édition des informations")
                                e_prenom = st.text_input("Prénom", value=safe_str(cli.get('Prénom')))
                                e_nom = st.text_input("Nom", value=safe_str(cli.get('Nom')))
                                e_tel = st.text_input("Téléphone", value=safe_str(cli.get('Numéro de téléphone')))
                                e_permis = st.text_input("N° Permis", value=safe_str(cli.get('N° Permis')))

                                e_init_d_cin = parse_date(cli.get('Date Délivrance CIN')) or datetime.now().date()
                                e_init_d_per = parse_date(cli.get('Date Délivrance Permis')) or datetime.now().date()

                                e_d_cin = st.date_input("Date Délivrance CIN", value=e_init_d_cin)
                                e_d_per = st.date_input("Date Délivrance Permis", value=e_init_d_per)

                                f_cin_remplace = st.file_uploader("Remplacer l'image CIN (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_cin_{unique_suffix}")
                                f_per_remplace = st.file_uploader("Remplacer l'image Permis (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_per_{unique_suffix}")

                                if st.form_submit_button("✅ METTRE À JOUR"):
                                    upd = {
                                        "Prénom": e_prenom, "Nom": e_nom,
                                        "Numéro de téléphone": e_tel, "N° Permis": e_permis,
                                        "Date Délivrance CIN": e_d_cin.strftime("%Y-%m-%d"),
                                        "Date Délivrance Permis": e_d_per.strftime("%Y-%m-%d")
                                    }
                                    if f_cin_remplace:
                                        upd["Image CIN"] = encoder_image_base64(f_cin_remplace)
                                    if f_per_remplace:
                                        upd["Image Permis"] = encoder_image_base64(f_per_remplace)

                                    update_row(T_CLIENT, upd, "CIN", cin_client_actuel)
                                    st.success("✅ Profil mis à jour !")
                                    st.session_state[f"mode_edition_{unique_suffix}"] = False
                                    get_all_tables.clear()
                                    rerun()
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
                    insert_row(T_CLIENT, {
                        "Prénom": n_prenom, "Nom": n_nom, "CIN": n_cin,
                        "Numéro de téléphone": n_tel, "N° Permis": n_permis,
                        "Date Délivrance CIN": n_d_cin.strftime("%Y-%m-%d"),
                        "Date Délivrance Permis": n_d_per.strftime("%Y-%m-%d"),
                        "Image CIN": encoder_image_base64(f_cin_new),
                        "Image Permis": encoder_image_base64(f_per_new)
                    })
                    st.success("✅ Nouveau client enregistré !")
                    get_all_tables.clear()
                    rerun()
                else:
                    st.error("❌ Veuillez remplir les champs obligatoires (*)")

# --- TAB 7 : ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Panneau de Configuration Système")
    st.warning("⚠️ Attention : Ces actions sont irréversibles.")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🗑️ PURGER TOUS LES MOUVEMENTS"):
            if st.checkbox("Confirmer la purge des mouvements", key="chk_purge_mouv"):
                delete_all(T_MOUVEMENT)
                st.success("✅ Tous les mouvements ont été effacés.")
                get_all_tables.clear()
                rerun()
    with col_a2:
        if st.button("🗑️ RÉINITIALISER LA BASE CLIENTS"):
            if st.checkbox("Confirmer la purge des clients", key="chk_purge_cli"):
                delete_all(T_CLIENT)
                st.success("✅ La base clients a été réinitialisée.")
                get_all_tables.clear()
                rerun()
