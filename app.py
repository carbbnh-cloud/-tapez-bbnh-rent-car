import streamlit as st
import pandas as pd
from supabase import create_client
import os
import base64
from datetime import datetime, timedelta, time
import traceback

# --- Compatibilité Streamlit ---
if hasattr(st, "rerun"):
    rerun = st.rerun
elif hasattr(st, "experimental_rerun"):
    rerun = st.experimental_rerun
else:
    def rerun(): pass

# --- CONFIGURATION PAGE ---
st.set_page_config(
    page_title="BBNH OS — Planning 365 Jours",
    layout="wide",
    page_icon="️",
    initial_sidebar_state="expanded"
)

# --- CSS ---
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
.car-plate { font-weight: bold; color: #333; }
.contract-num { font-weight: 800; font-size: 16px; color: #e60000; }
.status-badge {
    padding: 4px 10px; border-radius: 20px; font-weight: bold;
    font-size: 11px; text-transform: uppercase;
}
.status-paid { background-color: #e6f7ed; color: #28a745; border: 1px solid #28a745; }
.status-pending { background-color: #fff4e6; color: #fd7e14; border: 1px solid #fd7e14; }
.km-value { font-weight: bold; margin-bottom: 2px; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SUPABASE
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

# ============================================================
# CACHE SESSION STATE
# ============================================================
def load_all_data(force=False):
    if not force and st.session_state.get('data_loaded', False):
        return
    
    try:
        with st.spinner("Chargement des données..."):
            r1 = supabase.table(T_VEHICULE).select("*").execute()
            r2 = supabase.table(T_CLIENT).select("*").execute()
            r3 = supabase.table(T_MOUVEMENT).select("*").execute()
            r4 = supabase.table(T_VIDANGE).select("*").execute()
            r5 = supabase.table(T_CONTRAT).select("*").execute()
            
            st.session_state['df_voitures'] = pd.DataFrame(r1.data) if r1.data else pd.DataFrame()
            st.session_state['df_clients'] = pd.DataFrame(r2.data) if r2.data else pd.DataFrame()
            st.session_state['df_mouvs'] = pd.DataFrame(r3.data) if r3.data else pd.DataFrame()
            st.session_state['df_vidanges'] = pd.DataFrame(r4.data) if r4.data else pd.DataFrame()
            st.session_state['df_contrats'] = pd.DataFrame(r5.data) if r5.data else pd.DataFrame()
            st.session_state['data_loaded'] = True
    except Exception as e:
        st.error(f"Erreur chargement: {e}")

def refresh_data():
    st.session_state['data_loaded'] = False
    load_all_data(force=True)

load_all_data()

df_voitures = st.session_state.get('df_voitures', pd.DataFrame())
df_clients = st.session_state.get('df_clients', pd.DataFrame())
df_mouvs = st.session_state.get('df_mouvs', pd.DataFrame())
df_vidanges = st.session_state.get('df_vidanges', pd.DataFrame())
df_contrats = st.session_state.get('df_contrats', pd.DataFrame())

# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================
def safe_str(val, default=""):
    if val is None: return default
    if isinstance(val, float) and pd.isna(val): return default
    s = str(val).strip()
    if s.lower() in ('nan', 'none', ''): return default
    return s

def safe_int(val, default=0):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)): return default
        return int(float(str(val).replace(' ', '').replace(',', '.')))
    except: return default

def safe_float(val, default=0.0):
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)): return default
        return float(str(val).replace(' ', '').replace(',', '.'))
    except: return default

def encoder_image_base64(file_buffer):
    if file_buffer is None: return ""
    try: return base64.b64encode(file_buffer.getvalue()).decode()
    except: return ""

def formater_heure_propre(valeur):
    if valeur is None or (isinstance(valeur, float) and pd.isna(valeur)): return '00:00'
    if isinstance(valeur, (datetime, time)): return valeur.strftime('%H:%M')
    val_str = safe_str(valeur, '00:00')
    if " " in val_str:
        try: val_str = val_str.split(" ")[1]
        except: pass
    parts = val_str.split(":")
    if len(parts) >= 2: return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return '00:00'

def parse_date(val):
    if val is None: return None
    if isinstance(val, datetime): return val.date() if hasattr(val, 'date') else val
    if hasattr(val, 'date') and callable(val.date):
        try: return val.date()
        except: pass
    s = safe_str(val)
    if not s: return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try: return datetime.strptime(s, fmt).date()
        except: pass
    try: return pd.to_datetime(s).date()
    except: return None

# ============================================================
# FONCTIONS DATABASE
# ============================================================
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
        try: supabase.table(table_name).delete().neq("id", 0).execute()
        except:
            try: supabase.table(table_name).delete().gte("id", 0).execute()
            except:
                df = pd.DataFrame(supabase.table(table_name).select("id").execute().data or [])
                if not df.empty:
                    for id_val in df['id'].tolist():
                        try: supabase.table(table_name).delete().eq("id", id_val).execute()
                        except: pass
        return True
    except Exception as e:
        st.error(f"Erreur delete all: {e}")
        return False

def upsert_vidange(matricule, marque, km_recent=0):
    try:
        df_v = df_vidanges
        if not df_v.empty and 'Matricule' in df_v.columns:
            existing = df_v[df_v['Matricule'].astype(str).str.strip() == str(matricule).strip()]
            if not existing.empty:
                return update_row(T_VIDANGE, {
                    "KM_Recent": int(km_recent),
                    "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")
                }, "Matricule", matricule)
        return insert_row(T_VIDANGE, {
            "Matricule": matricule, "Marque": safe_str(marque).upper(),
            "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
            "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
            "KM_Dernier_Vidange": 0, "KM_Recent": int(km_recent)
        })
    except Exception as e:
        st.warning(f"Upsert vidange: {e}")
        return False

# ============================================================
# LISTES
# ============================================================
@st.cache_data(show_spinner=False)
def build_liste_clients(_df_clients):
    opts = ["-- Entrée manuelle --"]
    if not _df_clients.empty and 'Nom' in _df_clients.columns:
        for _, row in _df_clients.iterrows():
            nom = safe_str(row.get('Nom', ''))
            prenom = safe_str(row.get('Prénom', ''))
            cin = safe_str(row.get('CIN', ''))
            if nom: opts.append(f"{nom.upper()} {prenom} (CIN: {cin})")
    return opts

@st.cache_data(show_spinner=False)
def build_liste_vehicules(_df_voitures):
    if _df_voitures.empty or 'Matricule' not in _df_voitures.columns: return []
    return [safe_str(r.get('Matricule')) for _, r in _df_voitures.iterrows() if safe_str(r.get('Matricule'))]

@st.cache_data(show_spinner=False)
def build_liste_vehicules_complets(_df_voitures):
    if _df_voitures.empty or 'Matricule' not in _df_voitures.columns: return []
    res = []
    for _, r in _df_voitures.iterrows():
        mat = safe_str(r.get('Matricule'))
        modele = safe_str(r.get('Modèle', r.get('Marque', 'Voiture')))
        if mat: res.append(f"{mat} — {modele}")
    return res

liste_clients_opt = build_liste_clients(df_clients)
liste_vehicules_opt = build_liste_vehicules(df_voitures)
liste_vehicules_complets_opt = build_liste_vehicules_complets(df_voitures)

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
        " Supprimer une opération"
    ], label_visibility="collapsed")

    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    if st.button("🔄 Rafraîchir les données", use_container_width=True):
        refresh_data()
        rerun()

# ============================================================
# FORMULAIRES SIDEBAR
# ============================================================
if menu_action == "📝 Nouveau Contrat / Réservation":
    st.sidebar.markdown("📝 Éditer une nouvelle fiche")
    nature = st.sidebar.selectbox("Nature : ", ["Contrat Location", "Réservation", "Maintenance / Garage"])
    vehicule = st.sidebar.selectbox("Véhicule : ", liste_vehicules_opt) if liste_vehicules_opt else st.sidebar.text_input("Véhicule : ")
    client_b = st.sidebar.selectbox("Client : ", liste_clients_opt)

    nom_m = st.sidebar.text_input("Nom & Prénom (Manuel) : ")
    cin_m = st.sidebar.text_input("N° C.I.N (Manuel) : ")
    dc_m = st.sidebar.date_input("Date Délivrance CIN : ", datetime.now() - timedelta(days=365))
    permis_m = st.sidebar.text_input("N° Permis (Manuel) : ")
    dp_m = st.sidebar.date_input("Date Délivrance Permis : ", datetime.now() - timedelta(days=365))

    f_cin = st.sidebar.file_uploader("Fichier CIN : ", type=["png", "jpg", "jpeg", "pdf"])
    f_permis = st.sidebar.file_uploader("Fichier Permis : ", type=["png", "jpg", "jpeg", "pdf"])

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

    if st.sidebar.button(" ENREGISTRER ON THE PLANNING"):
        try:
            nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[0]
            cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "").strip()
            str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
            str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
            text_type = "Location" if "Contrat" in nature else nature

            img_cin_b64 = encoder_image_base64(f_cin)
            img_permis_b64 = encoder_image_base64(f_permis)

            if client_b == "-- Entrée manuelle --" and cin_f:
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
                st.success("✅ Fiche créée avec succès !")
                refresh_data()
                rerun()
            else:
                st.error("❌ Échec de création")
        except Exception as e:
            st.error(f"❌ Erreur : {e}")
            traceback.print_exc()

elif menu_action == "🚗 Ajouter un Véhicule à la Flotte":
    with st.sidebar.form("form_bbnh_add_car"):
        st.markdown("###  Nouveau Véhicule")
        nouveau_matricule = st.text_input("Matricule / Plaque * : ").strip()
        nouvelle_marque = st.text_input("Marque * : ").strip()
        nouveau_modele = st.text_input("Modèle * : ").strip()
        nouvelle_annee = st.text_input("Année : ", value="2026").strip()

        if st.form_submit_button(" ENREGISTRER LE VEHICULE"):
            if nouveau_matricule and nouvelle_marque and nouveau_modele:
                ok_v = insert_row(T_VEHICULE, {
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque,
                    "Modèle": nouveau_modele, "Année": nouvelle_annee,
                    "Marque/Model": f"{nouvelle_marque} {nouveau_modele}"
                })
                if ok_v:
                    upsert_vidange(nouveau_matricule, nouvelle_marque, 0)
                    st.success("✅ Véhicule enregistré !")
                    refresh_data()
                    rerun()
            else:
                st.error("❌ Tous les champs obligatoires doivent être remplis")

elif menu_action == "️ Supprimer un Véhicule de la Flotte":
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
                    refresh_data()
                    rerun()
    else:
        st.sidebar.info("Aucun véhicule dans la flotte.")

elif menu_action == "️ Modifier un Dossier (Contrat/Réservation)":
    df_mouv_actifs = pd.DataFrame()
    if not df_mouvs.empty:
        if 'Statut_Mouvement' in df_mouvs.columns:
            df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        else:
            df_mouv_actifs = df_mouvs.copy()

    if not df_mouv_actifs.empty and 'id' in df_mouv_actifs.columns:
        liste_mouv_mod = [f"ID: {r.get('id')} | {r.get('Matricule', '')} — {r.get('Client', '')}"
                         for _, r in df_mouv_actifs.iterrows()]
        mouv_selectionne = st.sidebar.selectbox("Sélectionner le dossier à éditer :", liste_mouv_mod)

        selected_id = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
        row_init = df_mouv_actifs[df_mouv_actifs['id'] == selected_id].iloc[0]

        df_cli_spec = df_clients[df_clients['Nom'] == str(row_init.get('Client', ''))] if not df_clients.empty else pd.DataFrame()
        row_cli_init = df_cli_spec.iloc[0] if not df_cli_spec.empty else {}

        init_date_deb = parse_date(row_init.get('Date_Debut')) or datetime.now().date()
        init_date_fin = parse_date(row_init.get('Date_Fin')) or datetime.now().date()
        init_time_deb = datetime.strptime(formater_heure_propre(row_init.get('Heure_Debut')), "%H:%M").time()
        init_time_fin = datetime.strptime(formater_heure_propre(row_init.get('Heure_Fin')), "%H:%M").time()
        init_date_cin = parse_date(row_cli_init.get('Date Délivrance CIN')) or datetime.now().date()
        init_date_permis = parse_date(row_cli_init.get('Date Délivrance Permis')) or datetime.now().date()

        st.sidebar.markdown(f"### ⚙️ Édition Dossier #{selected_id}")
        mod_nature = st.sidebar.selectbox("Nature : ", ["Location", "Réservation", "Maintenance / Garage"])
        idx_v_init = liste_vehicules_opt.index(safe_str(row_init.get('Matricule'))) if safe_str(row_init.get('Matricule')) in liste_vehicules_opt else 0
        mod_vehicule = st.sidebar.selectbox("Véhicule : ", liste_vehicules_opt, index=idx_v_init)

        st.sidebar.markdown("👤 **Informations Conducteur**")
        mod_client = st.sidebar.text_input("Nom & Prénom : ", value=safe_str(row_init.get('Client')))
        mod_cin = st.sidebar.text_input("N° CIN : ", value=safe_str(row_cli_init.get('CIN')))
        mod_date_cin = st.sidebar.date_input("Date Délivrance CIN : ", init_date_cin)
        mod_permis = st.sidebar.text_input("N° Permis : ", value=safe_str(row_cli_init.get('N° Permis')))
        mod_date_permis = st.sidebar.date_input("Date Délivrance Permis : ", init_date_permis)

        st.sidebar.markdown("---")
        c_d1, c_t1 = st.sidebar.columns(2)
        with c_d1: mod_d1 = st.sidebar.date_input("Date Début : ", init_date_deb, key="mod_d1")
        with c_t1: mod_t1 = st.sidebar.time_input("Heure Début : ", init_time_deb, key="mod_t1")
        c_d2, c_t2 = st.sidebar.columns(2)
        with c_d2: mod_d2 = st.sidebar.date_input("Date Fin : ", init_date_fin, key="mod_d2")
        with c_t2: mod_t2 = st.sidebar.time_input("Heure Fin : ", init_time_fin, key="mod_t2")

        mod_nbr_jours = max(1, (mod_d2 - mod_d1).days)
        st.sidebar.markdown(f"**🔢 Durée :** `{mod_nbr_jours} jour(s)`")

        mod_prix_unitaire = st.sidebar.number_input("💰 Prix / Jour (DT) : ", min_value=0, value=100, key="mod_pu")
        mod_prix = st.sidebar.number_input("Prix Total (DT) : ", value=int(mod_nbr_jours * mod_prix_unitaire), key="mod_tot")
        mod_caution = st.sidebar.number_input("Caution (DT) : ", value=0, key="mod_cau")
        mod_reste = mod_prix - mod_caution
        st.sidebar.markdown(f"**🔴 Reste :** `{mod_reste} DT`")

        st.sidebar.markdown("---")
        mod_lieu = st.sidebar.text_input("Lieu Réception : ", value=safe_str(row_init.get('Lieu_Reception', 'Siège Monastir')))
        mod_vol = st.sidebar.text_input("N° Vol : ", value=safe_str(row_init.get('No_Vol')))
        mod_km_deb = st.sidebar.number_input("KM Départ : ", min_value=0, value=safe_int(row_init.get('KM_Debut')))
        mod_note = st.sidebar.text_area("Note : ", value=safe_str(row_init.get('Info_Note')))

        if st.sidebar.button("💾 ENREGISTRER LES MODIFICATIONS"):
            try:
                str_mod_d1, str_mod_d2 = mod_d1.strftime("%Y-%m-%d"), mod_d2.strftime("%Y-%m-%d")
                str_mod_t1, str_mod_t2 = mod_t1.strftime("%H:%M"), mod_t2.strftime("%H:%M")

                if mod_cin:
                    update_row(T_CLIENT, {
                        "Nom": mod_client, "Date Délivrance CIN": mod_date_cin.strftime("%Y-%m-%d"),
                        "N° Permis": mod_permis, "Date Délivrance Permis": mod_date_permis.strftime("%Y-%m-%d")
                    }, "CIN", mod_cin)

                update_row(T_MOUVEMENT, {
                    "Matricule": mod_vehicule, "Type_Statut": mod_nature, "Client": mod_client,
                    "Date_Debut": str_mod_d1, "Heure_Debut": str_mod_t1,
                    "Date_Fin": str_mod_d2, "Heure_Fin": str_mod_t2,
                    "Prix": str(mod_prix), "Caution": str(mod_caution), "Reste": str(mod_reste),
                    "Lieu_Reception": mod_lieu, "No_Vol": mod_vol, "Info_Note": mod_note,
                    "KM_Debut": int(mod_km_deb)
                }, "id", int(selected_id))

                upsert_vidange(mod_vehicule, "", int(mod_km_deb))
                st.success("✅ Données mises à jour !")
                refresh_data()
                rerun()
            except Exception as e:
                st.error(f"❌ Erreur : {e}")
    else:
        st.sidebar.info("Aucun dossier actif à modifier.")

elif menu_action == " Supprimer une opération":
    df_mouv_actifs = pd.DataFrame()
    if not df_mouvs.empty:
        if 'Statut_Mouvement' in df_mouvs.columns:
            df_mouv_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']
        else:
            df_mouv_actifs = df_mouvs.copy()

    if not df_mouv_actifs.empty and 'id' in df_mouv_actifs.columns:
        liste_mouv_del = [f"ID: {r.get('id')} | {r.get('Matricule', '')} — {r.get('Client', '')}"
                         for _, r in df_mouv_actifs.iterrows()]
        with st.sidebar.form("form_bbnh_delete_mouv"):
            mouv_selectionne = st.selectbox("Choisir l'opération : ", liste_mouv_del)
            confirmer_action = st.checkbox("Confirmer la suppression")
            if st.form_submit_button("💥 RETIRER DU PLANNING"):
                if confirmer_action:
                    id_to_delete = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
                    delete_row(T_MOUVEMENT, "id", id_to_delete)
                    st.success("✅ Opération effacée !")
                    refresh_data()
                    rerun()
    else:
        st.sidebar.info("Aucune opération à supprimer.")

# ============================================================
# ESPACE CENTRAL
# ============================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION - PLANNING ANNUEL</h1>", unsafe_allow_html=True)

# Recherche avancée
with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    with c_search1: search_date_debut = st.date_input("📅 Date de Sortie : ", datetime.now(), key="adv_search_start")
    with c_search2: search_date_fin = st.date_input("📅 Date de Retour : ", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")

        df_disponibles = df_voitures.copy() if not df_voitures.empty else pd.DataFrame()
        if not df_mouvs.empty and not df_disponibles.empty and 'Matricule' in df_disponibles.columns:
            df_mouvs_en_cours = df_mouvs[df_mouvs.get('Statut_Mouvement', pd.Series()) == 'En cours'].copy()
            if not df_mouvs_en_cours.empty:
                df_mouvs_en_cours['Date_Debut_dt'] = pd.to_datetime(df_mouvs_en_cours['Date_Debut'], errors='coerce').dt.date
                df_mouvs_en_cours['Date_Fin_dt'] = pd.to_datetime(df_mouvs_en_cours['Date_Fin'], errors='coerce').dt.date
                
                mask_overlap = (
                    (df_mouvs_en_cours['Date_Fin_dt'] >= search_date_debut) &
                    (df_mouvs_en_cours['Date_Debut_dt'] <= search_date_fin)
                )
                matricules_indisponibles = set(df_mouvs_en_cours[mask_overlap]['Matricule'].astype(str).str.strip())
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
    "🗓️ PLANNING", "📄 CONTRATS", "🔑 RETOURS",
    "📊 PERFORMANCES", "🔧 VIDANGES", "👥 CRM", "⚙️ ADMIN"
])

# ============================================================
# TAB 1 : PLANNING 365 JOURS (CORRIGÉ & OPTIMISÉ)
# ============================================================
with tab_planning:
    st.markdown("### 🗓️ PLANNING ANNUEL - 365 JOURS")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        date_base = st.date_input(" Date de début de l'année :", datetime(2026, 1, 1), key="planning_date")
    with col2:
        vehicule_recherche = st.selectbox("🚘 Filtrer véhicule :", ["-- Toutes --"] + liste_vehicules_opt)
    
    array_jours = [date_base + timedelta(days=i) for i in range(365)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    
    df_voitures_valides = df_voitures[
        df_voitures['Matricule'].notna() & 
        (df_voitures['Matricule'].astype(str).str.strip() != '')
    ].copy()
    
    if vehicule_recherche != "-- Toutes --":
        df_voitures_valides = df_voitures_valides[
            df_voitures_valides['Matricule'].astype(str).str.strip() == vehicule_recherche
        ]
    
    if not df_voitures_valides.empty:
        build_matrix = []
        for _, car in df_voitures_valides.iterrows():
            immat = safe_str(car.get('Matricule'))
            modele = safe_str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            marque = safe_str(car.get('Marque', ''))
            ligne = {"Flotte BBNH": f"{marque} — [{immat}]"}
            for col_j in nom_colonnes:
                ligne[col_j] = "● Disponible|disponible"
            build_matrix.append(ligne)
        
        df_final_grid = pd.DataFrame(build_matrix)
        
        if not df_mouvs.empty:
            for _, mv in df_mouvs.iterrows():
                m_v = safe_str(mv.get('Matricule'))
                if not m_v: continue
                    
                client_v = safe_str(mv.get('Client', 'Inconnu'))
                type_statut = safe_str(mv.get('Type_Statut', '')).lower()
                h_debut = formater_heure_propre(mv.get('Heure_Debut'))
                h_fin = formater_heure_propre(mv.get('Heure_Fin'))
                d_debut_mv = parse_date(mv.get('Date_Debut'))
                d_fin_mv = parse_date(mv.get('Date_Fin'))
                
                if not (d_debut_mv and d_fin_mv): continue
                
                if "garage" in type_statut or "maintenance" in type_statut:
                    format_text, color_type = "🛠️ GARAGE", "garage"
                elif "réservation" in type_statut:
                    format_text, color_type = f"[{h_debut}→{h_fin}] {client_v}", "reservation"
                else:
                    heure_debut_int = int(h_debut.split(':')[0]) if ':' in h_debut else 0
                    if heure_debut_int < 12:
                        format_text, color_type = f"[{h_debut}→{h_fin}] {client_v}", "matin_clair"
                    elif heure_debut_int < 17:
                        format_text, color_type = f"[{h_debut}→{h_fin}] {client_v}", "apres_midi_rouge"
                    else:
                        format_text, color_type = f"[{h_debut}→{h_fin}] {client_v}", "soir_fonce"
                
                mask_voiture = df_final_grid['Flotte BBNH'].str.contains(f"[{m_v}]", na=False)
                if mask_voiture.any():
                    idx_voiture = df_final_grid[mask_voiture].index[0]
                    for j in array_jours:
                        if d_debut_mv <= j <= d_fin_mv:
                            key_day = j.strftime("%d/%m")
                            if key_day in df_final_grid.columns:
                                df_final_grid.at[idx_voiture, key_day] = f"{format_text}|{color_type}"
        
        def style_planning_365(val):
            if pd.isna(val): return "background-color: #ffffff; color: #000000; font-size: 10px;"
            val_str = str(val)
            if "|" in val_str:
                _, color_type = val_str.rsplit("|", 1)
            else:
                color_type = "disponible"
            
            if color_type == "disponible":
                return "background-color: #ffffff; color: #000000; font-size: 10px; font-weight: 500; text-align: left; padding: 4px;"
            elif color_type == "garage":
                return "background-color: #fef3c7; color: #92400e; font-weight: 600; font-size: 10px; text-align: left; padding: 4px;"
            elif color_type in ["reservation", "matin_clair"]:
                return "background-color: #86efac; color: #166534; font-weight: 600; font-size: 10px; text-align: left; padding: 4px;"
            elif color_type == "apres_midi_rouge":
                return "background-color: #ef4444; color: #ffffff; font-weight: 700; font-size: 10px; text-align: left; padding: 4px;"
            elif color_type == "soir_fonce":
                return "background-color: #22c55e; color: #ffffff; font-weight: 700; font-size: 10px; text-align: left; padding: 4px;"
            return "background-color: #ffffff; color: #000000; font-size: 10px;"

        cols_ordonnees = ['Flotte BBNH'] + nom_colonnes
        # Appliquer le style ET nettoyer l'affichage (enlever |type)
        styled_df = df_final_grid[cols_ordonnees].style.map(style_planning_365).format(
            lambda x: x.rsplit('|', 1)[0] if pd.notna(x) and '|' in str(x) else x
        )
        
        st.dataframe(styled_df, use_container_width=True, height=600, hide_index=True)
        
        st.markdown("""
        <div style='margin-top: 20px; padding: 15px; background-color: #1f2937; border-radius: 8px;'>
            <h4 style='color: white; margin-bottom: 10px;'>📊 Légende des Couleurs :</h4>
            <div style='display: flex; gap: 20px; flex-wrap: wrap;'>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 20px; height: 20px; background-color: #ffffff; border: 1px solid #e5e7eb; border-radius: 4px;'></div>
                    <span style='color: white; font-size: 13px;'>● Disponible</span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 20px; height: 20px; background-color: #86efac; border: 1px solid #22c55e; border-radius: 4px;'></div>
                    <span style='color: white; font-size: 13px;'>Réservation / Matin (avant 12h)</span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 20px; height: 20px; background-color: #ef4444; border: 1px solid #dc2626; border-radius: 4px;'></div>
                    <span style='color: white; font-size: 13px;'>Location Après-midi (12h-17h) - Urgent</span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 20px; height: 20px; background-color: #22c55e; border: 1px solid #16a34a; border-radius: 4px;'></div>
                    <span style='color: white; font-size: 13px;'>Location Soir (après 17h)</span>
                </div>
                <div style='display: flex; align-items: center; gap: 8px;'>
                    <div style='width: 20px; height: 20px; background-color: #fef3c7; border: 1px solid #fbbf24; border-radius: 4px;'></div>
                    <span style='color: white; font-size: 13px;'>️ Garage / Maintenance</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Aucun véhicule disponible pour afficher le planning.")

# ============================================================
# TAB 2 : CONTRATS
# ============================================================
with tab_contrats:
    st.markdown("###  Liste des Contrats & Mouvements")
    if not df_mouvs.empty and 'id' in df_mouvs.columns:
        df_contrats_list = df_mouvs.sort_values(by='id', ascending=False)
    else:
        df_contrats_list = df_mouvs

    if not df_contrats_list.empty:
        html_parts = ["""
        <table class="contract-table">
            <thead><tr>
                <th>🚗 Matricule</th><th>📞 Tel</th><th>📋 N° Contrat</th>
                <th>📅 Départ</th><th>📅 Retour</th><th> Jours</th>
                <th>💰 Montant</th><th>💸 Reste</th><th>🎁 Caution</th>
                <th>🛣️ KM Sortie</th><th>🏁 KM Retour</th>
            </tr></thead><tbody>
        """]
        
        clients_lookup = {}
        if not df_clients.empty and 'Nom' in df_clients.columns:
            for _, cli in df_clients.iterrows():
                nom = safe_str(cli.get('Nom'))
                if nom:
                    tel = cli.get('Numéro de téléphone', 'N/A')
                    if isinstance(tel, float) and pd.isna(tel): tel = 'N/A'
                    clients_lookup[nom] = str(tel)
        
        for _, row in df_contrats_list.iterrows():
            try:
                matricule = safe_str(row.get('Matricule'), 'N/A')
                client = safe_str(row.get('Client'))
                tel = clients_lookup.get(client, "N/A")
                num_contrat = f"#{int(row.get('id', 0)):04d}" if 'id' in row.index and pd.notna(row.get('id')) else matricule
                d_dep_dt = parse_date(row.get('Date_Debut')) or datetime.now().date()
                d_ret_dt = parse_date(row.get('Date_Fin')) or datetime.now().date()
                jours = max(1, (d_ret_dt - d_dep_dt).days)
                reste_val = safe_float(row.get('Reste'))
                reste_style = "status-paid" if reste_val <= 0 else "status-pending"
                reste_text = "PAYÉ" if reste_val <= 0 else f"{reste_val:,.3f}"

                html_parts.append(f"""
                    <tr>
                        <td><div class="car-info"><div class="car-plate">{matricule}</div></div></td>
                        <td style="color:#007bff; font-weight:bold;">{tel}</td>
                        <td><div class="contract-num">{num_contrat}</div></td>
                        <td style="font-weight:600;">{d_dep_dt.strftime('%d/%m/%Y')}</td>
                        <td style="font-weight:600;">{d_ret_dt.strftime('%d/%m/%Y')}</td>
                        <td style="font-weight:bold; color:#e60000;">{jours} j</td>
                        <td style="font-weight:bold;">{safe_float(row.get('Prix')):,.3f}</td>
                        <td><span class="status-badge {reste_style}">✔ {reste_text}</span></td>
                        <td><strong>{safe_float(row.get('Caution')):,.3f} DT</strong></td>
                        <td><div class="km-value" style="color:#28a745;">{safe_int(row.get('KM_Debut'))} Km</div></td>
                        <td><div class="km-value" style="color:#dc3545;">{safe_int(row.get('KM_Fin'))} Km</div></td>
                    </tr>
                """)
            except: continue
        html_parts.append("</tbody></table>")
        st.markdown("".join(html_parts), unsafe_allow_html=True)
    else:
        st.info("Aucun contrat enregistré.")

# ============================================================
# TAB 3 : RETOURS
# ============================================================
with tab_logistique:
    st.markdown("### 🔑 Terminal de Restitution")
    df_actifs = df_mouvs[df_mouvs.get('Statut_Mouvement', pd.Series()) == 'En cours'].copy() if not df_mouvs.empty else pd.DataFrame()

    if not df_actifs.empty and 'id' in df_actifs.columns:
        choix_actifs = [f"ID: {r.get('id')} | {r.get('Matricule', '')} — {r.get('Client', '')}" for _, r in df_actifs.iterrows()]
        col_list, col_details = st.columns([1, 1])
        with col_list:
            target_v = st.selectbox("Sélectionner le véhicule rentrant : ", choix_actifs)
            d_reel = st.date_input("Date de retour : ", datetime.now())
            t_reel = st.time_input("Heure de retour : ", datetime.now().time())
            l_retour = st.text_input("Lieu de retour : ", value="Siège Monastir")

            id_mouv_temp = int(target_v.split(" | ")[0].replace("ID: ", "").strip())
            res_dep = df_actifs[df_actifs['id'] == id_mouv_temp]
            km_dep_de_base = safe_int(res_dep.iloc[0].get('KM_Debut')) if not res_dep.empty else 0
            km_fin = st.number_input("Kilométrage au Retour : ", min_value=km_dep_de_base, value=km_dep_de_base, step=1)

            if st.button("✅ VALIDATION DU RETOUR", use_container_width=True):
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
                    st.success("✅ Retour validé !")
                    refresh_data()
                    rerun()
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")
        with col_details:
            if not res_dep.empty:
                row_sel = res_dep.iloc[0]
                diff_km = int(km_fin) - int(km_dep_de_base)
                st.markdown(f"**📊 Distance :** <span style='color:#4ade80; font-weight:bold; font-size:22px;'>{diff_km} KM</span>", unsafe_allow_html=True)
                st.write(f"**Reste dû :** {row_sel.get('Reste', '0')} DT")
    else:
        st.info("Aucun déplacement en cours.")

# ============================================================
# TAB 4 : PERFORMANCE
# ============================================================
with tab_analytics:
    st.markdown("### 📊 Performance du Jour")
    day_target = st.date_input("Journée d'analyse :", datetime.now())
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
        with k1: st.metric("📈 DÉPARTS", f"{len(sorties)}")
        with k2: st.metric("🔑 RETOURS", f"{len(entrees)}")
        with k3: st.metric("💰 CA DU JOUR", f"{sorties['Val_Prix'].sum():,.2f} DT")

        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("### 🛫 DÉPARTS")
            if not sorties.empty:
                cols = [c for c in ['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Prix', 'KM_Debut'] if c in sorties.columns]
                st.dataframe(sorties[cols], use_container_width=True, hide_index=True)
            else: st.info("Aucun départ.")
        with col_droite:
            st.markdown("### 🛬 RETOURS")
            if not entrees.empty:
                entrees_c = entrees.copy()
                entrees_c['KM Roulé'] = entrees_c['KM_Fin'] - entrees_c['KM_Debut']
                cols = [c for c in ['Matricule', 'Client', 'Date_Fin', 'Prix', 'KM_Debut', 'KM_Fin', 'KM Roulé'] if c in entrees_c.columns]
                st.dataframe(entrees_c[cols], use_container_width=True, hide_index=True)
            else: st.info("Aucun retour.")

# ============================================================
# TAB 5 : VIDANGES
# ============================================================
with tab_vidange:
    st.markdown("### 🔧 Suivi des Vidanges")
    if not df_vidanges.empty:
        df_v = df_vidanges.copy()
        df_v['KM_Dernier_Vidange'] = pd.to_numeric(df_v['KM_Dernier_Vidange'], errors='coerce').fillna(0).astype(int)
        df_v['KM_Recent'] = pd.to_numeric(df_v['KM_Recent'], errors='coerce').fillna(0).astype(int)
        df_v['KM_circuler'] = df_v['KM_Recent'] - df_v['KM_Dernier_Vidange']
        df_v['km_restant'] = 9000 - df_v['KM_circuler']

        alertes = df_v[df_v['km_restant'] <= 1500]
        if not alertes.empty:
            st.error(f"⚠️ **ALERTE :** {len(alertes)} véhicule(s) à vidanger !")
        else:
            st.success("✅ Flotte OK.")

        cols_aff = [c for c in ['Date_Mise_A_Jour', 'Marque', 'Matricule', 'Date_Dernier_Vidange', 'KM_Dernier_Vidange', 'KM_Recent', 'KM_circuler', 'km_restant'] if c in df_v.columns]
        def colorer_vidanges(row):
            val = row.get('km_restant', 9999)
            if val <= 500: return ['background-color: #ef4444; color: white;'] * len(row)
            elif val <= 1500: return ['background-color: #f97316; color: white;'] * len(row)
            return [''] * len(row)

        styled = df_v[cols_aff].style.apply(colorer_vidanges, axis=1)
        st.dataframe(styled, use_container_width=True, hide_index=True)

        st.markdown("<br>", unsafe_allow_html=True)
        with st.container(border=True):
            if 'Matricule' in df_v.columns and not df_v.empty:
                c_v1, c_v2, c_v3 = st.columns([1.5, 1.5, 2])
                with c_v1:
                    v_select = st.selectbox("Véhicule : ", df_v['Matricule'].tolist())
                    v_info = df_v[df_v['Matricule'] == v_select].iloc[0]
                    init_date_dernier = parse_date(v_info.get('Date_Dernier_Vidange')) or datetime.now().date()
                    date_dernier_manuel = st.date_input("Date Dernier Vidange : ", value=init_date_dernier)
                with c_v2:
                    dernier_km = st.number_input("KM Dernier Vidange : ", min_value=0, value=safe_int(v_info.get('KM_Dernier_Vidange')))
                    nouveau_km = st.number_input("KM Actuel : ", min_value=0, value=safe_int(v_info.get('KM_Recent')))
                with c_v3:
                    date_effective = st.date_input("Date opération : ", datetime.now())
                    action_sync = st.checkbox("Vidange effectuée (reset)")

                if st.button("💾 ENREGISTRER", use_container_width=True):
                    if action_sync:
                        update_row(T_VIDANGE, {
                            "KM_Recent": int(nouveau_km), "KM_Dernier_Vidange": int(nouveau_km),
                            "Date_Dernier_Vidange": date_effective.strftime("%Y-%m-%d"),
                            "Date_Mise_A_Jour": date_effective.strftime("%Y-%m-%d")
                        }, "Matricule", v_select)
                    else:
                        update_row(T_VIDANGE, {
                            "KM_Recent": int(nouveau_km), "KM_Dernier_Vidange": int(dernier_km),
                            "Date_Dernier_Vidange": date_dernier_manuel.strftime("%Y-%m-%d"),
                            "Date_Mise_A_Jour": date_effective.strftime("%Y-%m-%d")
                        }, "Matricule", v_select)
                    st.success("✅ Mis à jour !")
                    refresh_data()
                    rerun()

# ============================================================
# TAB 6 : CRM
# ============================================================
with tab_crm:
    st.markdown("### 👥 Comptes Conducteurs")
    c1, c2 = st.columns([5, 4])
    with c1:
        st.markdown("#### 🔍 Consultation")
        search_query = st.text_input("Rechercher (Nom, CIN) : ", key="crm_search_field")
        if search_query and not df_clients.empty:
            mask = (
                df_clients['Nom'].str.contains(search_query, case=False, na=False) |
                df_clients.get('Prénom', pd.Series()).str.contains(search_query, case=False, na=False) |
                df_clients['CIN'].str.contains(search_query, case=False, na=False)
            )
            clients_trouves = df_clients[mask]

            if not clients_trouves.empty:
                for idx, cli in clients_trouves.iterrows():
                    cin_client = safe_str(cli.get('CIN'))
                    unique_suffix = f"{idx}_{cin_client}"

                    if f"mode_edition_{unique_suffix}" not in st.session_state:
                        st.session_state[f"mode_edition_{unique_suffix}"] = False
                    if f"chk_del_{unique_suffix}" not in st.session_state:
                        st.session_state[f"chk_del_{unique_suffix}"] = False

                    with st.expander(f"👤 {safe_str(cli.get('Nom')).upper()} {safe_str(cli.get('Prénom'))} (CIN: {cin_client})", expanded=True):
                        st.write(f"**📞 Tel :** `{cli.get('Numéro de téléphone', 'N/A')}` | **🚗 Permis :** `{cli.get('N° Permis', 'N/A')}`")
                        col_img1, col_img2 = st.columns(2)
                        with col_img1:
                            img_cin = cli.get('Image CIN')
                            if img_cin:
                                try: st.image(base64.b64decode(img_cin), caption="CIN", use_container_width=True)
                                except: pass
                        with col_img2:
                            img_per = cli.get('Image Permis')
                            if img_per:
                                try: st.image(base64.b64decode(img_per), caption="Permis", use_container_width=True)
                                except: pass

                        col_btn_mod, col_btn_sup = st.columns(2)
                        with col_btn_mod:
                            if st.button(f"✏️ MODIFIER", key=f"btn_edit_{unique_suffix}"):
                                st.session_state[f"mode_edition_{unique_suffix}"] = True
                                rerun()
                        with col_btn_sup:
                            check_sup = st.checkbox("Confirmer suppression", key=f"chk_del_{unique_suffix}")
                            if st.button(f"🗑️ SUPPRIMER", key=f"btn_del_{unique_suffix}"):
                                if check_sup:
                                    delete_row(T_CLIENT, "CIN", cin_client)
                                    st.success(f"✅ Client supprimé.")
                                    refresh_data()
                                    rerun()
                                else:
                                    st.warning("Cochez la case de confirmation.")

                        if st.session_state.get(f"mode_edition_{unique_suffix}", False):
                            with st.form(key=f"form_edit_{unique_suffix}"):
                                e_prenom = st.text_input("Prénom", value=safe_str(cli.get('Prénom')))
                                e_nom = st.text_input("Nom", value=safe_str(cli.get('Nom')))
                                e_tel = st.text_input("Téléphone", value=safe_str(cli.get('Numéro de téléphone')))
                                e_permis = st.text_input("N° Permis", value=safe_str(cli.get('N° Permis')))
                                e_d_cin = st.date_input("Date CIN", value=parse_date(cli.get('Date Délivrance CIN')) or datetime.now().date())
                                e_d_per = st.date_input("Date Permis", value=parse_date(cli.get('Date Délivrance Permis')) or datetime.now().date())
                                f_cin_r = st.file_uploader("Nouvelle CIN", type=["png", "jpg", "jpeg"], key=f"f_cin_{unique_suffix}")
                                f_per_r = st.file_uploader("Nouveau Permis", type=["png", "jpg", "jpeg"], key=f"f_per_{unique_suffix}")
                                if st.form_submit_button("✅ METTRE À JOUR"):
                                    upd = {
                                        "Prénom": e_prenom, "Nom": e_nom,
                                        "Numéro de téléphone": e_tel, "N° Permis": e_permis,
                                        "Date Délivrance CIN": e_d_cin.strftime("%Y-%m-%d"),
                                        "Date Délivrance Permis": e_d_per.strftime("%Y-%m-%d")
                                    }
                                    if f_cin_r: upd["Image CIN"] = encoder_image_base64(f_cin_r)
                                    if f_per_r: upd["Image Permis"] = encoder_image_base64(f_per_r)
                                    update_row(T_CLIENT, upd, "CIN", cin_client)
                                    st.success("✅ Mis à jour !")
                                    st.session_state[f"mode_edition_{unique_suffix}"] = False
                                    refresh_data()
                                    rerun()
    with c2:
        st.markdown("#### ➕ Nouveau Client")
        with st.form("form_new_client_crm"):
            n_prenom = st.text_input("Prénom *")
            n_nom = st.text_input("Nom *")
            n_cin = st.text_input("N° CIN *")
            n_tel = st.text_input("Téléphone")
            n_permis = st.text_input("N° Permis")
            n_d_cin = st.date_input("Date CIN", value=datetime.now() - timedelta(days=365))
            n_d_per = st.date_input("Date Permis", value=datetime.now() - timedelta(days=365))
            f_cin_new = st.file_uploader("Image CIN", type=["png", "jpg", "jpeg"])
            f_per_new = st.file_uploader("Image Permis", type=["png", "jpg", "jpeg"])
            if st.form_submit_button(" CRÉER LE PROFIL"):
                if n_prenom and n_nom and n_cin:
                    insert_row(T_CLIENT, {
                        "Prénom": n_prenom, "Nom": n_nom, "CIN": n_cin,
                        "Numéro de téléphone": n_tel, "N° Permis": n_permis,
                        "Date Délivrance CIN": n_d_cin.strftime("%Y-%m-%d"),
                        "Date Délivrance Permis": n_d_per.strftime("%Y-%m-%d"),
                        "Image CIN": encoder_image_base64(f_cin_new),
                        "Image Permis": encoder_image_base64(f_per_new)
                    })
                    st.success("✅ Client créé !")
                    refresh_data()
                    rerun()
                else:
                    st.error("❌ Champs obligatoires manquants")

# ============================================================
# TAB 7 : ADMIN
# ============================================================
with tab_admin:
    st.markdown("### ⚙️ Panneau d'Administration")
    st.warning("⚠️ Actions irréversibles !")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🗑️ PURGER TOUS LES MOUVEMENTS"):
            if st.checkbox("Confirmer la purge des mouvements", key="chk_purge_mouv"):
                delete_all(T_MOUVEMENT)
                st.success("✅ Mouvements purgés.")
                refresh_data()
                rerun()
    with col_a2:
        if st.button("🗑️ PURGER TOUS LES CLIENTS"):
            if st.checkbox("Confirmer la purge des clients", key="chk_purge_cli"):
                delete_all(T_CLIENT)
                st.success("✅ Clients purgés.")
                refresh_data()
                rerun()
