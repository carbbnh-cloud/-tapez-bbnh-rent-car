import streamlit as st
import pandas as pd
from supabase import create_client, Client
import os
import base64
from datetime import datetime, timedelta, time

if hasattr(st, "rerun"): rerun = st.rerun
elif hasattr(st, "experimental_rerun"): rerun = st.experimental_rerun
else: 
    def rerun(): pass

st.set_page_config(page_title="BBNH OS", layout="wide", page_icon="🏎️", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
html, body, [data-testid="stAppViewContainer"] { font-family: 'Inter', sans-serif !important; background-color: #09090b !important; color: #fafafa !important; }
.main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1800px; }
section[data-testid="stSidebar"] { background-color: #0f0f12 !important; border-right: 1px solid #27272a !important; }
div.stButton > button { background: #e11d48 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 10px 20px !important; font-weight: 600 !important; }
div.stButton > button:hover { background: #be123c !important; transform: translateY(-1px); }
footer {visibility: hidden;} #MainMenu {visibility: hidden;}

/* PLANNING TABLE STYLE */
.planning-table-container {
    background: #0f0f12;
    border-radius: 12px;
    border: 1px solid #27272a;
    overflow: hidden;
}
.planning-header {
    background: #18181b;
    padding: 16px 20px;
    border-bottom: 1px solid #27272a;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.planning-title {
    font-size: 18px;
    font-weight: 700;
    color: #fafafa;
}
.planning-controls {
    display: flex;
    gap: 12px;
    align-items: center;
}
.planning-btn {
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #fafafa !important;
    padding: 6px 14px !important;
    border-radius: 6px !important;
    font-size: 12px !important;
}
.planning-btn:hover {
    background: #3f3f46 !important;
}

/* Table */
.planning-table-wrapper {
    overflow-x: auto;
    max-height: 700px;
    overflow-y: auto;
}
.planning-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 12px;
}
.planning-table th {
    background: #18181b;
    color: #a1a1aa;
    font-weight: 600;
    padding: 12px 8px;
    text-align: center;
    border-bottom: 2px solid #27272a;
    border-right: 1px solid #27272a;
    position: sticky;
    top: 0;
    z-index: 10;
    min-width: 100px;
    white-space: nowrap;
}
.planning-table th:first-child {
    position: sticky;
    left: 0;
    z-index: 11;
    background: #18181b;
    min-width: 220px;
    text-align: left;
    padding-left: 16px;
}
.planning-table td {
    padding: 10px 8px;
    border-bottom: 1px solid #1f1f23;
    border-right: 1px solid #1f1f23;
    text-align: center;
    vertical-align: middle;
}
.planning-table td:first-child {
    position: sticky;
    left: 0;
    background: #0f0f12;
    z-index: 5;
    text-align: left;
    padding-left: 16px;
    border-right: 2px solid #27272a;
}
.planning-table tbody tr:hover td {
    background: rgba(255,255,255,0.02);
}
.planning-table tbody tr:hover td:first-child {
    background: #18181b;
}

/* Vehicle Info */
.vehicle-name {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
    color: #fafafa;
    font-size: 13px;
}
.vehicle-icon {
    font-size: 14px;
}
.vehicle-plate {
    color: #71717a;
    font-size: 11px;
    margin-top: 2px;
}

/* Cell States */
.cell-disponible {
    background: #ffffff;
    color: #1f2937;
    font-weight: 500;
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
}
.cell-disponible::before {
    content: '●';
    color: #6b7280;
    font-size: 8px;
}

.cell-reservation {
    background: linear-gradient(135deg, #16a34a 0%, #15803d 100%);
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    box-shadow: 0 2px 4px rgba(22, 163, 74, 0.3);
}
.cell-reservation::before {
    content: '🕐';
    font-size: 11px;
}

.cell-location {
    background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
    box-shadow: 0 2px 4px rgba(220, 38, 38, 0.3);
}
.cell-location::before {
    content: '🚗';
    font-size: 11px;
}

.cell-maintenance {
    background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%);
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 6px 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 4px;
}
.cell-maintenance::before {
    content: '🔧';
    font-size: 11px;
}

/* Today Column */
.today-column {
    background: rgba(225, 29, 72, 0.1) !important;
}
.today-column th {
    background: #27272a !important;
    color: #e11d48 !important;
    font-weight: 700;
}

/* Legend */
.planning-legend {
    display: flex;
    gap: 24px;
    padding: 16px 20px;
    background: #18181b;
    border-top: 1px solid #27272a;
    font-size: 12px;
    color: #a1a1aa;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
}
.legend-box {
    width: 20px;
    height: 20px;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
}
.legend-box.dispo { background: #ffffff; border: 1px solid #3f3f46; }
.legend-box.resa { background: linear-gradient(135deg, #16a34a 0%, #15803d 100%); color: white; }
.legend-box.loc { background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%); color: white; }
.legend-box.maint { background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%); color: white; }
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
            response = supabase.table(table_name).select("id, Nom, Prénom, CIN, Numéro de téléphone, N° Permis").execute()
        else:
            response = supabase.table(table_name).select("*").execute()
        return pd.DataFrame(response.data) if response.data else pd.DataFrame()
    except: return pd.DataFrame()

def insert_row(table_name, data_dict):
    try:
        clean_data = {k: v for k, v in data_dict.items() if v is not None and not (isinstance(v, float) and pd.isna(v))}
        supabase.table(table_name).insert(clean_data).execute()
        return True
    except: return False

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

# Load data
df_voitures = get_all(T_VEHICULE)
df_clients_light = get_all(T_CLIENT, exclude_heavy=True)
df_mouvs = get_all(T_MOUVEMENT)
df_vidanges = get_all(T_VIDANGE)

def build_liste_vehicules():
    if df_voitures.empty or 'Matricule' not in df_voitures.columns: return []
    return [safe_str(r.get('Matricule')) for _, r in df_voitures.iterrows() if safe_str(r.get('Matricule'))]

liste_vehicules_opt = build_liste_vehicules()

with st.sidebar:
    st.markdown("<h1 style='text-align: center; color: #e11d48; font-weight:800; margin:0;'>BBNH</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #71717a; font-size:12px; letter-spacing:3px; margin-bottom:20px;'>PLANNING</p>", unsafe_allow_html=True)
    st.markdown("---")
    menu_action = st.radio("Navigation", [
        "📊 Dashboard", "🗓️ Planning", "📝 Nouveau Contrat", "🔑 Retours",
        "🚗 Flotte", "👥 CRM", "🔧 Vidanges"
    ], label_visibility="collapsed")

if menu_action == "🗓️ Planning":
    st.markdown("## 🗓️ Planning de la Flotte")
    
    # Controls
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        date_debut = st.date_input("Date de début", datetime.now().date())
    with col2:
        nb_jours = st.selectbox("Nombre de jours", [7, 14, 21, 30], index=1)
    with col3:
        if st.button(" Aujourd'hui"):
            st.session_state.today_clicked = True
            date_debut = datetime.now().date()
    
    # Generate dates
    array_jours = [date_debut + timedelta(days=i) for i in range(nb_jours)]
    today = datetime.now().date()
    
    # Build HTML Table
    html = '<div class="planning-table-container">'
    html += '<div class="planning-header">'
    html += '<div class="planning-title">Planning Flotte BBNH</div>'
    html += '</div>'
    
    html += '<div class="planning-table-wrapper">'
    html += '<table class="planning-table"><thead><tr>'
    html += '<th>Flotte BBNH</th>'
    
    # Date headers
    for j in array_jours:
        is_today = j == today
        day_name = j.strftime("%d/%m")
        day_week = j.strftime("%a").capitalize()
        class_today = "today-column" if is_today else ""
        html += f'<th class="{class_today}">{day_week}<br>{day_name}</th>'
    
    html += '</tr></thead><tbody>'
    
    # Vehicle rows
    if not df_voitures.empty and 'Matricule' in df_voitures.columns:
        for _, car in df_voitures.iterrows():
            immat = safe_str(car.get('Matricule'))
            if not immat: continue
            
            modele = safe_str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            annee = safe_str(car.get('Année', ''))
            
            # Determine icon based on vehicle type
            if 'IBIZA' in modele.upper(): icon = '🚗'
            elif 'PICANTO' in modele.upper(): icon = '🚙'
            elif 'SPORTAGE' in modele.upper(): icon = '🚐'
            elif 'ARONA' in modele.upper(): icon = '🚗'
            elif 'STONIC' in modele.upper(): icon = '🚙'
            else: icon = '🚗'
            
            html += '<tr>'
            html += f'<td><div class="vehicle-name"><span class="vehicle-icon">{icon}</span><div><div>{modele}</div><div class="vehicle-plate">[{immat}]</div></div></div></td>'
            
            # Cells for each day
            for j in array_jours:
                is_today = j == today
                class_today = "today-column" if is_today else ""
                
                # Check if vehicle has a reservation/movement on this day
                cell_content = '<div class="cell-disponible">Disponible</div>'
                
                if not df_mouvs.empty:
                    for _, mv in df_mouvs.iterrows():
                        m_v = safe_str(mv.get('Matricule'))
                        if m_v != immat: continue
                        
                        d_deb = parse_date(mv.get('Date_Debut'))
                        d_fin = parse_date(mv.get('Date_Fin'))
                        if not (d_deb and d_fin): continue
                        
                        # Check if this day is within the reservation period
                        if d_deb <= j <= d_fin:
                            h_deb = safe_str(mv.get('Heure_Debut', '00:00'))
                            h_fin = safe_str(mv.get('Heure_Fin', '00:00'))
                            client = safe_str(mv.get('Client', ''))
                            type_statut = safe_str(mv.get('Type_Statut', '')).lower()
                            
                            if 'maintenance' in type_statut or 'garage' in type_statut:
                                cell_content = f'<div class="cell-maintenance">[{h_deb}→{h_fin}]</div>'
                            elif 'réservation' in type_statut:
                                cell_content = f'<div class="cell-reservation">[{h_deb}→{h_fin}]</div>'
                            else:
                                # Location
                                cell_content = f'<div class="cell-location">[{h_deb}→{h_fin}] {client}</div>'
                            break
                
                html += f'<td class="{class_today}">{cell_content}</td>'
            
            html += '</tr>'
    
    html += '</tbody></table>'
    html += '</div>'
    
    # Legend
    html += '''
    <div class="planning-legend">
        <div class="legend-item"><div class="legend-box dispo"></div> Disponible</div>
        <div class="legend-item"><div class="legend-box resa">🕐</div> Réservation</div>
        <div class="legend-item"><div class="legend-box loc">🚗</div> Location</div>
        <div class="legend-item"><div class="legend-box maint">🔧</div> Maintenance</div>
    </div>
    '''
    
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

elif menu_action == "📊 Dashboard":
    st.markdown("# Tableau de Bord")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Véhicules", len(df_voitures))
    with c2: 
        actifs = len(df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours']) if not df_mouvs.empty and 'Statut_Mouvement' in df_mouvs.columns else 0
        st.metric("Contrats Actifs", actifs)
    with c3: st.metric("Clients", len(df_clients_light))

elif menu_action == "📝 Nouveau Contrat":
    st.markdown("# Nouveau Contrat")
    with st.form("new_contrat"):
        col1, col2 = st.columns(2)
        with col1:
            vehicule = st.selectbox("Véhicule", liste_vehicules_opt)
            client = st.text_input("Client")
            d1 = st.date_input("Date début", datetime.now())
            t1 = st.time_input("Heure début", time(9,0))
        with col2:
            nature = st.selectbox("Nature", ["Location", "Réservation", "Maintenance"])
            prix = st.number_input("Prix total", min_value=0, value=100)
            d2 = st.date_input("Date fin", datetime.now() + timedelta(days=2))
            t2 = st.time_input("Heure fin", time(12,0))
        
        km_debut = st.number_input("KM Départ", value=0)
        
        if st.form_submit_button("✅ Créer"):
            insert_row(T_MOUVEMENT, {
                "Matricule": vehicule,
                "Type_Statut": nature,
                "Date_Debut": d1.strftime("%Y-%m-%d"),
                "Heure_Debut": t1.strftime("%H:%M"),
                "Date_Fin": d2.strftime("%Y-%m-%d"),
                "Heure_Fin": t2.strftime("%H:%M"),
                "Client": client,
                "Prix": str(prix),
                "Statut_Mouvement": "En cours",
                "KM_Debut": km_debut,
                "KM_Fin": 0
            })
            upsert_vidange(vehicule, "", km_debut)
            st.toast("Contrat créé !", icon="✅")
            st.cache_data.clear()
            rerun()

elif menu_action == "🔑 Retours":
    st.markdown("# Terminal de Restitution")
    df_actifs = df_mouvs[df_mouvs['Statut_Mouvement'] == 'En cours'] if not df_mouvs.empty and 'Statut_Mouvement' in df_mouvs.columns else pd.DataFrame()
    
    if not df_actifs.empty:
        choix = [f"{r.get('Matricule')} - {r.get('Client')} (ID:{r.get('id')})" for _, r in df_actifs.iterrows()]
        target = st.selectbox("Véhicule", choix)
        id_temp = int(target.split("ID:")[1].replace(")", ""))
        
        km_fin = st.number_input("KM Retour", value=0)
        
        if st.button("✅ Valider Retour"):
            update_row(T_MOUVEMENT, {"Statut_Mouvement": "Retourné", "KM_Fin": km_fin}, "id", id_temp)
            st.toast("Retour validé !", icon="🔑")
            st.cache_data.clear()
            rerun()

elif menu_action == "🚗 Flotte":
    st.markdown("# Gestion Flotte")
    with st.form("add_vehicle"):
        col1, col2 = st.columns(2)
        with col1:
            mat = st.text_input("Matricule")
            marque = st.text_input("Marque")
        with col2:
            modele = st.text_input("Modèle")
            annee = st.text_input("Année", "2026")
        
        if st.form_submit_button("Ajouter"):
            if mat and marque and modele:
                insert_row(T_VEHICULE, {"Matricule": mat, "Marque": marque, "Modèle": modele, "Année": annee})
                upsert_vidange(mat, marque, 0)
                st.toast("Véhicule ajouté !", icon="🚗")
                st.cache_data.clear()
                rerun()

elif menu_action == "👥 CRM":
    st.markdown("# CRM Clients")
    search = st.text_input("Rechercher")
    if search and not df_clients_light.empty:
        mask = df_clients_light['Nom'].str.contains(search, case=False, na=False)
        st.dataframe(df_clients_light[mask], use_container_width=True)

elif menu_action == "🔧 Vidanges":
    st.markdown("# Vidanges")
    if not df_vidanges.empty:
        st.dataframe(df_vidanges, use_container_width=True)
