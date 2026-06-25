import streamlit as st
import pandas as pd
from supabase import create_client, Client
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

def style_apply(df_style, func, **kwargs):
    try: return df_style.map(func, **kwargs)
    except AttributeError: return df_style.applymap(func, **kwargs)

st.set_page_config(page_title="BBNH OS", layout="wide", page_icon="🏎️", initial_sidebar_state="expanded")

# --- CSS PREMIUM ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif !important; background-color: #09090b !important; color: #fafafa !important; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1400px; }
section[data-testid="stSidebar"] { background-color: #0f0f12 !important; border-right: 1px solid #27272a !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; margin-bottom: 20px; }
.stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; font-weight: 600; color: #a1a1aa; background-color: transparent; border: none !important; }
.stTabs [aria-selected="true"] { background-color: #e11d48 !important; color: #ffffff !important; }
div[data-testid="stVerticalBorder"] { background: rgba(24, 24, 27, 0.6) !important; border: 1px solid #27272a !important; border-radius: 12px !important; padding: 20px !important; }
div.stButton > button { background: #e11d48 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 10px 20px !important; font-weight: 600 !important; transition: all 0.2s ease; }
div.stButton > button:hover { background: #be123c !important; transform: translateY(-1px); }
div[data-testid="stMetric"] { background-color: #18181b; border: 1px solid #27272a; border-radius: 10px; padding: 15px; }
div[data-testid="stMetricLabel"] { color: #a1a1aa !important; font-weight: 500 !important; }
div[data-testid="stMetricValue"] { color: #fafafa !important; font-weight: 700 !important; }
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { background-color: #18181b !important; border: 1px solid #3f3f46 !important; color: #fafafa !important; border-radius: 8px !important; }
footer { visibility: hidden; }
#MainMenu { visibility: hidden; }
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #09090b; }
::-webkit-scrollbar-thumb { background: #3f3f46; border-radius: 4px; }
.contract-table { width: 100%; border-collapse: collapse; color: #fafafa; font-size: 14px; }
.contract-table th { background-color: #18181b; color: #a1a1aa; font-weight: 600; text-align: left; padding: 12px; border-bottom: 1px solid #27272a; }
.contract-table td { padding: 12px; border-bottom: 1px solid #27272a; }
.contract-table tr:hover { background-color: rgba(255,255,255,0.02); }
.status-paid { color: #4ade80; font-weight: 600; }
.status-pending { color: #f87171; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# SUPABASE OPTIMISÉ
# ============================================================
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets.get("SUPABASE_URL", "")
        key = st.secrets.get("SUPABASE_KEY", "")
        if not url or not key: return None
        return create_client(url, key)
    except: return None

supabase = init_supabase()
if supabase is None:
    st.error("🔴 Connexion Supabase impossible.")
    st.stop()

T_CLIENT = "client"
T_VEHICULE = "vehicule"
T_MOUVEMENT = "mouvement"
T_VIDANGE = "vidange"
T_CONTRAT = "carbbnh"

# ============================================================
# UTILITAIRES
# ============================================================
def safe_str(val, default=""):
    if val is None or (isinstance(val, float) and pd.isna(val)): return default
    s = str(val).strip()
    return default if s.lower() in ('nan', 'none', '') else s

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
    if " " in val_str: val_str = val_str.split(" ")[1]
    parts = val_str.split(":")
    return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}" if len(parts) >= 2 else '00:00'

def parse_date(val):
    if val is None: return None
    if isinstance(val, datetime): return val.date() if hasattr(val, 'date') else val
    s = safe_str(val)
    if not s: return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y-%m-%d %H:%M:%S"):
        try: return datetime.strptime(s, fmt).date()
        except: pass
    try: return pd.to_datetime(s).date()
    except: return None

# ============================================================
# CACHE OPTIMISÉ (TTL long, invalidation ciblée)
# ============================================================
@st.cache_data(ttl=3600, show_spinner=False)  # 1 heure au lieu de 30s
def get_all(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except: return pd.DataFrame()

def invalidate_cache(table_name=None):
    """Invalide le cache de manière ciblée"""
    if table_name:
        get_all.clear(table_name)
    else:
        get_all.clear()

# ============================================================
# OPÉRATIONS DB OPTIMISÉES
# ============================================================
def insert_row(table_name, data_dict):
    try:
        clean_data = {k: v for k, v in data_dict.items() if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).insert(clean_data).execute()
        invalidate_cache(table_name)
        return True
    except Exception as e:
        st.error(f"Erreur insert: {e}")
        return False

def update_row(table_name, data_dict, column, value):
    try:
        clean_data = {k: v for k, v in data_dict.items() if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).update(clean_data).eq(column, value).execute()
        invalidate_cache(table_name)
        return True
    except Exception as e:
        st.error(f"Erreur update: {e}")
        return False

def delete_row(table_name, column, value):
    try:
        supabase.table(table_name).delete().eq(column, value).execute()
        invalidate_cache(table_name)
        return True
    except: return False

def delete_all(table_name):
    try:
        supabase.table(table_name).delete().neq("id", 0).execute()
        invalidate_cache(table_name)
        return True
    except: return False

def upsert_vidange_optimized(matricule, marque, km_recent, df_vidanges_cached):
    """UPSERT optimisé : utilise le cache existant, pas de requête SELECT supplémentaire"""
    try:
        # Vérifier dans le cache si existe déjà
        exists = False
        if not df_vidanges_cached.empty and 'Matricule' in df_vidanges_cached.columns:
            existing = df_vidanges_cached[df_vidanges_cached['Matricule'].astype(str).str.strip() == str(matricule).strip()]
            exists = not existing.empty
        
        data = {
            "Matricule": matricule,
            "Marque": safe_str(marque).upper(),
            "KM_Recent": int(km_recent),
            "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")
        }
        
        if exists:
            # UPDATE uniquement
            supabase.table(T_VIDANGE).update(data).eq("Matricule", matricule).execute()
        else:
            # INSERT avec données complètes
            data.update({
                "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                "KM_Dernier_Vidange": 0
            })
            supabase.table(T_VIDANGE).insert(data).execute()
        
        invalidate_cache(T_VIDANGE)
        return True
    except Exception as e:
        return False

# ============================================================
# CHARGEMENT UNIQUE DES DONNÉES
# ============================================================
# Charger TOUTES les tables UNE SEULE FOIS au début
df_voitures = get_all(T_VEHICULE)
df_clients = get_all(T_CLIENT)
df_mouvs = get_all(T_MOUVEMENT)
df_vidanges = get_all(T_VIDANGE)
df_contrats = get_all(T_CONTRAT)

# SUPPRIMÉ : La boucle de synchronisation qui ralentissait tout
# La sync se fait uniquement lors des actions utilisateur

def build_liste_clients():
    opts = ["-- Entrée manuelle --"]
    if not df_clients.empty and 'Nom' in df_clients.columns:
        for _, row in df_clients.iterrows():
            nom, prenom, cin = safe_str(row.get('Nom')), safe_str(row.get('Prénom')), safe_str(row.get('CIN'))
            if nom: opts.append(f"{nom.upper()} {prenom} (CIN: {cin})")
    return opts

def build_liste_vehicules():
    if df_voitures.empty or 'Matricule' not in df_voitures.columns: return []
    return [safe_str(r.get('Matricule')) for _, r in df_voitures.iterrows() if safe_str(r.get('Matricule'))]

liste_clients_opt = build_liste_clients()
liste_vehicules_opt = build_liste_vehicules()

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    logo_path = "IMG_7149 (1).jpeg"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center; color: #e11d48; font-weight:800; margin:0;'>BBNH</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #71717a; font-size:12px; letter-spacing:3px; margin-bottom:20px;'>RENT A CAR OS</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    menu_action = st.radio("Navigation", [
        "📊 Dashboard",
        "🗓️ Planning",
        "📝 Nouveau Contrat",
        "🔑 Retours",
        "🚗 Flotte",
        "👥 CRM",
        "🔧 Vidanges",
        "⚙️ Admin"
    ], label_visibility="collapsed")
    
    st.markdown("---")
    st.caption(f"🟢 Connecté | {datetime.now().strftime('%H:%M')}")

# ============================================================
# ROUTEUR
# ============================================================

if menu_action == "📊 Dashboard":
    st.markdown("# Tableau de Bord")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        actifs = len(df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']) if not df_mouvs.empty and 'Statut_Mouvement' in df_mouvs.columns else 0
        st.metric("Contrats Actifs", actifs)
    with c2:
        st.metric("Véhicules", len(df_voitures))
    with c3:
        today = datetime.now().date()
        ca_jour = 0
        if not df_mouvs.empty and 'Date_Debut' in df_mouvs.columns:
            df_tmp = df_mouvs.copy()
            df_tmp['Clean_D'] = pd.to_datetime(df_tmp['Date_Debut'], errors='coerce').dt.date
            ca_jour = df_tmp[df_tmp['Clean_D'] == today]['Prix'].apply(safe_float).sum()
        st.metric("CA du Jour", f"{ca_jour:,.2f} DT")
    with c4:
        alertes_v = 0
        if not df_vidanges.empty:
            df_v_tmp = df_vidanges.copy()
            df_v_tmp['KM_circuler'] = pd.to_numeric(df_v_tmp['KM_Recent'], errors='coerce').fillna(0) - pd.to_numeric(df_v_tmp['KM_Dernier_Vidange'], errors='coerce').fillna(0)
            alertes_v = len(df_v_tmp[(9000 - df_v_tmp['KM_circuler']) <= 1500])
        st.metric("Alertes Vidange", alertes_v)

    st.markdown("### 🚗 Disponibles")
    dispo = df_voitures.copy() if not df_voitures.empty else pd.DataFrame()
    if not df_mouvs.empty and not dispo.empty and 'Matricule' in dispo.columns:
        indispo = set()
        for _, mv in df_mouvs.iterrows():
            if safe_str(mv.get('Statut_Mouvement')) == 'En cours':
                d_deb = parse_date(mv.get('Date_Debut'))
                d_fin = parse_date(mv.get('Date_Fin'))
                if d_deb and d_fin and d_deb <= today <= d_fin:
                    indispo.add(safe_str(mv.get('Matricule')))
        dispo = dispo[~dispo['Matricule'].isin(indispo)]
    
    if not dispo.empty:
        st.dataframe(dispo[['Matricule', 'Marque', 'Modèle']].rename(columns={'Matricule':'Plaque'}), use_container_width=True, hide_index=True)
    else:
        st.warning("Aucun véhicule disponible.")

elif menu_action == "🗓️ Planning":
    st.markdown("# Planning")
    
    date_base = st.date_input("Point de départ", datetime.now(), key="grid_date")
    array_jours = [date_base + timedelta(days=i) for i in range(14)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    
    if not df_voitures.empty and 'Matricule' in df_voitures.columns:
        build_matrix = []
        for _, car in df_voitures.iterrows():
            immat = safe_str(car.get('Matricule'))
            if not immat: continue
            modele = safe_str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            ligne = {"Véhicule": f"{modele} [{immat}]"}
            for col_j in nom_colonnes: ligne[col_j] = "✅"
            build_matrix.append(ligne)
            
        df_grid = pd.DataFrame(build_matrix)
        suivi = {}
        
        if not df_mouvs.empty:
            for _, mv in df_mouvs.iterrows():
                m_v = safe_str(mv.get('Matricule'))
                if not m_v: continue
                d_deb = parse_date(mv.get('Date_Debut'))
                d_fin = parse_date(mv.get('Date_Fin'))
                if not (d_deb and d_fin): continue
                
                client_v = safe_str(mv.get('Client'))
                if m_v not in suivi: suivi[m_v] = {}
                for j in array_jours:
                    if d_deb <= j <= d_fin:
                        suivi[m_v][j.strftime("%d/%m")] = f"🔴 {client_v}"

        for idx, row in df_grid.iterrows():
            mat = row["Véhicule"].split("[")[-1].replace("]", "").strip()
            if mat in suivi:
                for key_day, desc in suivi[mat].items():
                    if key_day in df_grid.columns:
                        df_grid.at[idx, key_day] = desc

        def style_grid(val):
            if "✅" in str(val): return "background-color: #18181b; color: #4ade80; text-align: center; font-weight: 600;"
            elif "🔴" in str(val): return "background-color: #450a0a; color: #fca5a5; text-align: center; font-weight: 600;"
            return ""

        st.dataframe(df_grid.style.map(style_grid, subset=nom_colonnes), use_container_width=True, height=600, hide_index=True)

elif menu_action == "📝 Nouveau Contrat":
    st.markdown("# Nouveau Contrat")
    
    with st.container(border=True):
        col_l, col_r = st.columns(2)
        with col_l:
            nature = st.selectbox("Nature", ["Contrat Location", "Réservation", "Maintenance"])
            vehicule = st.selectbox("Véhicule", liste_vehicules_opt) if liste_vehicules_opt else st.text_input("Véhicule")
            client_b = st.selectbox("Client", liste_clients_opt)
            nom_m = st.text_input("Nom")
            cin_m = st.text_input("CIN")
            permis_m = st.text_input("Permis")
            
        with col_r:
            c_d1, c_t1 = st.columns(2)
            with c_d1: d1 = st.date_input("Date Début", datetime.now())
            with c_t1: t1 = st.time_input("Heure", time(9, 0))
            c_d2, c_t2 = st.columns(2)
            with c_d2: d2 = st.date_input("Date Fin", datetime.now() + timedelta(days=2))
            with c_t2: t2 = st.time_input("Heure", time(12, 0))
            
            nbr_jours = max(1, (d2 - d1).days)
            st.markdown(f"**Durée :** `{nbr_jours}j`")
            prix_unit = st.number_input("Prix/Jour", min_value=0, value=100, step=5)
            montant = st.number_input("Total", min_value=0, value=int(nbr_jours * prix_unit))
            caution = st.number_input("Caution", value=0)
            reste = montant - caution
            st.markdown(f"**Reste :** `{reste} DT`")

    with st.container(border=True):
        col_km, col_lieu = st.columns(2)
        with col_km: km_deb = st.number_input("KM Départ", min_value=0, value=0)
        with col_lieu: lieu = st.text_input("Lieu", value="Siège Monastir")
        no_vol = st.text_input("N° Vol")
        note = st.text_area("Note")
        ref = st.text_input("Réf", f"BBNH-{datetime.now().strftime('%d%H%S')}")
        
        c_f1, c_f2 = st.columns(2)
        with c_f1: f_cin = st.file_uploader("CIN", type=["png", "jpg", "jpeg", "pdf"])
        with c_f2: f_permis = st.file_uploader("Permis", type=["png", "jpg", "jpeg", "pdf"])

        if st.button("⚡ CRÉER", use_container_width=True):
            with st.status("Création...") as status:
                try:
                    nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[0]
                    cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "").strip()
                    
                    if client_b == "-- Entrée manuelle --" and cin_f:
                        insert_row(T_CLIENT, {"Nom": nom_f, "CIN": cin_f, "N° Permis": permis_m, "Image CIN": encoder_image_base64(f_cin), "Image Permis": encoder_image_base64(f_permis)})
                    
                    ok = insert_row(T_MOUVEMENT, {
                        "Matricule": vehicule, "Type_Statut": "Location" if "Contrat" in nature else nature,
                        "Date_Debut": d1.strftime("%Y-%m-%d"), "Heure_Debut": t1.strftime("%H:%M"),
                        "Date_Fin": d2.strftime("%Y-%m-%d"), "Heure_Fin": t2.strftime("%H:%M"),
                        "Client": nom_f, "Prix": str(montant), "Statut_Mouvement": "En cours",
                        "Caution": str(caution), "Reste": str(reste), "Lieu_Reception": lieu,
                        "No_Vol": no_vol, "Info_Note": note, "KM_Debut": int(km_deb), "KM_Fin": 0
                    })
                    
                    if ok:
                        # Utiliser le cache existant, pas de requête supplémentaire
                        upsert_vidange_optimized(vehicule, "", int(km_deb), df_vidanges)
                        status.update(label="✅ Créé !", state="complete")
                        st.toast("Contrat créé !", icon="🚀")
                        rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")

elif menu_action == "🔑 Retours":
    st.markdown("# Retours")
    df_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours'] if not df_mouvs.empty and 'Statut_Mouvement' in df_mouvs.columns else pd.DataFrame()
    
    if not df_actifs.empty and 'id' in df_actifs.columns:
        choix = [f"{r.get('Matricule')} — {r.get('Client')} (ID:{r.get('id')})" for _, r in df_actifs.iterrows()]
        
        with st.container(border=True):
            col_l, col_r = st.columns(2)
            with col_l:
                target = st.selectbox("Véhicule", choix)
                id_mouv = int(target.split("(ID:")[1].replace(")", ""))
                res = df_actifs[df_actifs['id'] == id_mouv]
                d_ret = st.date_input("Date retour", datetime.now())
                t_ret = st.time_input("Heure", datetime.now().time())
                km_dep = safe_int(res.iloc[0].get('KM_Debut')) if not res.empty else 0
                km_fin = st.number_input("KM Retour", min_value=km_dep, value=km_dep)
                
                if st.button("✅ VALIDER", use_container_width=True):
                    with st.status("Validation..."):
                        veh = safe_str(res.iloc[0].get('Matricule'))
                        update_row(T_MOUVEMENT, {"Statut_Mouvement": "Retourné", "Date_Fin": d_ret.strftime("%Y-%m-%d"), "Heure_Fin": t_ret.strftime("%H:%M"), "KM_Fin": int(km_fin)}, "id", id_mouv)
                        upsert_vidange_optimized(veh, "", int(km_fin), df_vidanges)
                        st.toast("Retour validé !", icon="🔑")
                        rerun()
                        
            with col_r:
                if not res.empty:
                    row = res.iloc[0]
                    st.metric("Distance", f"{int(km_fin) - km_dep} KM")
                    st.metric("Reste", f"{row.get('Reste', 0)} DT")
                    st.info(f"**{row.get('Client')}**\n{row.get('Matricule')}")
    else:
        st.info("Aucun véhicule en circulation.")

elif menu_action == "🚗 Flotte":
    st.markdown("# Flotte")
    tab_add, tab_del = st.tabs(["➕ Ajouter", "🗑️ Supprimer"])
    
    with tab_add:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                mat = st.text_input("Matricule *")
                marque = st.text_input("Marque *")
            with c2:
                modele = st.text_input("Modèle *")
                annee = st.text_input("Année", value="2026")
            
            if st.button("Enregistrer"):
                if mat and marque and modele:
                    insert_row(T_VEHICULE, {"Matricule": mat, "Marque": marque, "Modèle": modele, "Année": annee})
                    upsert_vidange_optimized(mat, marque, 0, df_vidanges)
                    st.toast("Ajouté !", icon="🚗")
                    rerun()

    with tab_del:
        if liste_vehicules_opt:
            with st.container(border=True):
                v_del = st.selectbox("Retirer", liste_vehicules_opt)
                if st.button("💥 Supprimer"):
                    delete_row(T_VEHICULE, "Matricule", v_del)
                    delete_row(T_VIDANGE, "Matricule", v_del)
                    st.toast("Retiré", icon="🗑️")
                    rerun()

elif menu_action == "👥 CRM":
    st.markdown("# Clients")
    tab_list, tab_new = st.tabs(["📋 Liste", "➕ Nouveau"])
    
    with tab_list:
        search = st.text_input("Rechercher")
        if search and not df_clients.empty:
            mask = df_clients['Nom'].str.contains(search, case=False, na=False) | df_clients['CIN'].str.contains(search, case=False, na=False)
            for idx, cli in df_clients[mask].iterrows():
                with st.expander(f"👤 {safe_str(cli.get('Nom')).upper()} ({safe_str(cli.get('CIN'))})"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.write(f"**Tél:** {cli.get('Numéro de téléphone', 'N/A')}")
                        st.write(f"**Permis:** {cli.get('N° Permis', 'N/A')}")
                    with c2:
                        if cli.get('Image CIN'):
                            try: st.image(base64.b64decode(cli.get('Image CIN')), width=200)
                            except: pass
                    if st.button(f"🗑️ Supprimer", key=f"del_{idx}"):
                        delete_row(T_CLIENT, "CIN", safe_str(cli.get('CIN')))
                        st.toast("Supprimé", icon="🗑️")
                        rerun()

    with tab_new:
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                n_nom = st.text_input("Nom *")
                n_cin = st.text_input("CIN *")
                n_permis = st.text_input("Permis")
            with c2:
                n_prenom = st.text_input("Prénom")
                n_tel = st.text_input("Téléphone")
                f_cin = st.file_uploader("CIN", type=["png", "jpg", "jpeg"])
            if st.button("Créer"):
                if n_nom and n_cin:
                    insert_row(T_CLIENT, {"Nom": n_nom, "Prénom": n_prenom, "CIN": n_cin, "Numéro de téléphone": n_tel, "N° Permis": n_permis, "Image CIN": encoder_image_base64(f_cin)})
                    st.toast("Créé !", icon="👤")
                    rerun()

elif menu_action == "🔧 Vidanges":
    st.markdown("# Vidanges")
    if not df_vidanges.empty:
        df_v = df_vidanges.copy()
        df_v['KM_circuler'] = pd.to_numeric(df_v['KM_Recent'], errors='coerce').fillna(0) - pd.to_numeric(df_v['KM_Dernier_Vidange'], errors='coerce').fillna(0)
        df_v['km_restant'] = 9000 - df_v['KM_circuler']
        
        def color_vid(val):
            if val <= 500: return 'background-color: #7f1d1d; color: #fca5a5;'
            elif val <= 1500: return 'background-color: #78350f; color: #fcd34d;'
            return ''
            
        cols = [c for c in ['Matricule', 'Marque', 'KM_Dernier_Vidange', 'KM_Recent', 'KM_circuler', 'km_restant'] if c in df_v.columns]
        st.dataframe(df_v[cols].style.map(color_vid, subset=['km_restant']), use_container_width=True, hide_index=True)
        
        with st.container(border=True):
            st.markdown("#### Mise à jour")
            v_sel = st.selectbox("Véhicule", df_v['Matricule'].tolist())
            info = df_v[df_v['Matricule'] == v_sel].iloc[0]
            new_km = st.number_input("Nouveau KM", value=safe_int(info.get('KM_Recent')))
            is_done = st.checkbox("Vidange effectuée")
            if st.button("Mettre à jour"):
                upd = {"KM_Recent": int(new_km), "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")}
                if is_done:
                    upd["KM_Dernier_Vidange"] = int(new_km)
                    upd["Date_Dernier_Vidange"] = datetime.now().strftime("%Y-%m-%d")
                update_row(T_VIDANGE, upd, "Matricule", v_sel)
                st.toast("Mis à jour !", icon="🔧")
                rerun()

elif menu_action == "⚙️ Admin":
    st.markdown("# ⚠️ Administration")
    st.error("Actions irréversibles.")
    c1, c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### Purger Mouvements")
            if st.button("🗑️ Tout supprimer", key="p_m"):
                delete_all(T_MOUVEMENT)
                st.toast("Purgé", icon="🗑️")
                rerun()
    with c2:
        with st.container(border=True):
            st.markdown("### Purger Clients")
            if st.button("🗑️ Tout supprimer", key="p_c"):
                delete_all(T_CLIENT)
                st.toast("Purgé", icon="🗑️")
                rerun()
