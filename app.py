import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

# --- CONFIGURATION SUPABASE ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
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
    @import url(\'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap\');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: \'Plus Jakarta Sans\', sans-serif !important;
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

# --- FONCTION D\'ENCODAGE DES IMAGES EN TEXTE (BASE64) ---
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception as e:
        return ""

# --- FONCTION D\'EXECUTION DES REQUETES SUPABASE ---
def executer(table_name, method, data=None, filters=None, select_cols="*", upsert_on=None):
    try:
        if method == "insert":
            response = supabase.table(table_name).insert(data).execute()
        elif method == "upsert":
            response = supabase.table(table_name).upsert(data, on_conflict=upsert_on).execute()
        elif method == "update":
            query = supabase.table(table_name).update(data)
            if filters:
                for col, op, val in filters:
                    if op == "eq": query = query.eq(col, val)
                    elif op == "like": query = query.like(col, val)
            response = query.execute()
        elif method == "delete":
            query = supabase.table(table_name).delete()
            if filters:
                for col, op, val in filters:
                    if op == "eq": query = query.eq(col, val)
            response = query.execute()
        elif method == "select":
            query = supabase.table(table_name).select(select_cols)
            if filters:
                for col, op, val in filters:
                    if op == "eq": query = query.eq(col, val)
                    elif op == "like": query = query.like(col, val)
                    elif op == "lte": query = query.lte(col, val)
                    elif op == "gte": query = query.gte(col, val)
                    elif op == "not_in": query = query.not_(col, "in", val)
            response = query.execute()
            return pd.DataFrame(response.data)
        
        if response.data:
            return True
        else:
            st.error(f"Erreur Supabase: {response.data}")
            return False
    except Exception as e:
        st.error(f"Erreur Supabase: {e}")
        return False

# --- FONCTION DE PREPARATION DE LA BASE DE DONNEES (CREATION DES TABLES SI ELLES N\'EXISTENT PAS) ---
def preparer_base():
    # Supabase gère la création des tables via son interface ou des migrations.
    # Ici, nous nous assurons que les colonnes nécessaires existent ou sont ajoutées.
    # Pour un déploiement réel, ces tables devraient être créées dans Supabase UI ou via des migrations.
    # Nous allons simuler la vérification et l\'ajout de colonnes si nécessaire.
    
    # Clients table
    # Supabase ne permet pas d\'ajouter des colonnes avec ALTER TABLE directement depuis le client Python de cette manière.
    # Il est préférable de gérer le schéma via l\'interface Supabase ou des migrations.
    # Pour cette conversion, nous allons supposer que les tables existent avec le schéma complet.
    pass

# Initialisation de la base de données (appelée une fois au démarrage de l\'application)
preparer_base()

def formater_heure_propre(valeur_excel):
    if pd.isna(valeur_excel):
        return \'00:00\'
    if isinstance(valeur_excel, (datetime, time)):
        return valeur_excel.strftime(\'%H:%M\')
    val_str = str(valeur_excel).strip()
    if " " in val_str:
        try: val_str = val_str.split(" ")[1]
        except: pass
    parts = val_str.split(":")
    if len(parts) >= 2:
        return f"{parts[0].zfill(2)}:{parts[1].zfill(2)}"
    return \'00:00\'

# Remplacement des appels executer existants
df_voitures = executer("stock", "select")
df_c_list = executer("clients", "select", select_cols="Nom, Prénom, CIN")

liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row['Nom']).upper()} {str(row['Prénom'])} (CIN: {row['CIN']})" for _, row in df_c_list.iterrows()] if not df_c_list.empty else ["-- Entrée manuelle --"]
liste_vehicules_opt = [f"{str(row['Matricule']).strip()}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule']) and str(row['Matricule']).strip().lower() != 'nan'] if not df_voitures.empty else []
liste_vehicules_complets_opt = [f"{str(row['Matricule']).strip()} — {str(row.get('Modèle', row.get('Marque', 'Voiture')))}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule'])] if not df_voitures.empty else []

for _, car in df_voitures.iterrows():
    mat = str(car.get('Matricule', '')).strip()
    marq = str(car.get('Marque', '')).upper()
    if mat and mat.lower() != 'nan':
        # Pour l\'upsert, nous devons spécifier les colonnes à utiliser pour le conflit
        executer("vidanges", "upsert", 
                 data={
                     "Matricule": mat, 
                     "Marque": marq, 
                     "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"), 
                     "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"), 
                     "KM_Dernier_Vidange": 0, 
                     "KM_Recent": 0
                 }, 
                 upsert_on="Matricule")

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
        st.markdown("<h1 style=\'text-align: center; color: #e60000; font-weight:800; margin-bottom:0;\'>BBNH</h1>", unsafe_allow_html=True)
        st.markdown("<p style=\'text-align: center; opacity: 0.5; font-size:13px; letter-spacing:4px; margin-bottom:25px;\'>RENT A CAR</p>", unsafe_allow_html=True)
    
    st.markdown("<h3 style=\'margin-bottom:10px;\'>🕹️ CONSOLE D\'ACTION :</h3>", unsafe_allow_html=True)
    menu_action = st.radio("", [
        "🔍 Mode Visionneuse", 
        "📝 Nouveau Contrat / Réservation", 
        "🚗 Ajouter un Véhicule à la Flotte",
        "🗑️ Supprimer un Véhicule de la Flotte",
        "⚙️ Modifier un Dossier (Contrat / Réservation)",
        "❌ Supprimer une opération"
    ], label_visibility="collapsed")
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.sidebar.expander("📥 IMPORTS EXCEL AUTOMATIQUES", expanded=False):
        f_clients = st.file_uploader("Fichier Clients (BBNH)", type=["xlsx"])
        if f_clients:
            try:
                df_cli = pd.read_excel(f_clients, sheet_name='Base de Données', skiprows=1)
                df_cli = df_cli.loc[:, ~df_cli.columns.str.contains('^Unnamed')]
                # Conversion des noms de colonnes pour correspondre à Supabase si nécessaire
                # Par exemple, '[ID Client]' -> 'ID_Client'
                df_cli.columns = [col.replace(' ', '_').replace('[', '').replace(']', '') for col in df_cli.columns]
                
                # Pour Supabase, nous allons utiliser upsert pour gérer les doublons basés sur CIN
                # Assurez-vous que la table 'clients' dans Supabase a une contrainte d\'unicité sur 'CIN'
                for index, row in df_cli.iterrows():
                    client_data = row.to_dict()
                    # Convertir les dates en format string si elles ne le sont pas déjà
                    for date_col in ['Date_Délivrance_CIN', 'Date_Délivrance_Permis']:
                        if date_col in client_data and pd.notna(client_data[date_col]):
                            client_data[date_col] = pd.to_datetime(client_data[date_col]).strftime("%Y-%m-%d")
                        else:
                            client_data[date_col] = None # Ou une valeur par défaut appropriée
                    
                    # Gérer les images si elles étaient dans le fichier Excel (peu probable pour l\'instant)
                    # Pour l\'instant, nous laissons les champs Image CIN et Image Permis vides ou nulls si non présents
                    client_data['Image_CIN'] = client_data.get('Image_CIN', '')
                    client_data['Image_Permis'] = client_data.get('Image_Permis', '')

                    executer("clients", "upsert", data=client_data, upsert_on="CIN")
                
                st.success("Données clients synchronisées !")
                st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

        f_loc2 = st.file_uploader("Fichier Base LOC2", type=["xlsx"])
        if f_loc2:
            try:
                df_stock = pd.read_excel(f_loc2, sheet_name='Stock')
                df_mouv_raw = pd.read_excel(f_loc2, sheet_name='MOUVEMENTS')
                df_stock = df_stock.loc[:, ~df_stock.columns.str.contains('^Unnamed')]
                df_mouv_raw = df_mouv_raw.loc[:, ~df_mouv_raw.columns.str.contains('^Unnamed')]
                
                # Nettoyage et conversion des colonnes pour df_stock
                df_stock.columns = [col.replace(' ', '_').replace('[', '').replace(']', '') for col in df_stock.columns]
                for index, row in df_stock.iterrows():
                    stock_data = row.to_dict()
                    executer("stock", "upsert", data=stock_data, upsert_on="Matricule")

                # Nettoyage et conversion des colonnes pour df_mouv_raw
                df_mouv_raw.columns = [col.replace(' ', '_').replace('[', '').replace(']', '') for col in df_mouv_raw.columns]
                
                # Renommer les colonnes pour correspondre au schéma Supabase si nécessaire
                df_mouv_raw = df_mouv_raw.rename(columns={
                    'Type_Statut': 'Type_Statut',
                    'Date_Debut': 'Date_Debut',
                    'Heure_Debut': 'Heure_Debut',
                    'Date_Fin': 'Date_Fin',
                    'Heure_Fin': 'Heure_Fin',
                    'Client': 'Client',
                    'Prix': 'Prix',
                    'CHEV': 'CHEV',
                    'Statut_Mouvement': 'Statut_Mouvement',
                    'Caution': 'Caution',
                    'Reste': 'Reste',
                    'Lieu_Reception': 'Lieu_Reception',
                    'No_Vol': 'No_Vol',
                    'Info_Note': 'Info_Note',
                    'KM_Debut': 'KM_Debut',
                    'KM_Fin': 'KM_Fin'
                })

                # Traitement des mouvements
                for index, row in df_mouv_raw.iterrows():
                    mouvement_data = row.to_dict()
                    # Convertir les dates et heures en format string
                    for date_col in ['Date_Debut', 'Date_Fin']:
                        if date_col in mouvement_data and pd.notna(mouvement_data[date_col]):
                            mouvement_data[date_col] = pd.to_datetime(mouvement_data[date_col]).strftime("%Y-%m-%d")
                        else:
                            mouvement_data[date_col] = None
                    for time_col in ['Heure_Debut', 'Heure_Fin']:
                        if time_col in mouvement_data and pd.notna(mouvement_data[time_col]):
                            mouvement_data[time_col] = formater_heure_propre(mouvement_data[time_col])
                        else:
                            mouvement_data[time_col] = '00:00'
                    
                    # Assurez-vous que les valeurs numériques sont du bon type
                    for num_col in ['Prix', 'CHEV', 'Caution', 'Reste', 'KM_Debut', 'KM_Fin']:
                        if num_col in mouvement_data and pd.notna(mouvement_data[num_col]):
                            mouvement_data[num_col] = str(mouvement_data[num_col]) # Supabase peut stocker en TEXT ou NUMBER
                        else:
                            mouvement_data[num_col] = '0'

                    # Supabase gère l\'auto-incrément pour l\'ID, donc nous ne l\'incluons pas dans l\'insert
                    # Si vous avez un ID unique dans votre Excel que vous voulez conserver, utilisez upsert avec cet ID
                    executer("mouvements", "insert", data=mouvement_data)

                st.success("Données de stock et mouvements synchronisées !")
                st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

# --- MODE VISIONNEUSE ---
if menu_action == "🔍 Mode Visionneuse":
    st.markdown("### 📊 Tableau de Bord Général")
    
    tab_planning, tab_contrats, tab_logistique, tab_analytics, tab_vidange, tab_crm, tab_admin = st.tabs([
        "🗓️ CORE PLANNING (365 JOURS)",
        "📄 LISTE DE CONTRAT",
        "🔑 BOX RECEPTION RETOURS",
        "📊 SUIVI DES PERFORMANCES",
        "🔧 SUIVI DES VIDANGES",
        "👥 COMPTE CONDUCTEURS (CRM)",
        "⚙️ PANNEAU DE CONFIGURATION"
    ])

    with tab_planning:
        st.markdown("### 🗓️ Vue Globale & Filtres Intelligents")
        f_col_car, f_col_date_start, f_col_date_target = st.columns([2, 1.5, 1.5])
        with f_col_car:
            options_recherche_voiture = ["-- Toutes les voitures --"] + liste_vehicules_opt
            vehicule_recherche = st.selectbox("🚘 Filtrer par véhicule :", options_recherche_voiture)
        with f_col_date_start:
            date_base = st.date_input("Date de début de la grille :", datetime(2026, 1, 1), key="grid_bbnh_date")
        with f_col_date_target:
            recherche_date = st.date_input("📅 Aller à la date spécifique (Focus) :", datetime(2026, 6, 12))

        array_jours = [date_base + timedelta(days=i) for i in range(365)]
        nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
        df_voitures_valides = executer("stock", "select", filters=[["Matricule", "not_in", ["nan"]]]) if not df_voitures.empty else pd.DataFrame()

        if not df_voitures_valides.empty:
            # Récupérer tous les mouvements pour le planning
            df_mouvements = executer("mouvements", "select")
            if not df_mouvements.empty:
                df_mouvements['Date_Debut'] = pd.to_datetime(df_mouvements['Date_Debut'])
                df_mouvements['Date_Fin'] = pd.to_datetime(df_mouvements['Date_Fin'])

            # Construction de la grille de planning
            planning_data = []
            for _, car in df_voitures_valides.iterrows():
                matricule = car['Matricule']
                row_data = {'Matricule': matricule}
                for day in array_jours:
                    status = "Libre"
                    if not df_mouvements.empty:
                        # Vérifier si la voiture est en mouvement ce jour-là
                        mouvements_jour = df_mouvements[
                            (df_mouvements['Matricule'] == matricule) &
                            (df_mouvements['Date_Debut'] <= day) &
                            (df_mouvements['Date_Fin'] >= day)
                        ]
                        if not mouvements_jour.empty:
                            status = mouvements_jour.iloc[0]['Type_Statut'] # Ou un autre statut pertinent
                    row_data[day.strftime("%d/%m")] = status
                planning_data.append(row_data)
            
            df_planning = pd.DataFrame(planning_data)
            st.dataframe(df_planning, use_container_width=True)

    with tab_contrats:
        st.markdown("### 📄 Liste des Contrats")
        df_contrats = executer("contrats", "select")
        if not df_contrats.empty:
            st.dataframe(df_contrats, use_container_width=True)
        else:
            st.info("Aucun contrat trouvé.")

    with tab_logistique:
        st.markdown("### 🔑 Box Réception Retours")
        # Logique pour la réception des retours
        # Ceci nécessitera des requêtes SELECT et UPDATE sur la table 'mouvements'
        df_mouvements_en_cours = executer("mouvements", "select", filters=[["Statut_Mouvement", "eq", "En cours"]])
        if not df_mouvements_en_cours.empty:
            st.dataframe(df_mouvements_en_cours, use_container_width=True)
            # Ajouter ici la logique pour marquer un mouvement comme terminé
        else:
            st.info("Aucun mouvement en cours.")

    with tab_analytics:
        st.markdown("### 📊 Suivi des Performances")
        # Logique pour l\'analyse des performances
        df_mouvements_termines = executer("mouvements", "select", filters=[["Statut_Mouvement", "eq", "Terminé"]])
        if not df_mouvements_termines.empty:
            st.dataframe(df_mouvements_termines, use_container_width=True)
        else:
            st.info("Aucune donnée de performance disponible.")

    with tab_vidange:
        st.markdown("### 🔧 Tableau de bord de Maintenance & Vidanges Automatisé")
        df_v_base = executer("vidanges", "select")
        if not df_v_base.empty:
            df_v_base['KM_Dernier_Vidange'] = pd.to_numeric(df_v_base['KM_Dernier_Vidange'], errors='coerce').fillna(0).astype(int)
            df_v_base['KM_Recent'] = pd.to_numeric(df_v_base['KM_Recent'], errors='coerce').fillna(0).astype(int)
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
                    v_select = st.selectbox("Sélectionner le véhicule à mettre à jour :", df_v_base['Matricule'].tolist())
                    v_info = df_v_base[df_v_base['Matricule'] == v_select].iloc[0]
                    try: init_date_dernier = datetime.strptime(str(v_info['Date_Dernier_Vidange']), "%Y-%m-%d").date()
                    except: init_date_dernier = datetime.now().date()
                    date_dernier_manuel = st.date_input("Date du Dernier Vidange (Manuel) :", value=init_date_dernier)
                with c_v2:
                    dernier_km_vidange_input = st.number_input("Dernier KM Vidange (Manuel) :", min_value=0, value=int(v_info['KM_Dernier_Vidange']), step=1)
                    nouveau_km_actuel = st.number_input("Kilométrage Actuel / Récent (Manuel) :", min_value=0, value=int(v_info['KM_Recent']), step=1)
                with c_v3:
                    date_effective = st.date_input("Date effective de l\'opération :", datetime.now())
                    action_sync = st.checkbox("Vidange effectuée aujourd\'hui (Synchronise le dernier KM et remet à zéro)", value=False)
                
                if st.button("💾 ENREGISTRER ET RECALCULER DIRECTEMENT", use_container_width=True):
                    date_operation_str = date_effective.strftime("%Y-%m-%d")
                    date_historique_str = date_dernier_manuel.strftime("%Y-%m-%d")
                    if action_sync:
                        executer("vidanges", "update", 
                                 data={
                                     "KM_Recent": int(nouveau_km_actuel), 
                                     "KM_Dernier_Vidange": int(nouveau_km_actuel), 
                                     "Date_Dernier_Vidange": date_operation_str, 
                                     "Date_Mise_A_Jour": date_operation_str
                                 }, 
                                 filters=[["Matricule", "eq", v_select]])
                    else:
                        executer("vidanges", "update", 
                                 data={
                                     "KM_Recent": int(nouveau_km_actuel), 
                                     "KM_Dernier_Vidange": int(dernier_km_vidange_input), 
                                     "Date_Dernier_Vidange": date_historique_str, 
                                     "Date_Mise_A_Jour": date_operation_str
                                 }, 
                                 filters=[["Matricule", "eq", v_select]])
                    st.success("Calculs mis à jour instantanément !")
                    st.rerun()

    with tab_crm:
        st.markdown("### 👥 Banque d\'Information des Conducteurs & Profils Clients")
        c1, c2 = st.columns([5, 4])
        
        with c1:
            st.markdown("#### 🔍 Consultation & Actions")
            search_query = st.text_input("Rechercher un profil (Nom, Prénom, CIN) :", key="crm_search_field")
            
            if search_query:
                clients_trouves = executer("clients", "select", 
                                           filters=[["Nom", "like", f"%{search_query}%"], 
                                                    ["Prénom", "like", f"%{search_query}%"], 
                                                    ["CIN", "like", f"%{search_query}%"]])
                
                if not clients_trouves.empty:
                    for idx, cli in clients_trouves.iterrows():
                        cin_client_actuel = str(cli['CIN']).strip()
                        unique_suffix = f"{idx}_{cin_client_actuel}"
                        
                        with st.expander(f"👤 {str(cli['Nom']).upper()} {cli['Prénom']} (CIN: {cin_client_actuel})", expanded=True):
                            st.write(f"**📞 Téléphone :** `{cli.get('Numéro_de_téléphone', 'N/A')}` | **🚗 N° Permis :** `{cli.get('N°_Permis', 'N/A')}`")
                            st.write(f"📅 **Délivrance CIN :** `{cli.get('Date_Délivrance_CIN', 'N/A')}` | 📅 **Délivrance Permis :** `{cli.get('Date_Délivrance_Permis', 'N/A')}`")
                            
                            col_img1, col_img2 = st.columns(2)
                            with col_img1:
                                if cli.get('Image_CIN'):
                                    try: st.image(base64.b64decode(cli['Image_CIN']), caption="Pièce d\'identité (CIN)", use_container_width=True)
                                    except: pass
                            with col_img2:
                                if cli.get('Image_Permis'):
                                    try: st.image(base64.b64decode(cli['Image_Permis']), caption="Permis de conduire", use_container_width=True)
                                    except: pass
                            
                            st.markdown("---")
                            col_btn_mod, col_btn_sup = st.columns(2)
                            
                            with col_btn_mod:
                                if st.button(f"✏️ MODIFIER CE PROFIL", key=f"btn_edit_{unique_suffix}"):
                                    st.session_state[f"mode_edition_{unique_suffix}"] = True
                            
                            with col_btn_sup:
                                check_sup = st.checkbox("Confirmer la suppression", key=f"chk_del_{unique_suffix}")
                                if st.button(f"🗑️ SUPPRIMER CE CLIENT", key=f"btn_del_{unique_suffix}"):
                                    if check_sup:
                                        executer("clients", "delete", filters=[["CIN", "eq", cin_client_actuel]])
                                        st.success(f"Client [CIN: {cin_client_actuel}] supprimé définitivement.")
                                        st.rerun()
                                    else:
                                        st.warning("Veuillez cocher la case de confirmation avant de supprimer.")
                            
                            if st.session_state.get(f"mode_edition_{unique_suffix}", False):
                                st.markdown("<br>", unsafe_allow_html=True)
                                with st.form(key=f"form_reel_edit_{unique_suffix}"):
                                    st.markdown("##### 📝 Édition des informations")
                                    e_prenom = st.text_input("Prénom", value=str(cli['Prénom']))
                                    e_nom = st.text_input("Nom", value=str(cli['Nom']))
                                    e_tel = st.text_input("Téléphone", value=str(cli.get('Numéro_de_téléphone', '')))
                                    e_permis = st.text_input("N° Permis", value=str(cli.get('N°_Permis', '')))
                                    
                                    try: e_init_d_cin = datetime.strptime(str(cli.get('Date_Délivrance_CIN')), "%Y-%m-%d").date()
                                    except: e_init_d_cin = datetime.now().date()
                                    try: e_init_d_per = datetime.strptime(str(cli.get('Date_Délivrance_Permis')), "%Y-%m-%d").date()
                                    except: e_init_d_per = datetime.now().date()
                                        
                                    e_d_cin = st.date_input("Date Délivrance CIN", value=e_init_d_cin)
                                    e_d_per = st.date_input("Date Délivrance Permis", value=e_init_d_per)
                                    
                                    f_cin_remplace = st.file_uploader("Remplacer l\'image CIN (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_cin_{unique_suffix}")
                                    f_per_remplace = st.file_uploader("Remplacer l\'image Permis (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_per_{unique_suffix}")
                                    
                                    if st.form_submit_button("✅ METTRE À JOUR"):
                                        update_data = {
                                            "Prénom": e_prenom, 
                                            "Nom": e_nom, 
                                            "Numéro_de_téléphone": e_tel, 
                                            "N°_Permis": e_permis, 
                                            "Date_Délivrance_CIN": e_d_cin.strftime("%Y-%m-%d"), 
                                            "Date_Délivrance_Permis": e_d_per.strftime("%Y-%m-%d")
                                        }
                                        
                                        if f_cin_remplace:
                                            update_data["Image_CIN"] = encoder_image_base64(f_cin_remplace)
                                        if f_per_remplace:
                                            update_data["Image_Permis"] = encoder_image_base64(f_per_remplace)
                                            
                                        executer("clients", "update", data=update_data, filters=[["CIN", "eq", cin_client_actuel]])
                                        st.success("Profil mis à jour !")
                                        st.session_state[f"mode_edition_{unique_suffix}"] = False
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
                        client_new_data = {
                            "Prénom": n_prenom, 
                            "Nom": n_nom, 
                            "CIN": n_cin, 
                            "Numéro_de_téléphone": n_tel, 
                            "N°_Permis": n_permis, 
                            "Date_Délivrance_CIN": n_d_cin.strftime("%Y-%m-%d"), 
                            "Date_Délivrance_Permis": n_d_per.strftime("%Y-%m-%d"), 
                            "Image_CIN": encoder_image_base64(f_cin_new), 
                            "Image_Permis": encoder_image_base64(f_per_new)
                        }
                        executer("clients", "upsert", data=client_new_data, upsert_on="CIN")
                        st.success("Nouveau client enregistré !")
                        st.rerun()
                    else:
                        st.error("Veuillez remplir les champs obligatoires (*)")

    with tab_admin:
        st.markdown("### ⚙️ Panneau de Configuration Système")
        st.warning("Attention : Ces actions sont irréversibles.")
        
        col_a1, col_a2 = st.columns(2)
        with col_a1:
            if st.button("🗑️ PURGER TOUS LES MOUVEMENTS"):
                if st.checkbox("Confirmer la purge des mouvements"):
                    executer("mouvements", "delete", filters=[]) # Supprime toutes les lignes
                    st.success("Tous les mouvements ont été effacés.")
                    st.rerun()
        with col_a2:
            if st.button("🗑️ RÉINITIALISER LA BASE CLIENTS"):
                if st.checkbox("Confirmer la purge des clients"):
                    executer("clients", "delete", filters=[]) # Supprime toutes les lignes
                    st.success("La base clients a été réinitialisée.")
                    st.rerun()

# --- NOUVEAU CONTRAT / RÉSERVATION ---
elif menu_action == "📝 Nouveau Contrat / Réservation":
    st.markdown("### 📝 Création de Fiche : Contrat / Réservation / Maintenance")
    with st.form("form_bbnh_new_contract"):
        c1, c2, c3 = st.columns(3)
        with c1: nature = st.selectbox("Nature de l\'opération :", ["Location", "Réservation", "Maintenance / Garage"])
        with c2: vehicule = st.selectbox("Véhicule concerné :", liste_vehicules_opt)
        with c3: text_type = st.text_input("Type de statut (Ex: Contrat, Réservation) :", value=nature)

        st.markdown("---<br>", unsafe_allow_html=True)
        st.markdown("#### 👤 Informations Conducteur")
        client_selection = st.selectbox("Sélectionner un client existant ou créer un nouveau :", liste_clients_opt)

        if client_selection == "-- Entrée manuelle --":
            nom_f = st.text_input("Nom & Prénom du Conducteur :")
            cin_f = st.text_input("N° CIN :")
            dc = st.date_input("Date de Délivrance CIN :", value=datetime.now() - timedelta(days=365))
            permis_m = st.text_input("N° Permis de Conduire :")
            dp = st.date_input("Date de Délivrance Permis :", value=datetime.now() - timedelta(days=365))
            f_cin = st.file_uploader("Fichier CIN :", type=["png", "jpg", "jpeg", "pdf"])
            f_permis = st.file_uploader("Fichier Permis :", type=["png", "jpg", "jpeg", "pdf"])
            img_cin_b64 = encoder_image_base64(f_cin)
            img_permis_b64 = encoder_image_base64(f_permis)
        else:
            cin_f = client_selection.split("CIN: ")[1].replace(")", "")
            client_data = executer("clients", "select", filters=[["CIN", "eq", cin_f]])
            if not client_data.empty:
                nom_f = f"{client_data.iloc[0]['Nom']} {client_data.iloc[0]['Prénom']}"
                dc = datetime.strptime(client_data.iloc[0]['Date_Délivrance_CIN'], "%Y-%m-%d").date() if client_data.iloc[0]['Date_Délivrance_CIN'] else datetime.now().date()
                permis_m = client_data.iloc[0]['N°_Permis']
                dp = datetime.strptime(client_data.iloc[0]['Date_Délivrance_Permis'], "%Y-%m-%d").date() if client_data.iloc[0]['Date_Délivrance_Permis'] else datetime.now().date()
                img_cin_b64 = client_data.iloc[0]['Image_CIN']
                img_permis_b64 = client_data.iloc[0]['Image_Permis']
            else:
                nom_f, cin_f, dc, permis_m, dp, img_cin_b64, img_permis_b64 = "", "", datetime.now().date(), "", datetime.now().date(), "", ""

        st.markdown("---<br>", unsafe_allow_html=True)
        c_d1, c_t1 = st.columns(2)
        with c_d1: d1 = st.date_input("Date Début :", datetime.now())
        with c_t1: t1 = st.time_input("Heure Début :", time(9, 0))
        c_d2, c_t2 = st.columns(2)
        with c_d2: d2 = st.date_input("Date Fin :", datetime.now() + timedelta(days=1))
        with c_t2: t2 = st.time_input("Heure Fin / Retour :", time(12, 0))

        nbr_jours = (d2 - d1).days
        if nbr_jours <= 0: nbr_jours = 1
        st.markdown(f"**🔢 Durée recalculée :** `{nbr_jours} jour(s)`")

        prix_unitaire = st.number_input("💰 Prix Unitaire / Jour (DT) :", min_value=0, value=100)
        montant_total = nbr_jours * prix_unitaire
        prix = st.number_input("Prix Total Évalué (DT) :", value=montant_total)
        caution = st.number_input("Caution (DT) :", value=0)
        reste = prix - caution
        st.markdown(f"**🔴 Reste à payer recalculé :** `{reste} DT`")

        st.markdown("---<br>", unsafe_allow_html=True)
        lieu_reception = st.text_input("Lieu de Réception :", value="Siège Monastir")
        no_vol = st.text_input("N° Vol :")
        km_debut = st.number_input("Kilométrage Départ :", min_value=0, value=0)
        info_note = st.text_area("Note Interne :")

        if st.form_submit_button("⚡ CRÉER LA FICHE"):
            str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
            str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
            
            # Upsert client data
            client_data_to_save = {
                "Prénom": nom_f.split(' ')[1] if ' ' in nom_f else '',
                "Nom": nom_f.split(' ')[0] if ' ' in nom_f else nom_f,
                "CIN": cin_f,
                "Date_Délivrance_CIN": dc.strftime("%Y-%m-%d"),
                "N°_Permis": permis_m,
                "Date_Délivrance_Permis": dp.strftime("%Y-%m-%d"),
                "Image_CIN": img_cin_b64,
                "Image_Permis": img_permis_b64
            }
            executer("clients", "upsert", data=client_data_to_save, upsert_on="CIN")

            # Insert into contrats if nature is Contrat
            if "Contrat" in nature:
                # Générer un Num_Contrat unique, par exemple basé sur un timestamp ou un UUID
                num_contrat = f"CONTRAT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                contract_data = {
                    "Num_Contrat": num_contrat,
                    "Matricule": vehicule,
                    "Client_Nom": nom_f,
                    "CIN_Client": cin_f,
                    "Date_Debut": str_d1,
                    "Heure_Debut": str_t1,
                    "Date_Fin": str_d2,
                    "Heure_Fin": str_t2,
                    "Tarif_Jour": str(prix_unitaire),
                    "Montant_Total": str(montant_total),
                    "Statut_Contrat": "Actif"
                }
                executer("contrats", "insert", data=contract_data)

            # Insert into mouvements
            mouvement_data = {
                "Matricule": vehicule,
                "Type_Statut": text_type,
                "Date_Debut": str_d1,
                "Heure_Debut": str_t1,
                "Date_Fin": str_d2,
                "Heure_Fin": str_t2,
                "Client": nom_f,
                "Prix": str(montant_total),
                "CHEV": '0',
                "Statut_Mouvement": 'En cours',
                "Caution": str(caution),
                "Reste": str(reste),
                "Lieu_Reception": lieu_reception,
                "No_Vol": no_vol,
                "Info_Note": info_note,
                "KM_Debut": int(km_debut),
                "KM_Fin": 0
            }
            executer("mouvements", "insert", data=mouvement_data)

            # Update vidanges
            executer("vidanges", "update", 
                     data={
                         "KM_Recent": int(km_debut), 
                         "Date_Mise_A_Jour": str_d1
                     }, 
                     filters=[["Matricule", "eq", vehicule]])
            
            st.success("Fiche créée avec succès !")
            st.rerun()

# --- AJOUTER UN VÉHICULE À LA FLOTTE ---
elif menu_action == "🚗 Ajouter un Véhicule à la Flotte":
    with st.sidebar.form("form_bbnh_add_car"):
        st.markdown("### 🚗 Nouveau Véhicule")
        nouveau_matricule = st.text_input("Matricule / Plaque * :").strip()
        nouvelle_marque = st.text_input("Marque * :").strip()
        nouveau_modele = st.text_input("Modèle * :").strip()
        nouvelle_annee = st.text_input("Année :", value="2026").strip()
        
        if st.form_submit_button("⚡ ENREGISTRER LE VEHICULE"):
            if nouveau_matricule and nouvelle_marque and nouveau_modele:
                combinaison_modele = f"{nouvelle_marque} {nouveau_modele}"
                car_data = {
                    "Matricule": nouveau_matricule, 
                    "Marque": nouvelle_marque, 
                    "Modèle": nouveau_modele, 
                    "Année": nouvelle_annee, 
                    "Marque/Model": combinaison_modele
                }
                executer("stock", "upsert", data=car_data, upsert_on="Matricule")
                
                vidange_data = {
                    "Matricule": nouveau_matricule, 
                    "Marque": nouvelle_marque.upper(), 
                    "Date_Mise_A_Jour": datetime.now().strftime("%Y-%m-%d"), 
                    "Date_Dernier_Vidange": datetime.now().strftime("%Y-%m-%d"),
                    "KM_Dernier_Vidange": 0,
                    "KM_Recent": 0
                }
                executer("vidanges", "upsert", data=vidange_data, upsert_on="Matricule")
                st.success("Véhicule enregistré !")
                st.rerun()

# --- SUPPRIMER UN VÉHICULE DE LA FLOTTE ---
elif menu_action == "🗑️ Supprimer un Véhicule de la Flotte":
    if liste_vehicules_complets_opt:
        with st.sidebar.form("form_bbnh_delete_car"):
            vehicule_a_retirer = st.selectbox("Choisir le véhicule à supprimer :", liste_vehicules_complets_opt)
            confirmer_suppression = st.checkbox("Confirmer la suppression définitive")
            if st.form_submit_button("💥 SUPPRIMER LE VÉHICULE"):
                if confirmer_suppression:
                    matricule_pure = str(vehicule_a_retirer).split(" — ")[0].strip()
                    executer("stock", "delete", filters=[["Matricule", "eq", matricule_pure]])
                    executer("vidanges", "delete", filters=[["Matricule", "eq", matricule_pure]])
                    st.success("Véhicule retiré.")
                    st.rerun()

# --- MODIFIER UN DOSSIER (CONTRAT/RÉSERVATION) ---
elif menu_action == "⚙️ Modifier un Dossier (Contrat / Réservation)":
    df_mouv_actifs = executer("mouvements", "select", filters=[["Statut_Mouvement", "eq", "En cours"]])
    if not df_mouv_actifs.empty:
        liste_mouv_mod = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouv_actifs.iterrows()]
        mouv_selectionne = st.sidebar.selectbox("Sélectionner le dossier à éditer :", liste_mouv_mod)
        id_to_edit = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
        row_init = df_mouv_actifs[df_mouv_actifs['ID'] == id_to_edit].iloc[0]
        
        df_cli_spec = executer("clients", "select", filters=[["Nom", "eq", str(row_init['Client'])]])
        row_cli_init = df_cli_spec.iloc[0] if not df_cli_spec.empty else {}
        
        try: init_date_deb = datetime.strptime(str(row_init['Date_Debut']), "%Y-%m-%d").date()
        except: init_date_deb = datetime.now().date()
        try: init_date_fin = datetime.strptime(str(row_init['Date_Fin']), "%Y-%m-%d").date()
        except: init_date_fin = datetime.now().date()
        try: init_time_deb = datetime.strptime(formater_heure_propre(row_init['Heure_Debut']), "%H:%M").time()
        except: init_time_deb = time(9, 0)
        try: init_time_fin = datetime.strptime(formater_heure_propre(row_init['Heure_Fin']), "%H:%M").time()
        except: init_time_fin = time(12, 0)
        
        try: init_date_cin = datetime.strptime(str(row_cli_init.get('Date_Délivrance_CIN')), "%Y-%m-%d").date()
        except: init_date_cin = datetime.now().date()
        try: init_date_permis = datetime.strptime(str(row_cli_init.get('Date_Délivrance_Permis')), "%Y-%m-%d").date()
        except: init_date_permis = datetime.now().date()
        
        st.sidebar.markdown(f"### ⚙️ Édition Totale du Dossier #{id_to_edit}")
        mod_nature = st.sidebar.selectbox("Changer de Nature :", ["Location", "Réservation", "Maintenance / Garage"], index=["location", "réservation", "maintenance / garage"].index(str(row_init['Type_Statut']).lower()) if str(row_init['Type_Statut']).lower() in ["location", "réservation", "maintenance / garage"] else 0)
        idx_v_init = liste_vehicules_opt.index(str(row_init['Matricule']).strip()) if str(row_init['Matricule']).strip() in liste_vehicules_opt else 0
        mod_vehicule = st.sidebar.selectbox("Changer de véhicule :", liste_vehicules_opt, index=idx_v_init)
        
        st.sidebar.markdown("👤 **Informations Conducteur**")
        mod_client = st.sidebar.text_input("Nom & Prénom du Conducteur :", value=str(row_init['Client']))
        mod_cin = st.sidebar.text_input("N° CIN :", value=str(row_cli_init.get('CIN', '')))
        mod_date_cin = st.sidebar.date_input("Date de Délivrance CIN :", init_date_cin)
        mod_permis = st.sidebar.text_input("N° Permis de Conduire :", value=str(row_cli_init.get('N°_Permis', '')))
        mod_date_permis = st.sidebar.date_input("Date de Délivrance Permis :", init_date_permis)
        mod_f_cin = st.sidebar.file_uploader("Remplacer le fichier CIN :", type=["png", "jpg", "jpeg", "pdf"])
        mod_f_permis = st.sidebar.file_uploader("Remplacer le fichier Permis :", type=["png", "jpg", "jpeg", "pdf"])
        
        st.sidebar.markdown("---")
        c_d1, c_t1 = st.sidebar.columns(2)
        with c_d1: mod_d1 = st.sidebar.date_input("Date Début :", init_date_deb, key="mod_d1")
        with c_t1: mod_t1 = st.sidebar.time_input("Heure Début :", init_time_deb, key="mod_t1")
        c_d2, c_t2 = st.sidebar.columns(2)
        with c_d2: mod_d2 = st.sidebar.date_input("Date Fin :", init_date_fin, key="mod_d2")
        with c_t2: mod_t2 = st.sidebar.time_input("Heure Fin / Retour :", init_time_fin, key="mod_t2")
        
        mod_nbr_jours = (mod_d2 - mod_d1).days
        if mod_nbr_jours <= 0:
            mod_nbr_jours = 1
        st.sidebar.markdown(f"**🔢 Durée recalculée :** `{mod_nbr_jours} jour(s)`")
        
        df_contrat_spec = executer("contrats", "select", select_cols="Tarif_Jour", filters=[["Num_Contrat", "eq", str(id_to_edit)]])
        init_tarif_unitaire = 100
        if not df_contrat_spec.empty:
            try: init_tarif_unitaire = int(float(df_contrat_spec.iloc[0]['Tarif_Jour']))
            except: pass
            
        mod_prix_unitaire = st.sidebar.number_input("💰 Prix Unitaire / Jour (DT) :", min_value=0, value=init_tarif_unitaire, key="mod_pu")
        mod_total_auto = mod_nbr_jours * mod_prix_unitaire
        
        mod_prix = st.sidebar.number_input("Prix Total Évalué (DT) :", value=int(mod_total_auto), key="mod_tot")
        mod_caution = st.sidebar.number_input("Caution (DT) :", value=int(float(str(row_init['Caution']).replace(' ','')) or 0), key="mod_cau")
        mod_reste = mod_prix - mod_caution
        st.sidebar.markdown(f"**🔴 Reste à payer recalculé :** `{mod_reste} DT`")
        
        st.sidebar.markdown("---")
        mod_lieu = st.sidebar.text_input("Lieu de Réception :", value=str(row_init.get('Lieu_Reception', 'Siège Monastir')))
        mod_vol = st.sidebar.text_input("N° Vol :", value=str(row_init.get('No_Vol', '')))
        mod_km_deb = st.sidebar.number_input("Kilométrage Départ :", min_value=0, value=int(row_init.get('KM_Debut', 0)))
        mod_note = st.sidebar.text_area("Note Interne :", value=str(row_init.get('Info_Note', '')))
        
        if st.sidebar.button("💾 ENREGISTRER ABSOLUMENT TOUT"):
            str_mod_d1, str_mod_d2 = mod_d1.strftime("%Y-%m-%d"), mod_d2.strftime("%Y-%m-%d")
            str_mod_t1, str_mod_t2 = mod_t1.strftime("%H:%M"), mod_t2.strftime("%H:%M")
            
            if mod_f_cin:
                executer("clients", "update", data={
                    "Image_CIN": encoder_image_base64(mod_f_cin)
                }, filters=[["CIN", "eq", mod_cin]])
            if mod_f_permis:
                executer("clients", "update", data={
                    "Image_Permis": encoder_image_base64(mod_f_permis)
                }, filters=[["CIN", "eq", mod_cin]])
            
            executer("clients", "update", 
                     data={
                         "Nom": mod_client.split(' ')[0] if ' ' in mod_client else mod_client,
                         "Prénom": mod_client.split(' ')[1] if ' ' in mod_client else '',
                         "Date_Délivrance_CIN": mod_date_cin.strftime("%Y-%m-%d"), 
                         "N°_Permis": mod_permis, 
                         "Date_Délivrance_Permis": mod_date_permis.strftime("%Y-%m-%d")
                     }, 
                     filters=[["CIN", "eq", mod_cin]])
            
            executer("mouvements", "update", 
                     data={
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
                     }, 
                     filters=[["ID", "eq", id_to_edit]])
            
            executer("vidanges", "update", 
                     data={
                         "KM_Recent": int(mod_km_deb), 
                         "Date_Mise_A_Jour": str_mod_d1
                     }, 
                     filters=[["Matricule", "eq", mod_vehicule]])
            st.success("Toutes les données ont été mises à jour avec succès !")
            st.rerun()

# --- SUPPRIMER UNE OPÉRATION ---
elif menu_action == "❌ Supprimer une opération":
    df_mouv_actifs = executer("mouvements", "select", filters=[["Statut_Mouvement", "eq", "En cours"]])
    if not df_mouv_actifs.empty:
        liste_mouv_del = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouv_actifs.iterrows()]
        with st.sidebar.form("form_bbnh_delete_mouv"):
            mouv_selectionne = st.selectbox("Choisir l\'opération à détruire :", liste_mouv_del)
            confirmer_action = st.checkbox("Confirmer la suppression")
            if st.form_submit_button("💥 RETIRER DU PLANNING"):
                if confirmer_action:
                    id_to_delete = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
                    executer("mouvements", "delete", filters=[["ID", "eq", id_to_delete]])
                    st.success("Opération effacée !")
                    st.rerun()

# =========================================================================
# ESPACE CENTRAL DE TRAVAIL INTERACTIF
# =========================================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION</h1>", unsafe_allow_html=True)

# --- RECHERCHE AVANCÉE PAR PÉRIODE ---
with st.container(border=True):
    st.markdown("### 🔎 RECHERCHE AVANCÉE : VOITURES DISPONIBLES PAR PÉRIODE")
    c_search1, c_search2, c_search3 = st.columns([2, 2, 1.5])
    
    with c_search1:
        search_date_debut = st.date_input("📅 Date de Sortie souhaitée :", datetime.now(), key="adv_search_start")
    with c_search2:
        search_date_fin = st.date_input("📅 Date de Retour prévue :", datetime.now() + timedelta(days=3), key="adv_search_end")
    with c_search3:
        st.markdown("<div style=\'height:28px;\'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")
        
        if search_date_debut > search_date_fin:
            st.error("⚠️ La date de sortie ne peut pas être supérieure à la date de retour.")
        else:
            # Récupérer les mouvements qui chevauchent la période de recherche
            overlapping_mouvements = executer("mouvements", "select", 
                                              select_cols="Matricule",
                                              filters=[["Statut_Mouvement", "eq", "En cours"],
                                                       ["Date_Debut", "lte", str_s_end],
                                                       ["Date_Fin", "gte", str_s_start]])
            
            matricules_occupes = [row['Matricule'] for _, row in overlapping_mouvements.iterrows()] if not overlapping_mouvements.empty else []

            if matricules_occupes:
                df_disponibles = executer("stock", "select", 
                                          filters=[["Matricule", "not_in", matricules_occupes]])
            else:
                df_disponibles = executer("stock", "select")
            
            if not df_disponibles.empty:
                st.markdown(f"##### 🚗 {len(df_disponibles)} Véhicule(s) disponible(s) du `{str_s_start}` au `{str_s_end}` :")
                df_disponibles_affichage = df_disponibles[['Matricule', 'Marque', 'Modèle', 'Année']].rename(
                    columns={'Matricule': '🚘 Matricule / Plaque', 'Marque': 'Marque', 'Modèle': 'Modèle', 'Année': 'Année'}
                )
                st.dataframe(df_disponibles_affichage, use_container_width=True, hide_index=True)
            else:
                st.warning(f"❌ Désolé, aucun véhicule n\'est disponible dans la flotte BBNH du {str_s_start} au {str_s_end}.")

# --- TAB 3 : LOGISTIQUE ---
with tab_logistique:
    st.markdown("### 🔑 Box Réception Retours")
    st.markdown("#### 📝 Enregistrer un Retour de Véhicule")
    
    df_mouvements_actifs = executer("mouvements", "select", filters=[["Statut_Mouvement", "eq", "En cours"]])
    if not df_mouvements_actifs.empty:
        liste_mouvements_actifs = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouvements_actifs.iterrows()]
        
        with st.form("form_return_car"):
            mouvement_selectionne_retour = st.selectbox("Sélectionner le mouvement à clôturer :", liste_mouvements_actifs)
            
            id_mouvement_retour = int(mouvement_selectionne_retour.split(" | ")[0].replace("ID: ", "").strip())
            mouvement_info = df_mouvements_actifs[df_mouvements_actifs['ID'] == id_mouvement_retour].iloc[0]
            
            st.markdown("---<br>", unsafe_allow_html=True)
            st.markdown("##### Détails du Mouvement")
            st.write(f"**Matricule :** {mouvement_info['Matricule']}")
            st.write(f"**Client :** {mouvement_info['Client']}")
            st.write(f"**Date de début :** {mouvement_info['Date_Debut']}")
            st.write(f"**Date de fin prévue :** {mouvement_info['Date_Fin']}")
            st.write(f"**KM Départ :** {mouvement_info['KM_Debut']}")

            st.markdown("---<br>", unsafe_allow_html=True)
            st.markdown("##### Informations de Retour")
            date_retour_effective = st.date_input("Date de Retour Effective :", value=datetime.now().date())
            heure_retour_effective = st.time_input("Heure de Retour Effective :", value=datetime.now().time())
            km_retour = st.number_input("Kilométrage au Retour :", min_value=int(mouvement_info['KM_Debut']), value=int(mouvement_info['KM_Debut']))
            lieu_retour = st.text_input("Lieu de Retour :", value=mouvement_info.get('Lieu_Reception', 'Siège Monastir'))
            note_retour = st.text_area("Notes sur le Retour :")
            
            if st.form_submit_button("✅ CLÔTURER LE MOUVEMENT"):
                update_data_mouvement = {
                    "Date_Fin": date_retour_effective.strftime("%Y-%m-%d"),
                    "Heure_Fin": heure_retour_effective.strftime("%H:%M"),
                    "KM_Fin": int(km_retour),
                    "Lieu_Reception": lieu_retour,
                    "Info_Note": note_retour,
                    "Statut_Mouvement": "Terminé"
                }
                executer("mouvements", "update", data=update_data_mouvement, filters=[["ID", "eq", id_mouvement_retour]])

                # Mettre à jour le KM_Recent dans la table vidanges
                executer("vidanges", "update", 
                         data={
                             "KM_Recent": int(km_retour),
                             "Date_Mise_A_Jour": date_retour_effective.strftime("%Y-%m-%d")
                         },
                         filters=[["Matricule", "eq", mouvement_info['Matricule']]])

                st.success("Mouvement clôturé avec succès !")
                st.rerun()
    else:
        st.info("Aucun mouvement actif à clôturer.")

# --- TAB 4 : ANALYTICS ---
with tab_analytics:
    st.markdown("### 📊 Suivi des Performances")
    st.markdown("#### Statistiques Journalières")
    
    day_target = st.date_input("Sélectionner une date pour les statistiques :", datetime.now().date())
    
    df_stats = executer("mouvements", "select", filters=[["Statut_Mouvement", "eq", "Terminé"]])
    if not df_stats.empty:
        df_stats['Date_Debut'] = pd.to_datetime(df_stats['Date_Debut'])
        df_stats['Date_Fin'] = pd.to_datetime(df_stats['Date_Fin'])
        df_stats['Val_Prix'] = pd.to_numeric(df_stats['Prix'], errors='coerce').fillna(0)

        sorties = df_stats[df_stats['Date_Debut'].dt.date == day_target]
        entrees = df_stats[df_stats['Date_Fin'].dt.date == day_target]
        
        k1, k2, k3 = st.columns(3)
        with k1: st.metric("📈 DÉPARTS CONSTATÉS", f"{len(sorties)} Véhicule(s)")
        with k2: st.metric("🔑 RETOURS ENREGISTRÉS", f"{len(entrees)} Véhicule(s)")
        with k3: st.metric("💰 CA DU JOUR (DÉPARTS)", f"{sorties['Val_Prix'].sum():,.2f} DT")
            
        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("### 🛫 1. VOITURES SORTIES (DÉPARTS)")
            if not sorties.empty:
                sorties_final = sorties[['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Prix', 'KM_Debut']].rename(columns={'Matricule': '🚘 Matricule', 'Client': '👤 Client / Conducteur', 'Date_Debut': '📅 DATE SORTIE', 'Date_Fin': '📅 DATE RETOUR PRÉVUE', 'Prix': '💰 PRIX (DT)', 'KM_Debut': '🔢 KM SORTIE'})
                st.dataframe(sorties_final, use_container_width=True, hide_index=True)
            else: st.info("Aucun véhicule n\'est parti à cette date.")
        with col_droite:
            st.markdown("### 🛬 2. VOITURES RETOURNÉES (RETOURS)")
            if not entrees.empty:
                entrees['KM Roulé'] = entrees.apply(lambda r: (r['KM_Fin'] - r['KM_Debut']) if r['KM_Fin'] > r['KM_Debut'] else 0, axis=1)
                entrees['Heure_Retour_Propre'] = entrees['Heure_Fin'].apply(formater_heure_propre)
                entrees_final = entrees[['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Heure_Retour_Propre', 'Lieu_Reception', 'Prix', 'KM_Debut', 'KM_Fin', 'KM Roulé']].rename(columns={'Matricule': '🚘 Matricule', 'Client': '👤 Client / Conducteur', 'Date_Debut': '📅 DATE SORTIE', 'Date_Fin': '📅 DATE RETOUR', 'Heure_Retour_Propre': '🕒 HEURE RETOUR', 'Lieu_Reception': '📍 LIEU DE RETOUR', 'Prix': '💰 PRIX TOTAL (DT)', 'KM_Debut': '🔢 KM SORTIE', 'KM_Fin': '🔢 KM RETOUR', 'KM Roulé': '🔥 KM ROULÉ'})
                st.dataframe(entrees_final, use_container_width=True, hide_index=True)
            else: st.info("Aucun retour physique enregistré à cette date.")

# --- TAB 7 : ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Panneau de Configuration Système")
    st.warning("Attention : Ces actions sont irréversibles.")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🗑️ PURGER TOUS LES MOUVEMENTS"):
            if st.checkbox("Confirmer la purge des mouvements"):
                executer("mouvements", "delete", filters=[])
                st.success("Tous les mouvements ont été effacés.")
                st.rerun()
    with col_a2:
        if st.button("🗑️ RÉINITIALISER LA BASE CLIENTS"):
            if st.checkbox("Confirmer la purge des clients"):
                executer("clients", "delete", filters=[])
                st.success("La base clients a été réinitialisée.")
                st.rerun()
