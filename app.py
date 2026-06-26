import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
import base64
from datetime import datetime, timedelta, time
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

if hasattr(st, "rerun"):
    rerun = st.rerun
elif hasattr(st, "experimental_rerun"):
    rerun = st.experimental_rerun
else:
    def rerun(): pass

def style_apply(df_style, func, **kwargs):
    try:
        return df_style.map(func, **kwargs)
    except AttributeError:
        return df_style.applymap(func, **kwargs)

st.set_page_config(
    page_title="BBNH OS — Gestion Premium",
    layout="wide",
    page_icon="🏎️",
    initial_sidebar_state="expanded"
)

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
    st.stop()

T_CLIENT = "client"
T_VEHICULE = "vehicule"
T_MOUVEMENT = "mouvement"
T_VIDANGE = "vidange"
T_CONTRAT = "carbbnh"
T_VISITE_TECHNIQUE = "visite_technique"

MOUV_KEY_COLUMN = "Num_Contrat"

# ============================================================
#  CRÉATION AUTOMATIQUE DE LA TABLE VISITE TECHNIQUE
# ============================================================
def creer_table_visite_technique():
    """Crée la table visite_technique si elle n'existe pas via SQL"""
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS visite_technique (
            id BIGSERIAL PRIMARY KEY,
            "Matricule" TEXT UNIQUE NOT NULL,
            "Marque" TEXT,
            "Date_Premiere_Visite" DATE,
            "Date_Prochaine_Visite" DATE,
            "Date_Mise_A_Jour" DATE,
            "Statut" TEXT DEFAULT 'Active',
            created_at TIMESTAMPTZ DEFAULT NOW()
        );
        """
        response = supabase.rpc('exec_sql', {'query': sql}).execute()
        return True
    except Exception:
        # Fallback: essayer via l'insertion d'une ligne test
        try:
            supabase.table(T_VISITE_TECHNIQUE).insert({
                "Matricule": "_test_init_",
                "Marque": "INIT",
                "Date_Premiere_Visite": datetime.now().strftime("%Y-%m-%d"),
                "Date_Prochaine_Visite": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
                "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                "Statut": "Active"
            }).execute()
            # Supprimer la ligne test
            supabase.table(T_VISITE_TECHNIQUE).delete().eq("Matricule", "_test_init_").execute()
            return True
        except Exception as e2:
            return False

def verifier_table_visite_technique():
    """Vérifie si la table existe et est accessible"""
    try:
        response = supabase.table(T_VISITE_TECHNIQUE).select("Matricule").limit(1).execute()
        return True
    except Exception:
        return False

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
        return int(float(str(val).replace(' ', '').replace(',', '.')))
    except Exception:
        return default

def safe_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return default
        return float(str(val).replace(' ', '').replace(',', '.'))
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
            return parts[0].strip(), parts[1].replace(")", "").strip()
        return label.strip(), ""
    except Exception:
        return safe_str(label), ""

def est_une_reservation(type_statut):
    try:
        s = str(type_statut).strip().lower()
        s = s.replace('é', 'e').replace('è', 'e').replace('ê', 'e')
        return 'reserv' in s or 'resa' in s or 'booking' in s
    except Exception:
        return False

# ============================================================
# ⚡ FONCTIONS DATABASE - TOLÉRANTES AUX ERREURS
# ============================================================
def fetch_table_direct(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except Exception:
        return pd.DataFrame()

@st.cache_data(ttl=30, show_spinner=False)
def get_all_tables():
    """Charge toutes les tables - TOLÉRANT aux tables manquantes"""
    tables = [T_VEHICULE, T_CLIENT, T_MOUVEMENT, T_VIDANGE, T_CONTRAT, T_VISITE_TECHNIQUE]
    results = {}
    
    def fetch(table_name):
        try:
            response = supabase.table(table_name).select("*").execute()
            return table_name, pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception:
            # Table inexistante ou erreur → DataFrame vide
            return table_name, pd.DataFrame()
    
    with ThreadPoolExecutor(max_workers=6) as executor:
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

def upsert_visite_technique(matricule, marque, date_premiere_visite=None, date_prochaine_visite=None):
    """Crée ou met à jour une fiche de visite technique"""
    try:
        if date_premiere_visite is None:
            date_premiere_visite = datetime.now().strftime("%Y-%m-%d")
        if date_prochaine_visite is None:
            date_prochaine_visite = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
        
        response = supabase.table(T_VISITE_TECHNIQUE).select("Matricule").eq("Matricule", matricule).execute()
        
        if response.data and len(response.data) > 0:
            supabase.table(T_VISITE_TECHNIQUE).update({
                "Date_Prochaine_Visite": date_prochaine_visite,
                "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")
            }).eq("Matricule", matricule).execute()
        else:
            supabase.table(T_VISITE_TECHNIQUE).insert({
                "Matricule": matricule,
                "Marque": safe_str(marque).upper(),
                "Date_Premiere_Visite": date_premiere_visite,
                "Date_Prochaine_Visite": date_prochaine_visite,
                "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                "Statut": "Active"
            }).execute()
        return True
    except Exception as e:
        st.warning(f"Upsert visite technique échoué: {e}")
        return False

def transformer_reservation_en_contrat(num_contrat):
    try:
        df_mouvs = fetch_table_direct(T_MOUVEMENT)
        df_clients = fetch_table_direct(T_CLIENT)
        
        if df_mouvs.empty or MOUV_KEY_COLUMN not in df_mouvs.columns:
            return False, f"Colonne '{MOUV_KEY_COLUMN}' absente"
        
        row_matches = df_mouvs[df_mouvs[MOUV_KEY_COLUMN].astype(str).str.strip() == str(num_contrat).strip()]
        if row_matches.empty:
            return False, f"Contrat '{num_contrat}' introuvable"
        
        row = row_matches.iloc[0]
        statut_mouvement = safe_str(row.get('Statut_Mouvement', ''))
        
        if statut_mouvement and statut_mouvement != 'En cours':
            return False, f"Mouvement non actif (statut: {statut_mouvement})"
        
        ref_contrat = f"BBNH-{datetime.now().strftime('%d%m%H%M')}-{num_contrat}"
        
        cin_client = ""
        client_nom = safe_str(row.get('Client', ''))
        if not df_clients.empty and client_nom and 'Nom' in df_clients.columns:
            match_cli = df_clients[df_clients['Nom'].astype(str).str.strip() == client_nom.strip()]
            if not match_cli.empty:
                cin_client = safe_str(match_cli.iloc[0].get('CIN', ''))
        
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
            return False, "❌ Échec création contrat"
        
        ok_update = update_row(T_MOUVEMENT, {"Type_Statut": "Location"}, MOUV_KEY_COLUMN, num_contrat)
        
        if not ok_update:
            delete_row(T_CONTRAT, "Num_Contrat", ref_contrat)
            return False, "❌ Échec mise à jour mouvement"
        
        return True, f"✅ Transformé en contrat **{ref_contrat}**"
    except Exception as e:
        return False, f"❌ Erreur : {str(e)}"

# ============================================================
# CHARGEMENT DES DONNÉES
# ============================================================
if "force_reload" not in st.session_state:
    st.session_state["force_reload"] = False

if st.session_state["force_reload"]:
    get_all_tables.clear()
    st.session_state["force_reload"] = False

all_data = get_all_tables()
df_voitures = all_data[T_VEHICULE]
df_clients = all_data[T_CLIENT]
df_mouvs = all_data[T_MOUVEMENT]
df_vidanges = all_data[T_VIDANGE]
df_contrats = all_data[T_CONTRAT]
df_visites_tech = all_data[T_VISITE_TECHNIQUE]

# ============================================================
# 🆕 VÉRIFICATION ET INITIALISATION DE LA TABLE VISITE TECHNIQUE
# ============================================================
table_vt_existe = verifier_table_visite_technique()

if not table_vt_existe:
    st.warning("⚠️ La table **visite_technique** n'existe pas encore dans Supabase.")
    st.info("💡 Cliquez sur le bouton ci-dessous pour la créer automatiquement.")
    
    col_init1, col_init2 = st.columns(2)
    with col_init1:
        if st.button("🔧 CRÉER LA TABLE VISITE TECHNIQUE", use_container_width=True, type="primary"):
            with st.spinner("Création en cours..."):
                if creer_table_visite_technique():
                    st.success("✅ Table créée avec succès !")
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()
                else:
                    st.error("❌ Échec de création. Créez la table manuellement dans Supabase.")
                    st.code("""
                    -- SQL à exécuter dans Supabase SQL Editor :
                    CREATE TABLE visite_technique (
                        id BIGSERIAL PRIMARY KEY,
                        "Matricule" TEXT UNIQUE NOT NULL,
                        "Marque" TEXT,
                        "Date_Premiere_Visite" DATE,
                        "Date_Prochaine_Visite" DATE,
                        "Date_Mise_A_Jour" DATE,
                        "Statut" TEXT DEFAULT 'Active',
                        created_at TIMESTAMPTZ DEFAULT NOW()
                    );
                    """, language="sql")
    with col_init2:
        st.markdown("**📋 Colonnes requises :**")
        st.markdown("""
        - `Matricule` (TEXT, unique)
        - `Marque` (TEXT)
        - `Date_Premiere_Visite` (DATE)
        - `Date_Prochaine_Visite` (DATE)
        - `Date_Mise_A_Jour` (DATE)
        - `Statut` (TEXT)
        """)
    st.stop()

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

    if st.button("🔄 RAFRAÎCHIR LES DONNÉES", use_container_width=True):
        st.session_state["force_reload"] = True
        rerun()
    
    st.markdown("<h3 style='margin-bottom:10px;'>️ CONSOLE D'ACTION :</h3>", unsafe_allow_html=True)
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
# 📝 NOUVEAU CONTRAT
# ============================================================
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
    ref = st.sidebar.text_input("Code Contrat unique : ", f"BBNH-{datetime.now().strftime('%d%H%M%S')}")

    if st.sidebar.button("⚡ ENREGISTRER ON THE PLANNING"):
        try:
            if client_b == "-- Entrée manuelle --":
                nom_f, cin_f = nom_m, cin_m
            else:
                nom_f, cin_f = parse_client_label(client_b)
                if nom_m: nom_f = nom_m
                if cin_m: cin_f = cin_m

            if not vehicule or not vehicule.strip():
                st.error(" Le véhicule est obligatoire")
            elif not nom_f or not nom_f.strip():
                st.error(" Le nom du client est obligatoire")
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
                    MOUV_KEY_COLUMN: ref,
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
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()
                else:
                    st.error(" Échec de création du mouvement")
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            traceback.print_exc()

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
                    upsert_visite_technique(nouveau_matricule, nouvelle_marque)
                    st.success("✅ Véhicule enregistré !")
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()
            else:
                st.error("❌ Tous les champs obligatoires doivent être remplis")

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
                    delete_row(T_VISITE_TECHNIQUE, "Matricule", matricule_pure)
                    st.success("✅ Véhicule retiré.")
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()
    else:
        st.sidebar.info("Aucun véhicule dans la flotte.")

elif menu_action == "⚙️ Modifier un Dossier (Contrat/Réservation)":
    df_mouv_all = df_mouvs.copy() if not df_mouvs.empty else pd.DataFrame()

    if not df_mouv_all.empty and MOUV_KEY_COLUMN in df_mouv_all.columns:
        liste_mouv_mod = []
        key_map = {}
        for idx, r in df_mouv_all.iterrows():
            try:
                key_val = safe_str(r.get(MOUV_KEY_COLUMN, ''))
                if not key_val: continue
                mat = safe_str(r.get('Matricule', ''))
                cli = safe_str(r.get('Client', ''))
                statut = safe_str(r.get('Statut_Mouvement', ''))
                type_stat = safe_str(r.get('Type_Statut', ''))
                label = f"{key_val} | {mat} — {cli} [{type_stat} / {statut}]"
                liste_mouv_mod.append(label)
                key_map[label] = key_val
            except Exception: continue

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
            selected_key = key_map.get(mouv_selectionne, '')

            if selected_key:
                row_matches = df_mouv_all[df_mouv_all[MOUV_KEY_COLUMN].astype(str).str.strip() == selected_key.strip()]
                if not row_matches.empty:
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
                    try: init_time_deb = datetime.strptime(formater_heure_propre(row_init.get('Heure_Debut')), "%H:%M").time()
                    except: init_time_deb = time(9, 0)
                    try: init_time_fin = datetime.strptime(formater_heure_propre(row_init.get('Heure_Fin')), "%H:%M").time()
                    except: init_time_fin = time(12, 0)

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
                    try: idx_nature = nature_options.index(init_nature)
                    except: idx_nature = 0

                    idx_v_init = 0
                    if init_vehicule and init_vehicule in liste_vehicules_opt:
                        idx_v_init = liste_vehicules_opt.index(init_vehicule)

                    st.sidebar.markdown(f"### ⚙️ Édition : {selected_key}")
                    mod_nature = st.sidebar.selectbox("Nature : ", nature_options, index=idx_nature, key=f"mod_nature_{selected_key}")
                    mod_vehicule = st.sidebar.selectbox("Véhicule : ", liste_vehicules_opt if liste_vehicules_opt else [init_vehicule], index=idx_v_init, key=f"mod_veh_{selected_key}")

                    st.sidebar.markdown("👤 **Informations Conducteur**")
                    mod_client = st.sidebar.text_input("Nom & Prénom : ", value=init_client, key=f"mod_cli_{selected_key}")
                    mod_cin = st.sidebar.text_input("N° CIN : ", value=init_cin, key=f"mod_cin_{selected_key}")
                    mod_date_cin = st.sidebar.date_input("Date Délivrance CIN : ", init_date_cin, key=f"mod_dc_{selected_key}")
                    mod_permis = st.sidebar.text_input("N° Permis : ", value=init_permis, key=f"mod_perm_{selected_key}")
                    mod_date_permis = st.sidebar.date_input("Date Délivrance Permis : ", init_date_permis, key=f"mod_dp_{selected_key}")

                    st.sidebar.markdown("---")
                    c_d1, c_t1 = st.sidebar.columns(2)
                    with c_d1: mod_d1 = st.sidebar.date_input("Date Début : ", init_date_deb, key=f"mod_d1_{selected_key}")
                    with c_t1: mod_t1 = st.sidebar.time_input("Heure Début : ", init_time_deb, key=f"mod_t1_{selected_key}")
                    c_d2, c_t2 = st.sidebar.columns(2)
                    with c_d2: mod_d2 = st.sidebar.date_input("Date Fin : ", init_date_fin, key=f"mod_d2_{selected_key}")
                    with c_t2: mod_t2 = st.sidebar.time_input("Heure Fin : ", init_time_fin, key=f"mod_t2_{selected_key}")

                    mod_nbr_jours = max(1, (mod_d2 - mod_d1).days)
                    st.sidebar.markdown(f"**🔢 Durée :** `{mod_nbr_jours} jour(s)`")

                    init_jours_orig = max(1, (init_date_fin - init_date_deb).days)
                    init_prix_unit_calc = int(init_prix / init_jours_orig) if init_prix > 0 else 100
                    mod_prix_unitaire = st.sidebar.number_input("💰 Prix / Jour (DT) : ", min_value=0, value=init_prix_unit_calc if init_prix_unit_calc > 0 else 100, key=f"mod_pu_{selected_key}")
                    mod_prix = st.sidebar.number_input("Prix Total (DT) : ", value=int(mod_nbr_jours * mod_prix_unitaire), key=f"mod_tot_{selected_key}")
                    mod_caution = st.sidebar.number_input("Caution (DT) : ", value=int(init_caution), key=f"mod_cau_{selected_key}")
                    mod_reste = mod_prix - mod_caution
                    st.sidebar.markdown(f"** Reste :** `{mod_reste} DT`")

                    st.sidebar.markdown("---")
                    mod_lieu = st.sidebar.text_input("Lieu Réception : ", value=init_lieu, key=f"mod_lieu_{selected_key}")
                    mod_vol = st.sidebar.text_input("N° Vol : ", value=init_vol, key=f"mod_vol_{selected_key}")
                    mod_km_deb = st.sidebar.number_input("KM Départ : ", min_value=0, value=init_km_deb, key=f"mod_km_{selected_key}")
                    mod_note = st.sidebar.text_area("Note : ", value=init_note, key=f"mod_note_{selected_key}")

                    if st.sidebar.button("💾 ENREGISTRER LES MODIFICATIONS", key=f"mod_save_{selected_key}"):
                        try:
                            if mod_cin and mod_cin.strip():
                                if row_cli_init:
                                    update_row(T_CLIENT, {"Nom": mod_client, "Date Délivrance CIN": mod_date_cin.strftime("%Y-%m-%d"), "N° Permis": mod_permis, "Date Délivrance Permis": mod_date_permis.strftime("%Y-%m-%d")}, "CIN", mod_cin)
                                else:
                                    insert_row(T_CLIENT, {"Nom": mod_client, "CIN": mod_cin, "N° Permis": mod_permis, "Date Délivrance CIN": mod_date_cin.strftime("%Y-%m-%d"), "Date Délivrance Permis": mod_date_permis.strftime("%Y-%m-%d")})

                            ok_update = update_row(T_MOUVEMENT, {
                                "Matricule": mod_vehicule, "Type_Statut": mod_nature, "Client": mod_client,
                                "Date_Debut": mod_d1.strftime("%Y-%m-%d"), "Heure_Debut": mod_t1.strftime("%H:%M"),
                                "Date_Fin": mod_d2.strftime("%Y-%m-%d"), "Heure_Fin": mod_t2.strftime("%H:%M"),
                                "Prix": str(mod_prix), "Caution": str(mod_caution), "Reste": str(mod_reste),
                                "Lieu_Reception": mod_lieu, "No_Vol": mod_vol, "Info_Note": mod_note, "KM_Debut": int(mod_km_deb)
                            }, MOUV_KEY_COLUMN, selected_key)

                            if ok_update:
                                upsert_vidange(mod_vehicule, "", int(mod_km_deb))
                                st.sidebar.success("✅ Données mises à jour !")
                                get_all_tables.clear()
                                st.session_state["force_reload"] = True
                                rerun()
                            else:
                                st.sidebar.error("❌ Échec de la mise à jour")
                        except Exception as e:
                            st.sidebar.error(f"❌ Erreur : {e}")
    else:
        st.sidebar.info("📭 Aucun dossier enregistré.")

elif menu_action == "❌ Supprimer une opération":
    df_mouv_actifs = pd.DataFrame()
    if not df_mouvs.empty:
        if 'Statut_Mouvement' in df_mouvs.columns:
            df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        else:
            df_mouv_actifs = df_mouvs.copy()

    if not df_mouv_actifs.empty and MOUV_KEY_COLUMN in df_mouv_actifs.columns:
        liste_mouv_del = []
        key_map_del = {}
        for _, r in df_mouv_actifs.iterrows():
            try:
                key_val = safe_str(r.get(MOUV_KEY_COLUMN, ''))
                if not key_val: continue
                label = f"{key_val} | {safe_str(r.get('Matricule', ''))} — {safe_str(r.get('Client', ''))}"
                liste_mouv_del.append(label)
                key_map_del[label] = key_val
            except: continue

        if liste_mouv_del:
            with st.sidebar.form("form_bbnh_delete_mouv"):
                mouv_selectionne = st.selectbox("Choisir l'opération : ", liste_mouv_del)
                confirmer_action = st.checkbox("Confirmer la suppression")
                if st.form_submit_button("💥 RETIRER DU PLANNING"):
                    if confirmer_action:
                        key_to_delete = key_map_del.get(mouv_selectionne, '')
                        if key_to_delete:
                            delete_row(T_MOUVEMENT, MOUV_KEY_COLUMN, key_to_delete)
                            st.success("✅ Opération effacée !")
                            get_all_tables.clear()
                            st.session_state["force_reload"] = True
                            rerun()
    else:
        st.sidebar.info("Aucune opération à supprimer.")

elif menu_action == "🔄 Transformer Réservation → Contrat":
    st.sidebar.markdown("### 🔄 Transformer une Réservation en Contrat")
    df_mouvs_fresh = fetch_table_direct(T_MOUVEMENT)
    
    if not df_mouvs_fresh.empty:
        st.sidebar.markdown(f"**📊 Total mouvements :** `{len(df_mouvs_fresh)}`")
        if 'Type_Statut' in df_mouvs_fresh.columns:
            types = df_mouvs_fresh['Type_Statut'].dropna().unique().tolist()
            st.sidebar.markdown(f"**📋 Types :** {', '.join([str(t) for t in types])}")
    
    df_reservations = pd.DataFrame()
    if not df_mouvs_fresh.empty and 'Type_Statut' in df_mouvs_fresh.columns and MOUV_KEY_COLUMN in df_mouvs_fresh.columns:
        mask_resa = df_mouvs_fresh['Type_Statut'].astype(str).str.contains('reserv|resa|booking|réserv', case=False, na=False, regex=True)
        if 'Statut_Mouvement' in df_mouvs_fresh.columns:
            mask_actif = df_mouvs_fresh['Statut_Mouvement'] == 'En cours'
            df_reservations = df_mouvs_fresh[mask_resa & mask_actif].copy()
        else:
            df_reservations = df_mouvs_fresh[mask_resa].copy()
        
        if df_reservations.empty:
            st.sidebar.warning("⚠️ Aucune réservation. Affichage de TOUS les mouvements actifs.")
            if 'Statut_Mouvement' in df_mouvs_fresh.columns:
                df_reservations = df_mouvs_fresh[df_mouvs_fresh['Statut_Mouvement'] == 'En cours'].copy()
            else:
                df_reservations = df_mouvs_fresh.copy()
    
    if not df_reservations.empty and MOUV_KEY_COLUMN in df_reservations.columns:
        st.sidebar.success(f"✅ **{len(df_reservations)} mouvement(s)** à transformer")
        liste_resa = []
        key_map_resa = {}
        for _, r in df_reservations.iterrows():
            try:
                key_val = safe_str(r.get(MOUV_KEY_COLUMN, ''))
                if not key_val: continue
                mat = safe_str(r.get('Matricule', ''))
                cli = safe_str(r.get('Client', ''))
                d_deb = safe_str(r.get('Date_Debut', ''))
                d_fin = safe_str(r.get('Date_Fin', ''))
                type_stat = safe_str(r.get('Type_Statut', ''))
                label = f"{key_val} | {mat} — {cli} [{type_stat}] ({d_deb} → {d_fin})"
                liste_resa.append(label)
                key_map_resa[label] = key_val
            except: continue
        
        if liste_resa:
            with st.sidebar.form("form_transform_resa"):
                resa_selectionnee = st.selectbox("📋 Choisir le mouvement : ", liste_resa)
                confirmer_transformation = st.checkbox("⚠️ Je confirme la transformation")
                
                if st.form_submit_button("🔄 TRANSFORMER EN CONTRAT", use_container_width=True, type="primary"):
                    if confirmer_transformation:
                        key_resa = key_map_resa.get(resa_selectionnee, '')
                        if key_resa:
                            with st.spinner("Transformation..."):
                                ok, msg = transformer_reservation_en_contrat(key_resa)
                                if ok:
                                    st.success(msg)
                                    get_all_tables.clear()
                                    st.session_state["force_reload"] = True
                                    rerun()
                                else:
                                    st.error(msg)
    else:
        st.sidebar.error("🔴 Aucun mouvement trouvé.")

# ============================================================
# ESPACE CENTRAL
# ============================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION</h1>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    with c_search1: search_date_debut = st.date_input(" Date de Sortie : ", datetime.now(), key="adv_search_start")
    with c_search2: search_date_fin = st.date_input("📅 Date de Retour : ", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button(" Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        df_disponibles = df_voitures.copy() if not df_voitures.empty else pd.DataFrame()
        if not df_mouvs.empty and not df_disponibles.empty and 'Matricule' in df_disponibles.columns:
            matricules_indisponibles = set()
            for _, mv in df_mouvs.iterrows():
                if safe_str(mv.get('Statut_Mouvement')) != 'En cours': continue
                d_debut_mv = parse_date(mv.get('Date_Debut'))
                d_fin_mv = parse_date(mv.get('Date_Fin'))
                if d_debut_mv and d_fin_mv:
                    if not (d_fin_mv < search_date_debut or d_debut_mv > search_date_fin):
                        matricules_indisponibles.add(safe_str(mv.get('Matricule')))
            df_disponibles = df_disponibles[~df_disponibles['Matricule'].astype(str).str.strip().isin(matricules_indisponibles)]

        if not df_disponibles.empty:
            cols_aff = [c for c in ['Matricule', 'Marque', 'Modèle', 'Année'] if c in df_disponibles.columns]
            st.dataframe(df_disponibles[cols_aff], use_container_width=True, hide_index=True)
        else:
            st.warning("❌ Aucun véhicule disponible.")

st.markdown("<br>", unsafe_allow_html=True)

tab_planning, tab_logistique, tab_analytics, tab_vidange, tab_visite_tech, tab_crm, tab_admin = st.tabs([
    "🗓️ CORE PLANNING", "🔑 BOX RECEPTION", " PERFORMANCES", "🔧 VIDANGES", "🔍 VISITE TECHNIQUE", "👥 CRM", "⚙️ ADMIN"
])

with tab_planning:
    st.markdown("### 🗓️ Vue Globale")
    f_col_car, f_col_date_start, f_col_date_target = st.columns([2, 1.5, 1.5])
    with f_col_car:
        options_recherche_voiture = ["-- Toutes les voitures --"] + liste_vehicules_opt
        vehicule_recherche = st.selectbox("🚘 Filtrer par véhicule :", options_recherche_voiture)
    with f_col_date_start: date_base = st.date_input("Date de début :", datetime(2026, 1, 1), key="grid_bbnh_date")
    with f_col_date_target: recherche_date = st.date_input("📅 Focus date :", datetime(2026, 6, 26))

    array_jours = [date_base + timedelta(days=i) for i in range(365)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    df_voitures_valides = df_voitures[df_voitures['Matricule'].notna() & (df_voitures['Matricule'].astype(str).str.strip() != '')] if not df_voitures.empty else pd.DataFrame()

    if not df_voitures_valides.empty:
        build_matrix = []
        voiture_filter = vehicule_recherche != "-- Toutes les voitures --"
        for _, car in df_voitures_valides.iterrows():
            immat = safe_str(car.get('Matricule'))
            if voiture_filter and immat != vehicule_recherche: continue
            modele = safe_str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            ligne = {"Flotte BBNH": f" {modele} — [{immat}]"}
            for col_j in nom_colonnes: ligne[col_j] = "● Disponible"
            build_matrix.append(ligne)

        if build_matrix:
            df_final_grid = pd.DataFrame(build_matrix)
            suivi_jours = {}
            if not df_mouvs.empty:
                for _, mv in df_mouvs.iterrows():
                    m_v = safe_str(mv.get('Matricule'))
                    if not m_v: continue
                    d_debut_mv = parse_date(mv.get('Date_Debut'))
                    d_fin_mv = parse_date(mv.get('Date_Fin'))
                    if not (d_debut_mv and d_fin_mv): continue
                    s_v = safe_str(mv.get('Type_Statut')).lower()
                    client_v = safe_str(mv.get('Client'))
                    h_deb_label = formater_heure_propre(mv.get('Heure_Debut'))
                    h_fin_label = formater_heure_propre(mv.get('Heure_Fin'))
                    
                    current_day = d_debut_mv
                    while current_day <= d_fin_mv:
                        key_day = current_day.strftime("%d/%m")
                        if key_day not in suivi_jours: suivi_jours[m_v] = {}
                        if key_day not in suivi_jours[m_v]:
                            suivi_jours[m_v][key_day] = {"depart": False, "fin": False, "client_sortant": "", "client_entrant": "", "heure_sortie": "00:00", "heure_retour": "00:00", "desc": ""}
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
                                suivi_jours[m_v][key_day]["desc"] = f" [{h_deb_label}➔{h_fin_label}] {client_v}"
                            else:
                                suivi_jours[m_v][key_day]["desc"] = f"🟢 [{h_deb_label}➔{h_fin_label}] {client_v}"
                        current_day += timedelta(days=1)

            for idx, row in df_final_grid.iterrows():
                mat_extracted = row["Flotte BBNH"].split("[")[-1].replace("]", "").strip()
                if mat_extracted in suivi_jours:
                    for key_day, data in suivi_jours[mat_extracted].items():
                        if key_day in df_final_grid.columns:
                            if data["depart"] and data["fin"]:
                                df_final_grid.at[idx, key_day] = f"🔵 {data['heure_retour']} {data['client_entrant']} / 🛫{data['heure_sortie']} {data['client_sortant']}"
                            elif data["desc"]:
                                df_final_grid.at[idx, key_day] = data["desc"]

            def style_bbnh_theme(val):
                val_str = str(val)
                if "● Disponible" in val_str: return "background-color: #ffffff; color: #111827; font-size: 11px; font-weight: 600; text-align: center; border: 1px solid #e5e7eb;"
                elif "" in val_str: return "background-color: #1d4ed8; color: #ffffff; font-weight: 700; font-size: 10px; border: 2px solid #60a5fa;"
                elif "🛠️" in val_str: return "background-color: #eab308; color: #1e1b4b; font-weight: 700; font-size: 11px;"
                elif "🔴" in val_str: return "background-color: #dc2626; color: #ffffff; font-weight: 600; font-size: 11px;"
                elif "🟢" in val_str: return "background-color: #16a34a; color: #ffffff; font-weight: 600; font-size: 11px;"
                return "background-color: #090b0e; color: #ffffff; font-weight: 700; font-size: 12px; border-right: 3px solid #e60000;"

            target_col_str = recherche_date.strftime("%d/%m")
            cols_ordonnees = ['Flotte BBNH']
            if target_col_str in nom_colonnes:
                idx_target = nom_colonnes.index(target_col_str)
                cols_ordonnees += nom_colonnes[max(0, idx_target - 2):min(365, idx_target + 12)]

            styled_df = df_final_grid[cols_ordonnees].style
            styled_df = style_apply(styled_df, style_bbnh_theme, subset=[c for c in cols_ordonnees if c != 'Flotte BBNH'])
            st.dataframe(styled_df, use_container_width=True, height=800)

with tab_logistique:
    st.markdown("###  Terminal de Restitution")
    df_actifs = pd.DataFrame()
    if not df_mouvs.empty:
        if 'Statut_Mouvement' in df_mouvs.columns:
            df_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        else:
            df_actifs = df_mouvs.copy()

    if not df_actifs.empty and MOUV_KEY_COLUMN in df_actifs.columns:
        choix_actifs = []
        key_map_retour = {}
        for _, r in df_actifs.iterrows():
            try:
                key_val = safe_str(r.get(MOUV_KEY_COLUMN, ''))
                if not key_val: continue
                type_stat = safe_str(r.get('Type_Statut', ''))
                label = f"{key_val} | {safe_str(r.get('Matricule', ''))} — {safe_str(r.get('Client', ''))} [{type_stat}]"
                choix_actifs.append(label)
                key_map_retour[label] = key_val
            except: continue

        if choix_actifs:
            col_list, col_details = st.columns([1, 1])
            with col_list:
                target_v = st.selectbox("Sélectionner le véhicule rentrant : ", choix_actifs)
                d_reel = st.date_input("Date de retour : ", datetime.now())
                t_reel = st.time_input("Heure de retour : ", datetime.now().time())
                l_retour = st.text_input("Lieu de retour : ", value="Siège Monastir")
                key_mouv_temp = key_map_retour.get(target_v, '')
                res_dep = df_actifs[df_actifs[MOUV_KEY_COLUMN].astype(str).str.strip() == key_mouv_temp.strip()] if key_mouv_temp else pd.DataFrame()
                km_dep_de_base = safe_int(res_dep.iloc[0].get('KM_Debut')) if not res_dep.empty else 0
                km_fin = st.number_input("Kilométrage au Retour : ", min_value=km_dep_de_base, value=km_dep_de_base, step=1)

                if st.button("✅ VALIDATION DU RETOUR", use_container_width=True):
                    if key_mouv_temp:
                        try:
                            vehicule_rentre = safe_str(res_dep.iloc[0].get('Matricule')) if not res_dep.empty else ''
                            update_row(T_MOUVEMENT, {"Statut_Mouvement": "Retourné", "Date_Fin": d_reel.strftime("%Y-%m-%d"), "Heure_Fin": t_reel.strftime("%H:%M"), "Lieu_Reception": l_retour, "KM_Fin": int(km_fin)}, MOUV_KEY_COLUMN, key_mouv_temp)
                            upsert_vidange(vehicule_rentre, "", int(km_fin))
                            st.success("✅ Retour validé !")
                            get_all_tables.clear()
                            st.session_state["force_reload"] = True
                            rerun()
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
            with col_details:
                if not res_dep.empty:
                    row_sel = res_dep.iloc[0]
                    diff_km = int(km_fin) - int(km_dep_de_base)
                    st.markdown(f"** Distance :** <span style='color:#4ade80; font-weight:bold; font-size:22px;'>{diff_km} KM</span>", unsafe_allow_html=True)
                    st.write(f"**Reste dû :** {row_sel.get('Reste', '0')} DT")
    else:
        st.info("Aucun déplacement en cours.")

with tab_analytics:
    st.markdown("### 📊 Chiffre d'Affaires du Jour")
    day_target = st.date_input("Journée d'analyse :", datetime.now())
    if not df_mouvs.empty:
        df_stats = df_mouvs.copy()
        df_stats['Clean_D'] = pd.to_datetime(df_stats['Date_Debut'], errors='coerce').dt.date
        df_stats['Clean_F'] = pd.to_datetime(df_stats['Date_Fin'], errors='coerce').dt.date
        df_stats['Val_Prix'] = df_stats['Prix'].apply(safe_float)
        sorties = df_stats[df_stats['Clean_D'] == day_target]
        entrees = df_stats[df_stats['Clean_F'] == day_target]
        k1, k2, k3 = st.columns(3)
        with k1: st.metric("📈 DÉPARTS", f"{len(sorties)}")
        with k2: st.metric("🔑 RETOURS", f"{len(entrees)}")
        with k3: st.metric(" CA", f"{sorties['Val_Prix'].sum():,.2f} DT")

with tab_vidange:
    st.markdown("### 🔧 Suivi des Vidanges")
    if not df_vidanges.empty:
        df_v = df_vidanges.copy()
        df_v['KM_Dernier_Vidange'] = pd.to_numeric(df_v['KM_Dernier_Vidange'], errors='coerce').fillna(0).astype(int)
        df_v['KM_Recent'] = pd.to_numeric(df_v['KM_Recent'], errors='coerce').fillna(0).astype(int)
        df_v['KM cerculer'] = df_v['KM_Recent'] - df_v['KM_Dernier_Vidange']
        df_v['km restant'] = 9000 - df_v['KM cerculer']

        alertes = df_v[df_v['km restant'] <= 1500]
        if not alertes.empty:
            st.error(f"⚠️ **ALERTE :** {len(alertes)} véhicule(s) à vidanger !")
        else:
            st.success("✅ Aucune vidange urgente.")

        cols_aff = [c for c in ['Marque', 'Matricule', 'Date_Dernier_Vidange', 'KM_Dernier_Vidange', 'KM_Recent', 'KM cerculer', 'km restant'] if c in df_v.columns]
        st.dataframe(df_v[cols_aff], use_container_width=True, hide_index=True)

        with st.container(border=True):
            if 'Matricule' in df_v.columns:
                v_select = st.selectbox("Véhicule : ", df_v['Matricule'].tolist())
                v_info = df_v[df_v['Matricule'] == v_select].iloc[0]
                c1, c2 = st.columns(2)
                with c1: nouveau_km = st.number_input("KM Actuel : ", min_value=0, value=safe_int(v_info.get('KM_Recent')), step=1)
                with c2: action_sync = st.checkbox("Vidange effectuée aujourd'hui", value=False)
                
                if st.button("💾 ENREGISTRER", use_container_width=True):
                    if action_sync:
                        update_row(T_VIDANGE, {"KM_Recent": int(nouveau_km), "KM_Dernier_Vidange": int(nouveau_km), "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"), "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")}, "Matricule", v_select)
                    else:
                        update_row(T_VIDANGE, {"KM_Recent": int(nouveau_km), "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")}, "Matricule", v_select)
                    st.success("✅ Mis à jour !")
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()

# ============================================================
# 🆕 TAB VISITE TECHNIQUE - VERSION CORRIGÉE
# ============================================================
with tab_visite_tech:
    st.markdown("###  Tableau de Bord des Visites Techniques")
    
    # Recharger les données fraîches pour ce module
    df_vt_fresh = fetch_table_direct(T_VISITE_TECHNIQUE)
    
    if df_vt_fresh.empty:
        st.info("📭 Aucune visite technique enregistrée.")
        st.markdown("💡 Les visites techniques sont créées automatiquement lors de l'ajout de véhicules.")
        
        # Bouton pour initialiser tous les véhicules
        if not df_voitures.empty and 'Matricule' in df_voitures.columns:
            st.markdown("---")
            st.markdown("#### 🚀 Initialiser les visites techniques pour toute la flotte")
            if st.button("⚡ CRÉER LES FICHES POUR TOUS LES VÉHICULES", use_container_width=True, type="primary"):
                count = 0
                for _, v in df_voitures.iterrows():
                    mat = safe_str(v.get('Matricule', ''))
                    marque = safe_str(v.get('Marque', ''))
                    if mat:
                        if upsert_visite_technique(mat, marque):
                            count += 1
                st.success(f"✅ {count} fiche(s) créée(s) !")
                get_all_tables.clear()
                st.session_state["force_reload"] = True
                rerun()
    else:
        df_vt = df_vt_fresh.copy()
        
        # Calcul des jours restants
        df_vt['Date_Prochaine_Visite_dt'] = pd.to_datetime(df_vt['Date_Prochaine_Visite'], errors='coerce')
        df_vt['Jours_Restants'] = (df_vt['Date_Prochaine_Visite_dt'] - pd.Timestamp(datetime.now())).dt.days
        
        # 🆕 ALERTES 15 jours
        alertes_15 = df_vt[df_vt['Jours_Restants'] <= 15]
        
        if not alertes_15.empty:
            st.error(f"⚠️ **ALERTE VISITE TECHNIQUE :** {len(alertes_15)} véhicule(s) dans les 15 jours !")
            cols_alerte = [c for c in ['Matricule', 'Marque', 'Date_Prochaine_Visite', 'Jours_Restants'] if c in alertes_15.columns]
            st.dataframe(alertes_15[cols_alerte], use_container_width=True)
        else:
            st.success("✅ Aucune visite technique urgente.")
        
        # Tableau complet
        cols_aff = [c for c in ['Marque', 'Matricule', 'Date_Premiere_Visite', 'Date_Prochaine_Visite', 'Jours_Restants', 'Statut'] if c in df_vt.columns]
        df_tableau = df_vt[cols_aff].copy()
        
        def colorer_vt(row):
            try:
                jours = row.get('Jours_Restants', 999)
                if pd.isna(jours): jours = 999
                jours = int(jours)
                if jours <= 0:
                    return ['background-color: #dc2626; color: white; font-weight: bold;'] * len(row)
                elif jours <= 15:
                    return ['background-color: #f97316; color: white; font-weight: bold;'] * len(row)
                elif jours <= 30:
                    return ['background-color: #eab308; color: black; font-weight: bold;'] * len(row)
                return ['background-color: #16a34a; color: white;'] * len(row)
            except:
                return [''] * len(row)
        
        styled = df_tableau.style.apply(colorer_vt, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Formulaire de mise à jour
        with st.container(border=True):
            st.markdown("#### 📝 Mettre à jour une visite technique")
            if 'Matricule' in df_vt.columns:
                c1, c2, c3 = st.columns([1.5, 1.5, 2])
                with c1:
                    vt_select = st.selectbox("Véhicule : ", df_vt['Matricule'].tolist())
                    vt_info = df_vt[df_vt['Matricule'] == vt_select].iloc[0]
                    init_prem = parse_date(vt_info.get('Date_Premiere_Visite')) or datetime.now().date()
                    prem_visite = st.date_input("Première Visite : ", value=init_prem)
                with c2:
                    init_proch = parse_date(vt_info.get('Date_Prochaine_Visite')) or (datetime.now() + timedelta(days=365)).date()
                    proch_visite = st.date_input("Prochaine Visite : ", value=init_proch)
                with c3:
                    action_visite = st.checkbox("✅ Visite effectuée aujourd'hui (prochaine dans 1 an)", value=False)
                
                if st.button("💾 ENREGISTRER LA VISITE", use_container_width=True):
                    if action_visite:
                        prochaine_str = (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d")
                    else:
                        prochaine_str = proch_visite.strftime("%Y-%m-%d")
                    
                    marque_veh = safe_str(df_voitures[df_voitures['Matricule'] == vt_select].iloc[0].get('Marque', '')) if not df_voitures.empty else ''
                    
                    update_row(T_VISITE_TECHNIQUE, {
                        "Date_Premiere_Visite": prem_visite.strftime("%Y-%m-%d"),
                        "Date_Prochaine_Visite": prochaine_str,
                        "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                        "Marque": marque_veh.upper()
                    }, "Matricule", vt_select)
                    
                    st.success("✅ Visite technique enregistrée !")
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()

with tab_crm:
    st.markdown("### 👥 Gestion des Clients")
    c1, c2 = st.columns([5, 4])
    with c1:
        search_query = st.text_input("Rechercher (Nom, CIN) : ", key="crm_search")
        if search_query and not df_clients.empty:
            mask = df_clients['Nom'].str.contains(search_query, case=False, na=False)
            if 'CIN' in df_clients.columns:
                mask = mask | df_clients['CIN'].str.contains(search_query, case=False, na=False)
            clients_trouves = df_clients[mask]
            if not clients_trouves.empty:
                for idx, cli in clients_trouves.iterrows():
                    cin = safe_str(cli.get('CIN'))
                    with st.expander(f"👤 {safe_str(cli.get('Nom'))} (CIN: {cin})"):
                        st.write(f"**Tél :** {cli.get('Numéro de téléphone', 'N/A')}")
                        if st.button(f"🗑️ Supprimer", key=f"del_{idx}_{cin}"):
                            delete_row(T_CLIENT, "CIN", cin)
                            st.success("✅ Supprimé")
                            get_all_tables.clear()
                            st.session_state["force_reload"] = True
                            rerun()
    with c2:
        st.markdown("#### ➕ Nouveau Client")
        with st.form("form_new_client"):
            n_nom = st.text_input("Nom *")
            n_cin = st.text_input("CIN *")
            n_tel = st.text_input("Téléphone")
            if st.form_submit_button("⚡ CRÉER"):
                if n_nom and n_cin:
                    insert_row(T_CLIENT, {"Nom": n_nom, "CIN": n_cin, "Numéro de téléphone": n_tel})
                    st.success("✅ Client créé !")
                    get_all_tables.clear()
                    st.session_state["force_reload"] = True
                    rerun()

with tab_admin:
    st.markdown("### ⚙️ Administration")
    st.warning("⚠️ Actions irréversibles")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🗑️ PURGER MOUVEMENTS"):
            if st.checkbox("Confirmer", key="chk_purge_mouv"):
                delete_all(T_MOUVEMENT)
                st.success("✅ Purge effectuée")
                get_all_tables.clear()
                st.session_state["force_reload"] = True
                rerun()
    with col_a2:
        if st.button("🗑️ PURGER CLIENTS"):
            if st.checkbox("Confirmer", key="chk_purge_cli"):
                delete_all(T_CLIENT)
                st.success("✅ Purge effectuée")
                get_all_tables.clear()
                st.session_state["force_reload"] = True
                rerun()
