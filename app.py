import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = "https://pwsxxmmlscvazaictocg.supabase.co"
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY", ""))  # À ajouter dans secrets.toml

if not SUPABASE_KEY:
    st.error("❌ Clé API Supabase manquante. Ajoutez SUPABASE_KEY dans les secrets Streamlit.")
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

    /* --- STYLE TABLEAU CONTRATS TYPE IMAGE --- */
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
    </style>
    """, unsafe_allow_html=True)

# --- FONCTIONS UTILITAIRES SUPABASE ---
def executer(table: str, query_type: str = "select", data: dict = None, conditions: dict = None, columns: list = None):
    """
    Fonction unifiée pour les opérations Supabase
    query_type: "select", "insert", "update", "delete"
    """
    try:
        if query_type == "select":
            query = supabase.table(table).select("*")
            if conditions:
                for key, value in conditions.items():
                    query = query.eq(key, value)
            result = query.execute()
            if result.data:
                return pd.DataFrame(result.data)
            return pd.DataFrame()
        
        elif query_type == "insert":
            result = supabase.table(table).insert(data).execute()
            return result.data
        
        elif query_type == "update":
            query = supabase.table(table).update(data)
            if conditions:
                for key, value in conditions.items():
                    query = query.eq(key, value)
            result = query.execute()
            return result.data
        
        elif query_type == "delete":
            query = supabase.table(table).delete()
            if conditions:
                for key, value in conditions.items():
                    query = query.eq(key, value)
            result = query.execute()
            return result.data
        
        elif query_type == "upsert":
            result = supabase.table(table).upsert(data).execute()
            return result.data
    
    except Exception as e:
        st.error(f"Erreur Supabase: {str(e)}")
        return None

def encoder_image_base64(fichier_upload):
    """Encode une image en base64"""
    if fichier_upload is None:
        return None
    try:
        return base64.b64encode(fichier_upload.read()).decode()
    except:
        return None

def recalculer_vidanges():
    """Recalcule les vidanges pour tous les véhicules"""
    try:
        df_vehicules = executer("vehicules", "select")
        if df_vehicules.empty:
            return
        
        for idx, row in df_vehicules.iterrows():
            km_recent = row.get('km_recent', 0)
            km_dernier = row.get('km_dernier_vidange', 0)
            date_derniere = row.get('date_dernier_vidange')
            
            if km_recent is None or km_dernier is None:
                continue
            
            km_diff = km_recent - km_dernier
            jours_depuis = 0
            
            if date_derniere:
                try:
                    date_last = datetime.strptime(str(date_derniere), "%Y-%m-%d").date()
                    jours_depuis = (datetime.now().date() - date_last).days
                except:
                    pass
            
            # Logique de calcul
            jours_recommandes = 365
            km_recommandes = 15000
            
            jours_restants = max(0, jours_recommandes - jours_depuis)
            km_restants = max(0, km_recommandes - km_diff)
            
            # Déterminer le statut
            if km_restants <= 1000 or jours_restants <= 30:
                statut = "🔴 URGENT"
            elif km_restants <= 3000 or jours_restants <= 90:
                statut = "🟠 À PRÉVOIR"
            else:
                statut = "🟢 OK"
            
            executer("vidanges", "update", 
                    {"statut": statut, "km_restant": km_restants, "jours_restant": jours_restants},
                    {"matricule": row.get('matricule')})
    
    except Exception as e:
        st.warning(f"Erreur lors du recalcul: {str(e)}")

# --- INITIALISATION SESSION STATE ---
if "user_info" not in st.session_state:
    st.session_state.user_info = "ADMINISTRATEUR"

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div class="logo-container">
        <h2 style="margin: 0; font-size: 28px;">🏎️ BBNH OS</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👤 Connecté")
    st.info(f"**{st.session_state.user_info}**")
    
    st.divider()
    
    st.markdown("### 📊 Statistiques Rapides")
    
    try:
        df_vehicules = executer("vehicules", "select")
        nb_vehicules = len(df_vehicules) if df_vehicules is not None else 0
        
        df_clients = executer("clients", "select")
        nb_clients = len(df_clients) if df_clients is not None else 0
        
        df_mouvements = executer("mouvements", "select")
        nb_mouvements = len(df_mouvements) if df_mouvements is not None else 0
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("🚗 Véhicules", nb_vehicules)
            st.metric("📋 Mouvements", nb_mouvements)
        with col_s2:
            st.metric("👥 Clients", nb_clients)
    
    except:
        st.warning("Impossible de charger les statistiques")

# --- TABS PRINCIPALES ---
tab_accueil, tab_parc, tab_mouvements, tab_contrats, tab_vidanges, tab_crm, tab_admin = st.tabs([
    "🏠 Accueil",
    "🚗 Parc Véhicules",
    "📦 Mouvements",
    "📄 Contrats",
    "🛢️ Vidanges",
    "👥 CRM",
    "⚙️ Admin"
])

# --- TAB 1 : ACCUEIL ---
with tab_accueil:
    st.title("🏎️ BBNH OS — Système Gestion Premium")
    st.markdown("""
    ### Bienvenue dans votre système de gestion automobile
    
    Gérez efficacement votre flotte avec :
    - ✅ Suivi des véhicules en temps réel
    - ✅ Gestion des mouvements (entrée/sortie)
    - ✅ Suivi des contrats de location
    - ✅ Maintenance et vidanges
    - ✅ Base de données clients
    
    **Version:** 2.0 - Supabase Edition
    """)

# --- TAB 2 : PARC VÉHICULES ---
with tab_parc:
    st.markdown("### 🚗 Gestion du Parc Automobile")
    
    tab_parc_view, tab_parc_add = st.tabs(["📋 Consulter", "➕ Ajouter"])
    
    with tab_parc_view:
        try:
            df_parc = executer("vehicules", "select")
            if not df_parc.empty:
                st.dataframe(df_parc, use_container_width=True, hide_index=True)
                st.success(f"✅ {len(df_parc)} véhicule(s) en base")
            else:
                st.info("Aucun véhicule enregistré")
        except Exception as e:
            st.error(f"Erreur: {e}")
    
    with tab_parc_add:
        st.markdown("#### Ajouter un Nouveau Véhicule")
        with st.form("form_new_vehicule"):
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                matricule = st.text_input("Matricule *")
                marque = st.text_input("Marque")
            with col_v2:
                modele = st.text_input("Modèle")
                annee = st.number_input("Année", min_value=2000, max_value=2050, value=2024)
            
            couleur = st.text_input("Couleur")
            prix_location = st.number_input("Prix Location/Jour (TND)", min_value=0.0, step=5.0)
            
            if st.form_submit_button("⚡ AJOUTER VÉHICULE"):
                if matricule and marque and modele:
                    try:
                        executer("vehicules", "insert", {
                            "matricule": matricule,
                            "marque": marque,
                            "modele": modele,
                            "annee": int(annee),
                            "couleur": couleur,
                            "prix_location": float(prix_location),
                            "km_recent": 0,
                            "km_dernier_vidange": 0,
                            "date_dernier_vidange": datetime.now().strftime("%Y-%m-%d"),
                            "date_creation": datetime.now().strftime("%Y-%m-%d"),
                            "date_mise_a_jour": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.success("✅ Véhicule ajouté avec succès!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.error("Remplissez les champs obligatoires (*)")

# --- TAB 3 : MOUVEMENTS ---
with tab_mouvements:
    st.markdown("### 📦 Gestion des Mouvements")
    
    try:
        df_vehicules = executer("vehicules", "select")
        if df_vehicules is None or df_vehicules.empty:
            st.warning("Aucun véhicule disponible")
        else:
            col_m1, col_m2 = st.columns([2, 1])
            
            with col_m1:
                matricule_mvt = st.selectbox("Sélectionner un véhicule", df_vehicules['matricule'].tolist())
                type_mvt = st.radio("Type de Mouvement", ["Sortie de Parc", "Retour de Parc"], horizontal=True)
                date_mvt = st.date_input("Date du Mouvement", datetime.now())
                km_mvt = st.number_input("Kilométrage", min_value=0, step=1)
                notes = st.text_area("Observations")
            
            with col_m2:
                if st.button("✅ ENREGISTRER MOUVEMENT", use_container_width=True):
                    try:
                        executer("mouvements", "insert", {
                            "matricule": matricule_mvt,
                            "type_mouvement": type_mvt,
                            "date_mouvement": date_mvt.strftime("%Y-%m-%d"),
                            "kilometrage": int(km_mvt),
                            "observations": notes,
                            "date_creation": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.success("✅ Mouvement enregistré!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
            
            st.divider()
            st.markdown("#### 📋 Historique des Mouvements")
            df_mouvements = executer("mouvements", "select")
            if df_mouvements is not None and not df_mouvements.empty:
                st.dataframe(df_mouvements, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun mouvement enregistré")
    
    except Exception as e:
        st.error(f"Erreur: {e}")

# --- TAB 4 : CONTRATS ---
with tab_contrats:
    st.markdown("### 📄 Gestion des Contrats de Location")
    
    try:
        df_vehicules = executer("vehicules", "select")
        df_clients = executer("clients", "select")
        
        if (df_vehicules is None or df_vehicules.empty) or (df_clients is None or df_clients.empty):
            st.warning("⚠️ Assurez-vous d'avoir des véhicules et clients en base")
        else:
            with st.form("form_new_contrat"):
                col_c1, col_c2, col_c3 = st.columns(3)
                
                with col_c1:
                    client_contrat = st.selectbox("Client", df_clients['cin'].tolist() if 'cin' in df_clients.columns else [])
                    vehicule_contrat = st.selectbox("Véhicule", df_vehicules['matricule'].tolist())
                
                with col_c2:
                    date_debut = st.date_input("Date Début", datetime.now())
                    date_fin = st.date_input("Date Fin", datetime.now() + timedelta(days=7))
                
                with col_c3:
                    km_debut = st.number_input("KM Début", min_value=0, step=1)
                    montant = st.number_input("Montant (TND)", min_value=0.0, step=10.0)
                
                if st.form_submit_button("✅ CRÉER CONTRAT"):
                    try:
                        executer("contrats", "insert", {
                            "cin_client": str(client_contrat),
                            "matricule": vehicule_contrat,
                            "date_debut": date_debut.strftime("%Y-%m-%d"),
                            "date_fin": date_fin.strftime("%Y-%m-%d"),
                            "km_debut": int(km_debut),
                            "montant_total": float(montant),
                            "statut": "Actif",
                            "date_creation": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.success("✅ Contrat créé!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
            
            st.divider()
            df_contrats = executer("contrats", "select")
            if df_contrats is not None and not df_contrats.empty:
                st.markdown("#### 📋 Contrats Actifs")
                st.dataframe(df_contrats, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun contrat enregistré")
    
    except Exception as e:
        st.error(f"Erreur: {e}")

# --- TAB 5 : VIDANGES ---
with tab_vidanges:
    st.markdown("### 🛢️ Suivi des Vidanges & Maintenance")
    
    try:
        recalculer_vidanges()
        
        df_vidanges = executer("vidanges", "select")
        if df_vidanges is not None and not df_vidanges.empty:
            st.dataframe(df_vidanges, use_container_width=True, hide_index=True)
        else:
            st.info("Aucune donnée de vidange")
        
        st.divider()
        st.markdown("#### 🔧 Mise à Jour Manuelle")
        
        df_vehicules = executer("vehicules", "select")
        if df_vehicules is not None and not df_vehicules.empty:
            v_select = st.selectbox("Sélectionner véhicule", df_vehicules['matricule'].tolist(), key="vidange_select")
            col_v1, col_v2, col_v3 = st.columns(3)
            
            with col_v1:
                date_vidange = st.date_input("Date Vidange", datetime.now())
                km_vidange = st.number_input("KM Vidange", min_value=0, step=1)
            
            with col_v2:
                km_recent = st.number_input("KM Récent", min_value=0, step=1)
            
            with col_v3:
                if st.button("💾 ENREGISTRER VIDANGE", use_container_width=True):
                    try:
                        executer("vidanges", "update", {
                            "date_dernier_vidange": date_vidange.strftime("%Y-%m-%d"),
                            "km_dernier_vidange": int(km_vidange),
                            "km_recent": int(km_recent),
                            "date_mise_a_jour": datetime.now().strftime("%Y-%m-%d")
                        }, {"matricule": v_select})
                        st.success("✅ Vidange mise à jour!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
    
    except Exception as e:
        st.error(f"Erreur: {e}")

# --- TAB 6 : CRM ---
with tab_crm:
    st.markdown("### 👥 Banque d'Information Clients")
    
    col_crm1, col_crm2 = st.columns([5, 4])
    
    with col_crm1:
        st.markdown("#### 🔍 Consultation")
        search_query = st.text_input("Rechercher (Nom, Prénom, CIN)")
        
        df_clients = executer("clients", "select")
        if df_clients is not None and not df_clients.empty and search_query:
            # Recherche simple (à améliorer avec Supabase full-text search)
            df_filtered = df_clients[
                df_clients.astype(str).apply(lambda x: x.str.contains(search_query, case=False)).any(axis=1)
            ]
            
            if not df_filtered.empty:
                st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun client trouvé")
        elif df_clients is not None and not df_clients.empty:
            st.dataframe(df_clients, use_container_width=True, hide_index=True)
    
    with col_crm2:
        st.markdown("#### ➕ Nouveau Client")
        with st.form("form_new_client"):
            prenom = st.text_input("Prénom *")
            nom = st.text_input("Nom *")
            cin = st.text_input("CIN *")
            tel = st.text_input("Téléphone")
            permis = st.text_input("N° Permis")
            date_cin = st.date_input("Date CIN", datetime.now() - timedelta(days=365))
            date_permis = st.date_input("Date Permis", datetime.now() - timedelta(days=365))
            
            if st.form_submit_button("⚡ CRÉER CLIENT"):
                if prenom and nom and cin:
                    try:
                        executer("clients", "insert", {
                            "prenom": prenom,
                            "nom": nom,
                            "cin": cin,
                            "numero_telephone": tel,
                            "numero_permis": permis,
                            "date_delivrance_cin": date_cin.strftime("%Y-%m-%d"),
                            "date_delivrance_permis": date_permis.strftime("%Y-%m-%d"),
                            "date_creation": datetime.now().strftime("%Y-%m-%d")
                        })
                        st.success("✅ Client créé!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
                else:
                    st.error("Remplissez les champs obligatoires (*)")

# --- TAB 7 : ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Panneau d'Administration")
    st.warning("⚠️ Ces actions sont irréversibles")
    
    col_a1, col_a2, col_a3 = st.columns(3)
    
    with col_a1:
        if st.button("🗑️ PURGER MOUVEMENTS"):
            if st.checkbox("Confirmer purge mouvements"):
                try:
                    executer("mouvements", "delete")
                    st.success("✅ Mouvements purgés")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    with col_a2:
        if st.button("🗑️ RÉINITIALISER CLIENTS"):
            if st.checkbox("Confirmer réinitialisation clients"):
                try:
                    executer("clients", "delete")
                    st.success("✅ Clients réinitialisés")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erreur: {e}")
    
    with col_a3:
        st.markdown("#### 📡 Status Connexion")
        try:
            supabase.table("vehicules").select("matricule").limit(1).execute()
            st.success("✅ Connecté à Supabase")
        except:
            st.error("❌ Erreur de connexion")

st.markdown("---")
st.caption("BBNH OS v2.0 — Gestion Automobile Premium | Powered by Supabase")
