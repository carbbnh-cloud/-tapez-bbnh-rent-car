import streamlit as st
import pandas as pd
import os
import base64
import io
from datetime import datetime, timedelta, time
from supabase import create_client, Client
import json

# ═══════════════════════════════════════════════════════════════════════════
# 🏎️ BBNH OS — SYSTÈME GESTION AUTOMOBILE PREMIUM — ÉDITION SUPABASE
# ═══════════════════════════════════════════════════════════════════════════

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = "https://pwsxxmmlscvazaictocg.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))

if not SUPABASE_KEY:
    st.error("❌ Clé API Supabase manquante. Ajoutez SUPABASE_KEY dans .streamlit/secrets.toml")
    st.stop()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES ---
def encoder_image_base64(file_buffer):
    """Encode une image en base64"""
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except:
        return ""

def formater_heure_propre(valeur_excel):
    """Formate une heure correctement"""
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

# --- FONCTIONS SUPABASE UNIVERSELLES ---
def executer_select(table, conditions=None):
    """Récupère des données avec conditions optionnelles"""
    try:
        query = supabase.table(table).select("*")
        if conditions:
            for key, value in conditions.items():
                query = query.eq(key, value)
        result = query.execute()
        return pd.DataFrame(result.data) if result.data else pd.DataFrame()
    except Exception as e:
        st.error(f"Erreur lecture {table}: {str(e)}")
        return pd.DataFrame()

def executer_insert(table, data):
    """Insère des données"""
    try:
        supabase.table(table).insert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur insertion {table}: {str(e)}")
        return False

def executer_update(table, data, conditions):
    """Met à jour des données"""
    try:
        query = supabase.table(table).update(data)
        for key, value in conditions.items():
            query = query.eq(key, value)
        query.execute()
        return True
    except Exception as e:
        st.error(f"Erreur update {table}: {str(e)}")
        return False

def executer_delete(table, conditions):
    """Supprime des données"""
    try:
        query = supabase.table(table).delete()
        for key, value in conditions.items():
            query = query.eq(key, value)
        query.execute()
        return True
    except Exception as e:
        st.error(f"Erreur suppression {table}: {str(e)}")
        return False

def executer_upsert(table, data):
    """Insert or Replace"""
    try:
        supabase.table(table).upsert(data).execute()
        return True
    except Exception as e:
        st.error(f"Erreur upsert {table}: {str(e)}")
        return False

# --- INITIALISATION SESSION STATE ---
if "user_info" not in st.session_state:
    st.session_state.user_info = "ADMINISTRATEUR"

# --- BARRE LATÉRALE ---
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <h2 style="margin: 0; font-size: 28px;">🏎️ BBNH OS</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👤 Connecté")
    st.info(f"**{st.session_state.user_info}**")
    
    st.divider()
    
    st.markdown("### 📊 STATISTIQUES RAPIDES")
    
    try:
        df_vehicules = executer_select("stock")
        df_clients = executer_select("clients")
        df_mouvements = executer_select("mouvements")
        df_contrats = executer_select("contrats")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("🚗 Véhicules", len(df_vehicules))
            st.metric("📋 Mouvements", len(df_mouvements))
        with col_s2:
            st.metric("👥 Clients", len(df_clients))
            st.metric("📄 Contrats", len(df_contrats))
    except:
        st.warning("Impossible de charger les statistiques")
    
    st.divider()
    
    st.markdown("### 🔧 MENU ACTIONS")
    menu_action = st.radio("", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat", 
        "🚗 Ajouter Véhicule",
        "🗑️ Supprimer Véhicule",
        "⚙️ Modifier Dossier",
        "❌ Supprimer Opération"
    ], label_visibility="collapsed")

# --- TABS PRINCIPALES ---
tab_accueil, tab_vision, tab_contrats, tab_mouvements, tab_stock, tab_clients, tab_vidanges, tab_admin = st.tabs([
    "🏠 Accueil",
    "🔍 Visionneuse",
    "📄 Contrats", 
    "📦 Mouvements",
    "🚗 Stock",
    "👥 Clients",
    "🛢️ Vidanges",
    "⚙️ Admin"
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 : ACCUEIL
# ═══════════════════════════════════════════════════════════════════════════
with tab_accueil:
    st.title("🏎️ BBNH OS — Système Gestion Automobile Premium")
    
    col1, col2, col3 = st.columns(3)
    try:
        df_v = executer_select("stock")
        df_c = executer_select("clients")
        df_m = executer_select("mouvements")
        
        with col1:
            st.metric("Total Véhicules", len(df_v))
        with col2:
            st.metric("Total Clients", len(df_c))
        with col3:
            st.metric("Total Mouvements", len(df_m))
    except:
        st.warning("Erreur chargement données")
    
    st.markdown("""
    ### Bienvenue! 👋
    
    **BBNH OS v2.0 — Édition Supabase**
    
    Système complet de gestion automobile avec:
    - ✅ Gestion des véhicules (Stock)
    - ✅ Base de données clients
    - ✅ Mouvements (Entrée/Sortie)
    - ✅ Contrats de location
    - ✅ Suivi vidanges/maintenance
    - ✅ Reporting avancé
    
    **URL Supabase:** https://pwsxxmmlscvazaictocg.supabase.co
    """)

# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 : VISIONNEUSE - Affichage détaillé
# ═══════════════════════════════════════════════════════════════════════════
with tab_vision:
    st.markdown("### 🔍 Mode Visionneuse")
    
    tab_v_stock, tab_v_clients, tab_v_mouvements, tab_v_contrats = st.tabs(
        ["🚗 Stock", "👥 Clients", "📦 Mouvements", "📄 Contrats"]
    )
    
    # STOCK
    with tab_v_stock:
        st.markdown("#### 🚗 Parc Automobile")
        df_stock = executer_select("stock")
        if not df_stock.empty:
            st.dataframe(df_stock, use_container_width=True, hide_index=True)
            st.success(f"✅ {len(df_stock)} véhicule(s) en parc")
        else:
            st.info("Aucun véhicule enregistré")
    
    # CLIENTS
    with tab_v_clients:
        st.markdown("#### 👥 Banque de Clients")
        df_clients = executer_select("clients")
        if not df_clients.empty:
            st.dataframe(df_clients, use_container_width=True, hide_index=True)
            st.success(f"✅ {len(df_clients)} client(s) en base")
        else:
            st.info("Aucun client enregistré")
    
    # MOUVEMENTS
    with tab_v_mouvements:
        st.markdown("#### 📦 Historique Mouvements")
        df_mvt = executer_select("mouvements")
        if not df_mvt.empty:
            st.dataframe(df_mvt, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun mouvement enregistré")
    
    # CONTRATS
    with tab_v_contrats:
        st.markdown("#### 📄 Contrats Actifs")
        df_ctr = executer_select("contrats")
        if not df_ctr.empty:
            st.dataframe(df_ctr, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun contrat enregistré")

# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 : CONTRATS
# ═══════════════════════════════════════════════════════════════════════════
with tab_contrats:
    st.markdown("### 📄 Gestion des Contrats de Location")
    
    tab_ctr_view, tab_ctr_new, tab_ctr_edit = st.tabs(["📋 Consulter", "➕ Nouveau", "✏️ Modifier"])
    
    # Consulter
    with tab_ctr_view:
        df_contrats = executer_select("contrats")
        if not df_contrats.empty:
            st.dataframe(df_contrats, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun contrat enregistré")
    
    # Créer
    with tab_ctr_new:
        st.markdown("#### ➕ Créer un Nouveau Contrat")
        with st.form("form_new_contrat"):
            df_clients = executer_select("clients")
            df_stock = executer_select("stock")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                num_contrat = st.text_input("N° Contrat *")
                if df_clients is not None and not df_clients.empty:
                    client_sel = st.selectbox("Client *", df_clients['CIN'].tolist() if 'CIN' in df_clients.columns else [])
                    client_nom = df_clients[df_clients['CIN'] == client_sel]['Nom'].values[0] if 'CIN' in df_clients.columns else ""
                else:
                    st.warning("Aucun client disponible")
            
            with col2:
                if df_stock is not None and not df_stock.empty:
                    matricule = st.selectbox("Véhicule *", df_stock['Matricule'].tolist() if 'Matricule' in df_stock.columns else [])
                else:
                    st.warning("Aucun véhicule disponible")
                date_debut = st.date_input("Date Début *", datetime.now())
            
            with col3:
                date_fin = st.date_input("Date Fin *", datetime.now() + timedelta(days=7))
                tarif_jour = st.number_input("Tarif/Jour (TND)", min_value=0.0, step=5.0)
            
            nb_jours = (date_fin - date_debut).days
            montant_total = tarif_jour * nb_jours
            
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                st.metric("Nombre de jours", nb_jours)
            with col_m2:
                st.metric("Montant Total", f"{montant_total:.2f} TND")
            
            if st.form_submit_button("✅ CRÉER CONTRAT"):
                if num_contrat and df_clients is not None and df_stock is not None:
                    new_data = {
                        "Num_Contrat": num_contrat,
                        "Matricule": matricule,
                        "Client_Nom": client_nom,
                        "CIN_Client": client_sel,
                        "Date_Debut": date_debut.strftime("%Y-%m-%d"),
                        "Heure_Debut": "00:00",
                        "Date_Fin": date_fin.strftime("%Y-%m-%d"),
                        "Heure_Fin": "00:00",
                        "Tarif_Jour": str(tarif_jour),
                        "Montant_Total": str(montant_total),
                        "Statut_Contrat": "Actif"
                    }
                    if executer_insert("contrats", new_data):
                        st.success("✅ Contrat créé!")
                        st.rerun()
                    else:
                        st.error("Erreur création contrat")
                else:
                    st.error("Remplissez les champs obligatoires (*)")
    
    # Modifier
    with tab_ctr_edit:
        st.markdown("#### ✏️ Modifier un Contrat")
        df_contrats = executer_select("contrats")
        if not df_contrats.empty and 'Num_Contrat' in df_contrats.columns:
            num_sel = st.selectbox("Sélectionner contrat", df_contrats['Num_Contrat'].tolist())
            contrat = df_contrats[df_contrats['Num_Contrat'] == num_sel].iloc[0]
            
            with st.form("form_edit_contrat"):
                montant = st.number_input("Montant Total", value=float(contrat.get('Montant_Total', 0)))
                statut = st.selectbox("Statut", ["Actif", "Clôturé", "Annulé"], 
                                     index=["Actif", "Clôturé", "Annulé"].index(contrat.get('Statut_Contrat', 'Actif')))
                
                if st.form_submit_button("💾 ENREGISTRER"):
                    if executer_update("contrats", 
                                      {"Montant_Total": str(montant), "Statut_Contrat": statut},
                                      {"Num_Contrat": num_sel}):
                        st.success("✅ Contrat mis à jour!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 : MOUVEMENTS
# ═══════════════════════════════════════════════════════════════════════════
with tab_mouvements:
    st.markdown("### 📦 Gestion des Mouvements")
    
    tab_mvt_view, tab_mvt_new = st.tabs(["📋 Consulter", "➕ Nouveau"])
    
    # Consulter
    with tab_mvt_view:
        df_mouvements = executer_select("mouvements")
        if not df_mouvements.empty:
            st.dataframe(df_mouvements, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun mouvement enregistré")
    
    # Créer
    with tab_mvt_new:
        st.markdown("#### ➕ Enregistrer un Nouveau Mouvement")
        with st.form("form_new_mouvement"):
            df_stock = executer_select("stock")
            df_clients = executer_select("clients")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if df_stock is not None and not df_stock.empty:
                    matricule = st.selectbox("Véhicule *", df_stock['Matricule'].tolist() if 'Matricule' in df_stock.columns else [])
                type_mvt = st.selectbox("Type *", ["Sortie de Parc", "Retour de Parc"])
            
            with col2:
                date_debut = st.date_input("Date Début", datetime.now())
                heure_debut = st.time_input("Heure Début", time(9, 0))
            
            with col3:
                date_fin = st.date_input("Date Fin", datetime.now())
                heure_fin = st.time_input("Heure Fin", time(18, 0))
            
            col_km1, col_km2 = st.columns(2)
            with col_km1:
                km_debut = st.number_input("KM Début", min_value=0, step=1)
            with col_km2:
                km_fin = st.number_input("KM Fin", min_value=0, step=1)
            
            if df_clients is not None and not df_clients.empty:
                client_sel = st.selectbox("Client", ["-- Entrée manuelle --"] + df_clients['CIN'].tolist() if 'CIN' in df_clients.columns else [])
            
            info_note = st.text_area("Notes/Observations")
            
            if st.form_submit_button("✅ CRÉER MOUVEMENT"):
                if df_stock is not None:
                    new_mvt = {
                        "ID": None,
                        "Matricule": matricule,
                        "Type_Statut": type_mvt,
                        "Date_Debut": date_debut.strftime("%Y-%m-%d"),
                        "Heure_Debut": formater_heure_propre(heure_debut),
                        "Date_Fin": date_fin.strftime("%Y-%m-%d"),
                        "Heure_Fin": formater_heure_propre(heure_fin),
                        "Client": client_sel if client_sel != "-- Entrée manuelle --" else "",
                        "Prix": "0",
                        "CHEV": "0",
                        "Statut_Mouvement": "En cours",
                        "Caution": "0",
                        "Reste": "0",
                        "Lieu_Reception": "",
                        "No_Vol": "",
                        "Info_Note": info_note,
                        "KM_Debut": int(km_debut),
                        "KM_Fin": int(km_fin)
                    }
                    if executer_insert("mouvements", new_mvt):
                        st.success("✅ Mouvement enregistré!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 : STOCK
# ═══════════════════════════════════════════════════════════════════════════
with tab_stock:
    st.markdown("### 🚗 Gestion du Stock")
    
    tab_stock_view, tab_stock_add, tab_stock_del = st.tabs(["📋 Consulter", "➕ Ajouter", "🗑️ Supprimer"])
    
    # Consulter
    with tab_stock_view:
        df_stock = executer_select("stock")
        if not df_stock.empty:
            st.dataframe(df_stock, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun véhicule enregistré")
    
    # Ajouter
    with tab_stock_add:
        st.markdown("#### ➕ Ajouter un Véhicule")
        with st.form("form_add_stock"):
            col1, col2, col3 = st.columns(3)
            with col1:
                matricule = st.text_input("Matricule *")
                marque = st.text_input("Marque *")
            with col2:
                modele = st.text_input("Modèle")
                annee = st.text_input("Année")
            with col3:
                marque_modele = st.text_input("Marque/Modèle")
            
            if st.form_submit_button("✅ AJOUTER VÉHICULE"):
                if matricule and marque:
                    new_stock = {
                        "Matricule": matricule,
                        "Marque": marque,
                        "Modèle": modele,
                        "Année": annee,
                        "Marque/Model": marque_modele
                    }
                    if executer_insert("stock", new_stock):
                        st.success("✅ Véhicule ajouté!")
                        st.rerun()
                else:
                    st.error("Remplissez les champs obligatoires (*)")
    
    # Supprimer
    with tab_stock_del:
        st.markdown("#### 🗑️ Supprimer un Véhicule")
        df_stock = executer_select("stock")
        if not df_stock.empty and 'Matricule' in df_stock.columns:
            mat_sel = st.selectbox("Sélectionner véhicule", df_stock['Matricule'].tolist())
            if st.checkbox("Confirmer la suppression"):
                if st.button("🗑️ SUPPRIMER VÉHICULE"):
                    if executer_delete("stock", {"Matricule": mat_sel}):
                        st.success("✅ Véhicule supprimé!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 6 : CLIENTS
# ═══════════════════════════════════════════════════════════════════════════
with tab_clients:
    st.markdown("### 👥 Gestion des Clients")
    
    tab_cli_view, tab_cli_add, tab_cli_edit = st.tabs(["📋 Consulter", "➕ Ajouter", "✏️ Modifier"])
    
    # Consulter
    with tab_cli_view:
        df_clients = executer_select("clients")
        search = st.text_input("Rechercher (Nom, Prénom, CIN)")
        if not df_clients.empty:
            if search:
                df_filtered = df_clients[
                    df_clients.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)
                ]
                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_clients, use_container_width=True, hide_index=True)
        else:
            st.info("Aucun client enregistré")
    
    # Ajouter
    with tab_cli_add:
        st.markdown("#### ➕ Ajouter un Client")
        with st.form("form_add_client"):
            col1, col2 = st.columns(2)
            with col1:
                prenom = st.text_input("Prénom *")
                nom = st.text_input("Nom *")
                cin = st.text_input("CIN *")
                tel = st.text_input("Téléphone")
            with col2:
                permis = st.text_input("N° Permis")
                date_cin = st.date_input("Date Délivrance CIN", datetime.now() - timedelta(days=365))
                date_permis = st.date_input("Date Délivrance Permis", datetime.now() - timedelta(days=365))
            
            if st.form_submit_button("✅ CRÉER CLIENT"):
                if prenom and nom and cin:
                    new_client = {
                        "Prénom": prenom,
                        "Nom": nom,
                        "CIN": cin,
                        "Numéro de téléphone": tel,
                        "N° Permis": permis,
                        "Date Délivrance CIN": date_cin.strftime("%Y-%m-%d"),
                        "Date Délivrance Permis": date_permis.strftime("%Y-%m-%d")
                    }
                    if executer_insert("clients", new_client):
                        st.success("✅ Client créé!")
                        st.rerun()
                else:
                    st.error("Remplissez les champs obligatoires (*)")
    
    # Modifier
    with tab_cli_edit:
        st.markdown("#### ✏️ Modifier un Client")
        df_clients = executer_select("clients")
        if not df_clients.empty and 'CIN' in df_clients.columns:
            cin_sel = st.selectbox("Sélectionner client", df_clients['CIN'].tolist())
            client = df_clients[df_clients['CIN'] == cin_sel].iloc[0]
            
            with st.form("form_edit_client"):
                prenom = st.text_input("Prénom", value=str(client.get('Prénom', '')))
                nom = st.text_input("Nom", value=str(client.get('Nom', '')))
                tel = st.text_input("Téléphone", value=str(client.get('Numéro de téléphone', '')))
                
                if st.form_submit_button("💾 ENREGISTRER"):
                    if executer_update("clients",
                                      {"Prénom": prenom, "Nom": nom, "Numéro de téléphone": tel},
                                      {"CIN": cin_sel}):
                        st.success("✅ Client mis à jour!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 7 : VIDANGES
# ═══════════════════════════════════════════════════════════════════════════
with tab_vidanges:
    st.markdown("### 🛢️ Suivi Vidanges & Maintenance")
    
    df_vidanges = executer_select("vidanges")
    if not df_vidanges.empty:
        st.dataframe(df_vidanges, use_container_width=True, hide_index=True)
    else:
        st.info("Aucune donnée de vidange")
    
    st.divider()
    st.markdown("#### 🔧 Mise à Jour Manuelle Vidange")
    
    df_stock = executer_select("stock")
    if not df_stock.empty and 'Matricule' in df_stock.columns:
        with st.form("form_vidange"):
            col1, col2, col3 = st.columns(3)
            with col1:
                matricule = st.selectbox("Véhicule", df_stock['Matricule'].tolist())
                date_vidange = st.date_input("Date Vidange", datetime.now())
            with col2:
                km_vidange = st.number_input("KM Vidange", min_value=0, step=1)
                km_recent = st.number_input("KM Récent", min_value=0, step=1)
            with col3:
                st.write("")
                if st.form_submit_button("💾 ENREGISTRER VIDANGE"):
                    new_vidange = {
                        "Matricule": matricule,
                        "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"),
                        "Date_Dernier_Vidange": date_vidange.strftime("%Y-%m-%d"),
                        "KM_Dernier_Vidange": int(km_vidange),
                        "KM_Recent": int(km_recent)
                    }
                    if executer_upsert("vidanges", new_vidange):
                        st.success("✅ Vidange mise à jour!")
                        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════
# TAB 8 : ADMIN
# ═══════════════════════════════════════════════════════════════════════════
with tab_admin:
    st.markdown("### ⚙️ Panneau d'Administration")
    st.warning("⚠️ Ces actions sont irréversibles!")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        if st.button("🗑️ PURGER MOUVEMENTS"):
            if st.checkbox("Confirmer purge mouvements", key="chk_mvt"):
                try:
                    # Récupérer tous puis supprimer
                    df = executer_select("mouvements")
                    for _, row in df.iterrows():
                        executer_delete("mouvements", {"ID": row.get('ID')})
                    st.success("✅ Mouvements purgés")
                    st.rerun()
                except:
                    st.error("Erreur purge")
    
    with col_a2:
        if st.button("🗑️ PURGER CONTRATS"):
            if st.checkbox("Confirmer purge contrats", key="chk_ctr"):
                try:
                    df = executer_select("contrats")
                    for _, row in df.iterrows():
                        executer_delete("contrats", {"Num_Contrat": row.get('Num_Contrat')})
                    st.success("✅ Contrats purgés")
                    st.rerun()
                except:
                    st.error("Erreur purge")
    
    with col_a3:
        if st.button("📡 TEST CONNEXION"):
            try:
                supabase.table("stock").select("1").limit(1).execute()
                st.success("✅ Connecté à Supabase")
            except:
                st.error("❌ Erreur de connexion")

# --- FOOTER ---
st.markdown("---")
st.caption("🏎️ BBNH OS v2.0 — Gestion Automobile Premium | Powered by Supabase")
