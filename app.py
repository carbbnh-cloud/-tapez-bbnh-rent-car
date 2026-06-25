import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
import base64
from datetime import datetime, timedelta, time
import traceback

if hasattr(st, "rerun"): rerun = st.rerun
elif hasattr(st, "experimental_rerun"): rerun = st.experimental_rerun
else: 
    def rerun(): pass

st.set_page_config(page_title="BBNH OS", layout="wide", page_icon="🏎️", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif !important; background-color: #09090b !important; color: #fafafa !important; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1600px; }
section[data-testid="stSidebar"] { background-color: #0f0f12 !important; border-right: 1px solid #27272a !important; }
.stTabs [data-baseweb="tab-list"] { gap: 8px; background-color: transparent; margin-bottom: 20px; }
.stTabs [data-baseweb="tab"] { padding: 10px 20px; border-radius: 8px; font-weight: 600; color: #a1a1aa; background-color: transparent; border: none !important; }
.stTabs [aria-selected="true"] { background-color: #e11d48 !important; color: #ffffff !important; }
div[data-testid="stVerticalBorder"] { background: rgba(24, 24, 27, 0.6) !important; border: 1px solid #27272a !important; border-radius: 12px !important; padding: 20px !important; }
div.stButton > button { background: #e11d48 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 10px 20px !important; font-weight: 600 !important; transition: all 0.2s; }
div.stButton > button:hover { background: #be123c !important; transform: translateY(-1px); box-shadow: 0 4px 12px rgba(225, 29, 72, 0.4); }
div[data-testid="stMetric"] { background-color: #18181b; border: 1px solid #27272a; border-radius: 10px; padding: 15px; }
.stTextInput input, .stNumberInput input, .stDateInput input, .stSelectbox div[data-baseweb="select"] { background-color: #18181b !important; border: 1px solid #3f3f46 !important; color: #fafafa !important; border-radius: 8px !important; }
footer {visibility: hidden;} #MainMenu {visibility: hidden;}

/* PLANNING GANTT STYLES */
.gantt-container { 
    background: #0f0f12; 
    border-radius: 12px; 
    padding: 20px; 
    overflow-x: auto;
    border: 1px solid #27272a;
}
.gantt-header {
    display: flex;
    border-bottom: 2px solid #27272a;
    padding-bottom: 10px;
    margin-bottom: 10px;
    position: sticky;
    top: 0;
    background: #0f0f12;
    z-index: 10;
}
.gantt-header-cell {
    min-width: 80px;
    text-align: center;
    font-weight: 600;
    color: #a1a1aa;
    font-size: 12px;
    padding: 8px 4px;
}
.gantt-header-cell:first-child {
    min-width: 200px;
    text-align: left;
    color: #fafafa;
    font-size: 14px;
}
.gantt-row {
    display: flex;
    border-bottom: 1px solid #1f1f23;
    min-height: 60px;
    align-items: center;
    transition: background 0.2s;
}
.gantt-row:hover {
    background: rgba(255,255,255,0.02);
}
.gantt-cell {
    min-width: 80px;
    height: 50px;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
}
.gantt-cell:first-child {
    min-width: 200px;
    justify-content: flex-start;
    padding-left: 10px;
}
.gantt-bar {
    position: absolute;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 600;
    color: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    transition: all 0.2s;
    cursor: pointer;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    padding: 0 8px;
}
.gantt-bar:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 16px rgba(0,0,0,0.5);
    z-index: 100;
}
.gantt-bar-location { background: linear-gradient(135deg, #e11d48 0%, #be123c 100%); }
.gantt-bar-reservation { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); }
.gantt-bar-maintenance { background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); }
.gantt-bar-today { 
    border: 2px solid #e11d48;
    background: rgba(225, 29, 72, 0.1);
}
.vehicle-label {
    font-weight: 600;
    color: #fafafa;
    font-size: 13px;
}
.vehicle-plate {
    color: #a1a1aa;
    font-size: 11px;
    margin-top: 2px;
}
.gantt-legend {
    display: flex;
    gap: 20px;
    margin-top: 15px;
    padding: 10px;
    background: #18181b;
    border-radius: 8px;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #a1a1aa;
}
.legend-dot {
    width: 16px;
    height: 16px;
    border-radius: 4px;
}
.nav-buttons {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
}
.nav-btn {
    background: #18181b !important;
    border: 1px solid #27272a !important;
    color: #fafafa !important;
    padding: 8px 16px !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
.nav-btn:hover {
    background: #27272a !important;
    border-color: #3f3f46 !important;
}
.today-marker {
    position: absolute;
    top: 0;
    bottom: 0;
    width: 2px;
    background: #e11d48;
    z-index: 5;
}
</style>
""", unsafe_allow_html=True)

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

T_CLIENT, T_VEHICULE, T_MOUVEMENT, T_VIDANGE, T_CONTRAT = "client", "vehicule", "mouvement", "vidange", "carbbnh"

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

@st.cache_data(ttl=300, show_spinner=False)
def get_all(table_name, exclude_heavy=False):
    try:
        if exclude_heavy and table_name == T_CLIENT:
            response = supabase.table(table_name).select("id, Nom, Prénom, CIN, Numéro de téléphone, N° Permis, Date Délivrance CIN, Date Délivrance Permis").execute()
        else:
            response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except: return pd.DataFrame()

@st.cache_data(ttl=300, show_spinner=False)
def get_client_details(cin):
    try:
        response = supabase.table(T_CLIENT).select("*, Image CIN, Image Permis").eq("CIN", cin).execute()
        return response.data[0] if response.data else None
    except: return None

def insert_row(table_name, data_dict):
    try:
        clean_data = {k: v for k, v in data_dict.items() if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).insert(clean_data).execute()
        return True
    except Exception as e:
        st.toast(f"Erreur DB: {e}", icon="❌")
        return False

def update_row(table_name, data_dict, column, value):
    try:
        clean_data = {k: v for k, v in data_dict.items() if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).update(clean_data).eq(column, value).execute()
        return True
    except: return False

def delete_row(table_name, column, value):
    try:
        supabase.table(table_name).delete().eq(column, value).execute()
        return True
    except: return False

def delete_all(table_name):
    try:
        supabase.table(table_name).delete().neq("id", 0).execute()
        return True
    except:
        try:
            df = get_all(table_name)
            if not df.empty and 'id' in df.columns:
                for id_val in df['id'].tolist():
                    supabase.table(table_name).delete().eq("id", id_val).execute()
            return True
        except: return False

def upsert_vidange(matricule, marque, km_recent=0):
    try:
        df_v = get_all(T_VIDANGE)
        if not df_v.empty and 'Matricule' in df_v.columns:
            existing = df_v[df_v['Matricule'].astype(str).str.strip() == str(matricule).strip()]
            if not existing.empty:
                return update_row(T_VIDANGE, {"KM_Recent": int(km_recent), "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")}, "Matricule", matricule)
        return insert_row(T_VIDANGE, {
            "Matricule": matricule, "Marque": safe_str(marque).upper(),
            "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
            "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
            "KM_Dernier_Vidange": 0, "KM_Recent": int(km_recent)
        })
    except: return False

df_voitures = get_all(T_VEHICULE)
df_clients_light = get_all(T_CLIENT, exclude_heavy=True)
df_mouvs = get_all(T_MOUVEMENT)
df_vidanges = get_all(T_VIDANGE)

def build_liste_clients():
    opts = ["-- Entrée manuelle --"]
    if not df_clients_light.empty and 'Nom' in df_clients_light.columns:
        for _, row in df_clients_light.iterrows():
            nom, prenom, cin = safe_str(row.get('Nom')), safe_str(row.get('Prénom')), safe_str(row.get('CIN'))
            if nom: opts.append(f"{nom.upper()} {prenom} (CIN: {cin})")
    return opts

def build_liste_vehicules():
    if df_voitures.empty or 'Matricule' not in df_voitures.columns: return []
    return [safe_str(r.get('Matricule')) for _, r in df_voitures.iterrows() if safe_str(r.get('Matricule'))]

liste_clients_opt = build_liste_clients()
liste_vehicules_opt = build_liste_vehicules()

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #e11d48; font-weight:800; margin:0;'>BBNH</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #71717a; font-size:12px; letter-spacing:3px; margin-bottom:20px;'>OS V2 FAST</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu_action = st.radio("Navigation", [
        "📊 Dashboard", "🗓️ Planning", "📝 Nouveau Contrat", "🔑 Retours",
        "🚗 Flotte", "👥 CRM", "🔧 Vidanges", "⚙️ Admin"
    ], label_visibility="collapsed")

# --- ROUTEUR ---
if menu_action == "📊 Dashboard":
    st.markdown("# Tableau de Bord")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Contrats Actifs", len(df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']) if not df_mouvs.empty else 0)
    with c2: st.metric("Véhicules", len(df_voitures))
    with c3:
        today = datetime.now().date()
        ca = 0
        if not df_mouvs.empty and 'Date_Debut' in df_mouvs.columns:
            tmp = df_mouvs.copy()
            tmp['D'] = pd.to_datetime(tmp['Date_Debut'], errors='coerce').dt.date
            ca = tmp[tmp['D'] == today]['Prix'].apply(safe_float).sum()
        st.metric("CA du Jour", f"{ca:,.0f} DT")
    with c4: st.metric("Alertes Vidange", len(df_vidanges[df_vidanges['KM_Recent'].apply(safe_int) - df_vidanges['KM_Dernier_Vidange'].apply(safe_int) > 7500]) if not df_vidanges.empty else 0)
    
    st.markdown("### 🚗 Disponibles")
    dispo = df_voitures.copy()
    if not df_mouvs.empty and not dispo.empty:
        indispo = {safe_str(m.get('Matricule')) for _, m in df_mouvs.iterrows() if safe_str(m.get('Statut_Mouvement')) == 'En cours' and parse_date(m.get('Date_Debut')) <= today <= parse_date(m.get('Date_Fin'))}
        dispo = dispo[~dispo['Matricule'].isin(indispo)]
    if not dispo.empty: st.dataframe(dispo[['Matricule', 'Marque', 'Modèle']], use_container_width=True, hide_index=True)
    else: st.warning("Aucun véhicule dispo.")

elif menu_action == "🗓️ Planning":
    st.markdown("# 🗓️ Planning de la Flotte")
    
    # Navigation temporelle
    if 'planning_offset' not in st.session_state:
        st.session_state.planning_offset = 0
    
    col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 2])
    with col_nav1:
        if st.button("◀ Semaine préc.", key="nav_prev"):
            st.session_state.planning_offset -= 7
            rerun()
    with col_nav2:
        if st.button("Aujourd'hui", key="nav_today"):
            st.session_state.planning_offset = 0
            rerun()
    with col_nav3:
        if st.button("Semaine suiv. ▶", key="nav_next"):
            st.session_state.planning_offset += 7
            rerun()
    with col_nav4:
        nb_jours = st.selectbox("Afficher", [7, 14, 21, 30], index=1, format_func=lambda x: f"{x} jours")
    
    # Calcul des dates
    today = datetime.now().date()
    date_base = today + timedelta(days=st.session_state.planning_offset)
    array_jours = [date_base + timedelta(days=i) for i in range(nb_jours)]
    
    # Construction du HTML du Gantt
    html_gantt = '<div class="gantt-container">'
    
    # Header avec dates
    html_gantt += '<div class="gantt-header">'
    html_gantt += '<div class="gantt-header-cell">Véhicule</div>'
    for j in array_jours:
        is_today = j == today
        day_name = j.strftime("%a").capitalize()
        day_num = j.strftime("%d/%m")
        style = 'color: #e11d48; font-weight: 700;' if is_today else ''
        html_gantt += f'<div class="gantt-header-cell" style="{style}">{day_name}<br>{day_num}</div>'
    html_gantt += '</div>'
    
    # Lignes par véhicule
    if not df_voitures.empty and 'Matricule' in df_voitures.columns:
        for _, car in df_voitures.iterrows():
            immat = safe_str(car.get('Matricule'))
            if not immat: continue
            modele = safe_str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            
            html_gantt += '<div class="gantt-row">'
            html_gantt += f'<div class="gantt-cell"><div><div class="vehicle-label">{modele}</div><div class="vehicle-plate">{immat}</div></div></div>'
            
            # Cells pour chaque jour
            for j in array_jours:
                is_today = j == today
                cell_class = "gantt-cell"
                if is_today:
                    cell_class += " gantt-bar-today"
                html_gantt += f'<div class="{cell_class}"></div>'
            
            # Barres de réservation (positionnées en absolu)
            if not df_mouvs.empty:
                for _, mv in df_mouvs.iterrows():
                    m_v = safe_str(mv.get('Matricule'))
                    if m_v != immat: continue
                    
                    d_deb = parse_date(mv.get('Date_Debut'))
                    d_fin = parse_date(mv.get('Date_Fin'))
                    if not (d_deb and d_fin): continue
                    
                    # Vérifier si la réservation chevauche la période affichée
                    if d_fin < array_jours[0] or d_deb > array_jours[-1]:
                        continue
                    
                    # Calculer la position et la largeur de la barre
                    start_idx = max(0, (d_deb - array_jours[0]).days)
                    end_idx = min(nb_jours - 1, (d_fin - array_jours[0]).days)
                    
                    left_pos = 200 + (start_idx * 80) + 10  # 200px pour la première colonne + offset
                    width = ((end_idx - start_idx + 1) * 80) - 20
                    
                    # Déterminer le type de réservation
                    type_statut = safe_str(mv.get('Type_Statut')).lower()
                    if 'maintenance' in type_statut or 'garage' in type_statut:
                        bar_class = 'gantt-bar-maintenance'
                        icon = '🔧'
                    elif 'réservation' in type_statut:
                        bar_class = 'gantt-bar-reservation'
                        icon = '📅'
                    else:
                        bar_class = 'gantt-bar-location'
                        icon = '🚗'
                    
                    client = safe_str(mv.get('Client'))
                    tooltip = f"{client} | {d_deb.strftime('%d/%m')} → {d_fin.strftime('%d/%m')}"
                    
                    html_gantt += f'<div class="gantt-bar {bar_class}" style="left: {left_pos}px; width: {width}px;" title="{tooltip}">{icon} {client}</div>'
            
            html_gantt += '</div>'
    
    html_gantt += '</div>'
    
    # Légende
    html_gantt += '''
    <div class="gantt-legend">
        <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #e11d48 0%, #be123c 100%);"></div>Location</div>
        <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);"></div>Réservation</div>
        <div class="legend-item"><div class="legend-dot" style="background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);"></div>Maintenance</div>
        <div class="legend-item"><div class="legend-dot" style="border: 2px solid #e11d48; background: rgba(225, 29, 72, 0.1);"></div>Aujourd'hui</div>
    </div>
    '''
    
    st.markdown(html_gantt, unsafe_allow_html=True)

elif menu_action == "📝 Nouveau Contrat":
    st.markdown("# Nouveau Contrat")
    with st.container(border=True):
        col_l, col_r = st.columns(2)
        with col_l:
            nature = st.selectbox("Nature", ["Contrat Location", "Réservation", "Maintenance"])
            vehicule = st.selectbox("Véhicule", liste_vehicules_opt) if liste_vehicules_opt else st.text_input("Véhicule")
            client_b = st.selectbox("Client", liste_clients_opt)
            nom_m = st.text_input("Nom (si manuel)")
            cin_m = st.text_input("CIN (si manuel)")
            permis_m = st.text_input("Permis")
        with col_r:
            c_d1, c_t1 = st.columns(2)
            with c_d1: d1 = st.date_input("Date Début", datetime.now())
            with c_t1: t1 = st.time_input("Heure", time(9, 0))
            c_d2, c_t2 = st.columns(2)
            with c_d2: d2 = st.date_input("Date Fin", datetime.now() + timedelta(days=2))
            with c_t2: t2 = st.time_input("Heure", time(12, 0))
            nbr_jours = max(1, (d2 - d1).days)
            prix_unitaire = st.number_input("Prix / Jour", min_value=0, value=100)
            montant_total = st.number_input("Total", value=nbr_jours * prix_unitaire)
            caution = st.number_input("Caution", value=0)
            
    with st.container(border=True):
        km_debut = st.number_input("KM Départ", value=0)
        l_reception = st.text_input("Lieu", "Siège Monastir")
        info_note = st.text_area("Note")
        c_f1, c_f2 = st.columns(2)
        with c_f1: f_cin = st.file_uploader("Image CIN", type=["png", "jpg", "jpeg"])
        with c_f2: f_permis = st.file_uploader("Image Permis", type=["png", "jpg", "jpeg"])
        
        if st.button("⚡ CRÉER", use_container_width=True):
            with st.spinner("Enregistrement..."):
                nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[0]
                cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "").strip()
                
                if client_b == "-- Entrée manuelle --" and cin_f:
                    insert_row(T_CLIENT, {"Nom": nom_f, "CIN": cin_f, "N° Permis": permis_m, "Image CIN": encoder_image_base64(f_cin), "Image Permis": encoder_image_base64(f_permis)})
                
                ok = insert_row(T_MOUVEMENT, {
                    "Matricule": vehicule, "Type_Statut": "Location" if "Contrat" in nature else nature,
                    "Date_Debut": d1.strftime("%Y-%m-%d"), "Heure_Debut": t1.strftime("%H:%M"),
                    "Date_Fin": d2.strftime("%Y-%m-%d"), "Heure_Fin": t2.strftime("%H:%M"),
                    "Client": nom_f, "Prix": str(montant_total), "Statut_Mouvement": "En cours",
                    "Caution": str(caution), "Reste": str(montant_total - caution), "Lieu_Reception": l_reception,
                    "Info_Note": info_note, "KM_Debut": int(km_debut), "KM_Fin": 0
                })
                if ok:
                    upsert_vidange(vehicule, "", int(km_debut))
                    st.toast("Contrat créé !", icon="✅")
                    st.cache_data.clear()
                    rerun()

elif menu_action == "🔑 Retours":
    st.markdown("# Terminal de Restitution")
    df_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours'] if not df_mouvs.empty and 'Statut_Mouvement' in df_mouvs.columns else pd.DataFrame()
    if not df_actifs.empty:
        choix = [f"{r.get('Matricule')} - {r.get('Client')} (ID:{r.get('id')})" for _, r in df_actifs.iterrows()]
        target_v = st.selectbox("Véhicule", choix)
        id_temp = int(target_v.split("ID:")[1].replace(")", ""))
        res_dep = df_actifs[df_actifs['id'] == id_temp]
        
        c1, c2 = st.columns(2)
        with c1: d_reel = st.date_input("Date retour", datetime.now())
        with c2: t_reel = st.time_input("Heure", datetime.now().time())
        
        km_dep = safe_int(res_dep.iloc[0].get('KM_Debut')) if not res_dep.empty else 0
        km_fin = st.number_input("KM Retour", value=km_dep)
        
        if st.button("✅ Valider Retour", use_container_width=True):
            v_ret = safe_str(res_dep.iloc[0].get('Matricule'))
            update_row(T_MOUVEMENT, {"Statut_Mouvement": "Retourné", "Date_Fin": d_reel.strftime("%Y-%m-%d"), "Heure_Fin": t_reel.strftime("%H:%M"), "KM_Fin": int(km_fin)}, "id", id_temp)
            upsert_vidange(v_ret, "", int(km_fin))
            st.toast("Retour validé !", icon="🔑")
            st.cache_data.clear()
            rerun()

elif menu_action == "🚗 Flotte":
    st.markdown("# Gestion Flotte")
    tab_a, tab_d = st.tabs(["Ajouter", "Supprimer"])
    with tab_a:
        c1, c2 = st.columns(2)
        with c1: mat = st.text_input("Matricule *"); marque = st.text_input("Marque *")
        with c2: modele = st.text_input("Modèle *"); annee = st.text_input("Année", "2026")
        if st.button("Enregistrer"):
            if mat and marque and modele:
                insert_row(T_VEHICULE, {"Matricule": mat, "Marque": marque, "Modèle": modele, "Année": annee})
                upsert_vidange(mat, marque, 0)
                st.toast("Ajouté !", icon="🚗")
                st.cache_data.clear()
                rerun()
    with tab_d:
        if liste_vehicules_opt:
            v_del = st.selectbox("À supprimer", liste_vehicules_opt)
            if st.button("💥 Supprimer"):
                delete_row(T_VEHICULE, "Matricule", v_del)
                delete_row(T_VIDANGE, "Matricule", v_del)
                st.toast("Supprimé.", icon="🗑️")
                st.cache_data.clear()
                rerun()

elif menu_action == "👥 CRM":
    st.markdown("# CRM Clients")
    search = st.text_input("Rechercher (Nom, CIN)")
    if search and not df_clients_light.empty:
        mask = df_clients_light['Nom'].str.contains(search, case=False, na=False) | df_clients_light['CIN'].str.contains(search, case=False, na=False)
        for idx, cli in df_clients_light[mask].iterrows():
            cin_val = safe_str(cli.get('CIN'))
            with st.expander(f"👤 {safe_str(cli.get('Nom')).upper()} (CIN: {cin_val})"):
                details = get_client_details(cin_val)
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Tél:** {cli.get('Numéro de téléphone', 'N/A')}")
                    st.write(f"**Permis:** {cli.get('N° Permis', 'N/A')}")
                with c2:
                    if details and details.get('Image CIN'):
                        try: st.image(base64.b64decode(details.get('Image CIN')), width=200, caption="CIN")
                        except: pass
                if st.button(f"🗑️ Supprimer", key=f"del_{idx}"):
                    delete_row(T_CLIENT, "CIN", cin_val)
                    st.toast("Supprimé", icon="🗑️")
                    st.cache_data.clear()
                    rerun()

elif menu_action == "🔧 Vidanges":
    st.markdown("# Vidanges")
    if not df_vidanges.empty:
        df_v = df_vidanges.copy()
        df_v['KM_circ'] = df_v['KM_Recent'].apply(safe_int) - df_v['KM_Dernier_Vidange'].apply(safe_int)
        df_v['Reste'] = 9000 - df_v['KM_circ']
        def c_v(val):
            if val <= 500: return 'background-color: #7f1d1d; color: #fca5a5;'
            elif val <= 1500: return 'background-color: #78350f; color: #fcd34d;'
            return ''
        cols = [c for c in ['Matricule', 'Marque', 'KM_Dernier_Vidange', 'KM_Recent', 'KM_circ', 'Reste'] if c in df_v.columns]
        try: st.dataframe(df_v[cols].style.map(c_v, subset=['Reste']), use_container_width=True, hide_index=True)
        except: st.dataframe(df_v[cols], use_container_width=True, hide_index=True)
        
        with st.container(border=True):
            v_sel = st.selectbox("Véhicule", df_v['Matricule'].tolist())
            info = df_v[df_v['Matricule'] == v_sel].iloc[0]
            new_km = st.number_input("Nouveau KM", value=safe_int(info.get('KM_Recent')))
            is_done = st.checkbox("Vidange effectuée (Reset)")
            if st.button("Mettre à jour"):
                upd = {"KM_Recent": int(new_km), "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d")}
                if is_done: upd.update({"KM_Dernier_Vidange": int(new_km), "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d")})
                update_row(T_VIDANGE, upd, "Matricule", v_sel)
                st.toast("MAJ !", icon="🔧")
                st.cache_data.clear()
                rerun()

elif menu_action == "⚙️ Admin":
    st.markdown("# ⚠️ Zone Danger")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Purger Mouvements"):
            delete_all(T_MOUVEMENT); st.cache_data.clear(); rerun()
    with c2:
        if st.button("🗑️ Purger Clients"):
            delete_all(T_CLIENT); st.cache_data.clear(); rerun()
