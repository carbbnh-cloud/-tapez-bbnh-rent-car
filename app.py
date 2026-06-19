import streamlit as st
import pandas as pd
import sqlite3
import os
import base64
from datetime import datetime, timedelta, time
# --- LOGIQUE DE LOGIN (Placer ici tout en haut de app.py) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>🔒 Accès BBNH OS</h1>", unsafe_allow_html=True)
    
    # Formulaire de login
    login = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    
    if st.button("Connexion"):
        # Vérification de vos identifiants
        if login == "carbbnh" and password == "oussamabnh":
            st.session_state.authenticated = True
            st.rerun() # Rafraîchit la page pour accéder à l'application
        else:
            st.error("Nom d'utilisateur ou mot de passe incorrect !")
            
    st.stop() # Bloque l'exécution du reste de l'application si non connecté

# --- FIN DU BLOC LOGIN ---
# Le reste de votre code (set_page_config, CSS, Tabs...) suit normalement ici.
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
    
    /* --- CORRECTION POUR LA SIDEBAR --- */
    section[data-testid="stSidebar"] {
        background-color: #07080a !important;
        border-right: 1px solid #1f242e !important;
        min-width: 450px !important;
        max-width: 450px !important;
    }

    /* --- REGLE RESPONSIVE POUR MOBILE --- */
    @media (max-width: 600px) {
        section[data-testid="stSidebar"] {
            min-width: 100% !important;
            max-width: 100% !important;
        }
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
    </style>
""", unsafe_allow_html=True)

DB_NAME = "agence_systeme_final.db"

# --- FONCTION D'ENCODAGE DES IMAGES EN TEXTE (BASE64) ---
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception as e:
        return ""

# --- CONFIGURATION ET INTEGRITE DE LA BDD ---
def preparer_base():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            [ID Client] TEXT, [Prénom] TEXT, [Nom] TEXT, [CIN] TEXT PRIMARY KEY, 
            [Date Délivrance CIN] TEXT, [Lieu & Date Naissance] TEXT, [N° Permis] TEXT, 
            [Date Délivrance Permis] TEXT, [Adresse] TEXT, [Remarque] TEXT, [Numéro de téléphone] TEXT,
            [Image CIN] TEXT DEFAULT '', [Image Permis] TEXT DEFAULT ''
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vidanges (
            [Matricule] TEXT PRIMARY KEY, [Marque] TEXT, [Date_Mise_A_Jour] TEXT,
            [Date_Dernier_Vidange] TEXT, [KM_Dernier_Vidange] INTEGER DEFAULT 0,
            [KM_Recent] INTEGER DEFAULT 0
        )
    """)
    
    cursor.execute("PRAGMA table_info(clients)")
    cols_clients = [col[1] for col in cursor.fetchall()]
    if "Image CIN" not in cols_clients:
        try: cursor.execute("ALTER TABLE clients ADD COLUMN [Image CIN] TEXT DEFAULT ''")
        except: pass
    if "Image Permis" not in cols_clients:
        try: cursor.execute("ALTER TABLE clients ADD COLUMN [Image Permis] TEXT DEFAULT ''")
        except: pass
    if "Date Délivrance CIN" not in cols_clients:
        try: cursor.execute("ALTER TABLE clients ADD COLUMN [Date Délivrance CIN] TEXT DEFAULT ''")
        except: pass
    if "Date Délivrance Permis" not in cols_clients:
        try: cursor.execute("ALTER TABLE clients ADD COLUMN [Date Délivrance Permis] TEXT DEFAULT ''")
        except: pass

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock (
            [Matricule] TEXT PRIMARY KEY, [Marque] TEXT, [Modèle] TEXT, [Année] TEXT, [Marque/Model] TEXT
        )
    """)

    cursor.execute("PRAGMA table_info(mouvements)")
    colonnes = [col[1] for col in cursor.fetchall()]
    
    if not colonnes or "ID" not in colonnes:
        cursor.execute("DROP TABLE IF EXISTS mouvements")
        cursor.execute("""
            CREATE TABLE mouvements (
                ID INTEGER PRIMARY KEY AUTOINCREMENT, Matricule TEXT, Type_Statut TEXT, 
                Date_Debut TEXT, Heure_Debut TEXT DEFAULT '00:00', Date_Fin TEXT, 
                Heure_Fin TEXT DEFAULT '00:00', Client TEXT, Prix TEXT DEFAULT '0', 
                CHEV TEXT DEFAULT '0', Statut_Mouvement TEXT DEFAULT 'En cours',
                Caution TEXT DEFAULT '0', Reste TEXT DEFAULT '0', 
                Lieu_Reception TEXT DEFAULT '', No_Vol TEXT DEFAULT '', Info_Note TEXT DEFAULT '',
                KM_Debut INTEGER DEFAULT 0, KM_Fin INTEGER DEFAULT 0
            )
        """)
    else:
        nouvelles_cols = {
            "Heure_Debut": "TEXT DEFAULT '00:00'",
            "Heure_Fin": "TEXT DEFAULT '00:00'",
            "Caution": "TEXT DEFAULT '0'",
            "Reste": "TEXT DEFAULT '0'",
            "Lieu_Reception": "TEXT DEFAULT ''",
            "No_Vol": "TEXT DEFAULT ''",
            "Info_Note": "TEXT DEFAULT ''",
            "KM_Debut": "INTEGER DEFAULT 0",
            "KM_Fin": "INTEGER DEFAULT 0"
        }
        for col_name, col_type in nouvelles_cols.items():
            if col_name not in colonnes:
                cursor.execute(f"ALTER TABLE mouvements ADD COLUMN {col_name} {col_type}")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contrats (
            [Num_Contrat] TEXT PRIMARY KEY, [Matricule] TEXT, [Client_Nom] TEXT, [CIN_Client] TEXT,
            [Date_Debut] TEXT, [Heure_Debut] TEXT, [Date_Fin] TEXT, [Heure_Fin] TEXT,
            [Tarif_Jour] TEXT, [Montant_Total] TEXT, [Statut_Contrat] TEXT
        )
    """)
    conn.commit()
    conn.close()

def executer(sql, params=(), modifier=False):
    preparer_base()
    conn = sqlite3.connect(DB_NAME)
    df = pd.DataFrame()
    reussi = True
    try:
        if modifier:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            conn.commit()
        else:
            df = pd.read_sql_query(sql, conn, params=params)
    except Exception as e:
        st.error(f"Erreur base de données : {e}")
        reussi = False
    finally:
        conn.close()
    if modifier:
        return reussi
    return df

preparer_base()

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

df_voitures = executer("SELECT * FROM stock")
df_c_list = executer("SELECT [Nom], [Prénom], [CIN] FROM clients")

liste_clients_opt = ["-- Entrée manuelle --"] + [f"{str(row['Nom']).upper()} {str(row['Prénom'])} (CIN: {row['CIN']})" for _, row in df_c_list.iterrows()] if not df_c_list.empty else ["-- Entrée manuelle --"]
liste_vehicules_opt = [f"{str(row['Matricule']).strip()}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule']) and str(row['Matricule']).strip().lower() != 'nan'] if not df_voitures.empty else []
liste_vehicules_complets_opt = [f"{str(row['Matricule']).strip()} — {str(row.get('Modèle', row.get('Marque', 'Voiture')))}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule'])] if not df_voitures.empty else []

for _, car in df_voitures.iterrows():
    mat = str(car.get('Matricule', '')).strip()
    marq = str(car.get('Marque', '')).upper()
    if mat and mat.lower() != 'nan':
        executer("INSERT OR IGNORE INTO vidanges (Matricule, Marque, Date_Mise_A_Jour, Date_Dernier_Vidange, KM_Dernier_Vidange, KM_Recent) VALUES (?, ?, ?, ?, 0, 0)", 
                 (mat, marq, datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d")), modifier=True)

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
    
    st.markdown("<br><hr>", unsafe_allow_html=True)
    with st.sidebar.expander("📥 IMPORTS EXCEL AUTOMATIQUES", expanded=False):
        f_clients = st.file_uploader("Fichier Clients (BBNH)", type=["xlsx"])
        if f_clients:
            try:
                df_cli = pd.read_excel(f_clients, sheet_name='Base de Données', skiprows=1)
                df_cli = df_cli.loc[:, ~df_cli.columns.str.contains('^Unnamed')]
                conn = sqlite3.connect(DB_NAME)
                df_cli.to_sql("clients", conn, if_exists="replace", index=False)
                conn.close()
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
                
                mapping = {}
                for col in df_mouv_raw.columns:
                    c_clean = str(col).strip().lower().replace(" ", "_").replace("é", "e").replace("è", "e")
                    if "matri" in c_clean: mapping[col] = "Matricule"
                    elif "type" in c_clean or "statut" in c_clean: mapping[col] = "Type_Statut"
                    elif "deb" in c_clean and "heur" not in c_clean: mapping[col] = "Date_Debut"
                    elif "fin" in c_clean and "heur" not in c_clean: mapping[col] = "Date_Fin"
                    elif "heur" in c_clean and "deb" in c_clean: mapping[col] = "Heure_Debut"
                    elif "heur" in c_clean and "fin" in c_clean: mapping[col] = "Heure_Fin"
                    elif "client" in c_clean or "nom" in c_clean: mapping[col] = "Client"
                    elif "prix" in c_clean or "montant" in c_clean or "total" in c_clean: mapping[col] = "Prix"
                    elif "km_deb" in c_clean or "kilometrage_deb" in c_clean or "km_depart" in c_clean: mapping[col] = "KM_Debut"
                    elif "km_fin" in c_clean or "kilometrage_ret" in c_clean or "km_retour" in c_clean: mapping[col] = "KM_Fin"
                    elif "lieu" in c_clean: mapping[col] = "Lieu_Reception"
                
                df_mouv_raw = df_mouv_raw.rename(columns=mapping)
                conn = sqlite3.connect(DB_NAME)
                df_stock.to_sql("stock", conn, if_exists="replace", index=False)
                
                cursor = conn.cursor()
                cursor.execute("DELETE FROM mouvements")
                for _, row in df_mouv_raw.iterrows():
                    h_d = formater_heure_propre(row.get('Heure_Debut'))
                    h_f = formater_heure_propre(row.get('Heure_Fin'))
                    
                    try: km_d = int(float(str(row.get('KM_Debut', 0)).strip().replace(' ', '')))
                    except: km_d = 0
                    try: km_f = int(float(str(row.get('KM_Fin', 0)).strip().replace(' ', '')))
                    except: km_f = 0
                    
                    p_raw = str(row.get('Prix', '0')).strip().replace(' ', '').replace('DT', '').replace(',','.')
                    try: p_clean = str(float(p_raw))
                    except: p_clean = "0"
                    
                    cursor.execute("""
                        INSERT INTO mouvements (Matricule, Type_Statut, Date_Debut, Heure_Debut, Date_Fin, Heure_Fin, Client, Prix, Statut_Mouvement, Caution, Reste, Lieu_Reception, KM_Debut, KM_Fin)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'En cours', '0', ?, ?, ?, ?)
                    """, (
                        str(row.get('Matricule', 'Inconnu')), str(row.get('Type_Statut', 'Location')), 
                        str(row.get('Date_Debut', '')), h_d, str(row.get('Date_Fin', '')), h_f,
                        str(row.get('Client', 'Client')), p_clean, p_clean, str(row.get('Lieu_Reception', 'Siège')), km_d, km_f
                    ))
                conn.commit()
                conn.close()
                st.success("Données intégrées avec succès !")
                st.rerun()
            except Exception as e: st.error(f"Erreur : {e}")

df_mouvs = executer("SELECT * FROM mouvements")

# --- PROCESS DES FORMULAIRES DE LA SIDEBAR ---
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
    
    f_cin = st.sidebar.file_uploader("Fichier CIN (Image/PDF) :", type=["png", "jpg", "jpeg", "pdf"])
    f_permis = st.sidebar.file_uploader("Fichier Permis (Image/PDF) :", type=["png", "jpg", "jpeg", "pdf"])
    
    # --- BLOC DATES & CALCULS AUTOMATIQUES ---
    st.sidebar.markdown("---")
    d1 = st.sidebar.date_input("Date Réception / Début :", datetime.now())
    t1 = st.sidebar.time_input("Heure Réception :", time(9, 0))
    d2 = st.sidebar.date_input("Date Fin / Retour :", datetime.now() + timedelta(days=2))
    t2 = st.sidebar.time_input("Heure Fin :", time(12, 0))
    
    nbr_jours = (d2 - d1).days
    if nbr_jours <= 0:
        nbr_jours = 1
        
    st.sidebar.markdown(f"**🔢 Durée estimée :** `{nbr_jours} jour(s)`")
    
    prix_unitaire = st.sidebar.number_input("💰 Prix Unitaire / Jour (DT) :", min_value=0, value=100, step=5)
    
    total_auto = nbr_jours * prix_unitaire
    montant_total = st.sidebar.number_input("💵 Montant Total Calculé (DT) :", min_value=0, value=int(total_auto))
    
    caution = st.sidebar.number_input("🛡️ Caution Déposée (DT) :", value=0)
    reste = montant_total - caution
    st.sidebar.markdown(f"**🔴 Reste à payer :** `{reste} DT`")
    st.sidebar.markdown("---")
    
    km_debut = st.sidebar.number_input("Kilométrage au Départ :", min_value=0, value=0, step=1)
    l_reception = st.sidebar.text_input("Lieu de réception :", value="Siège Monastir")
    no_vol = st.sidebar.text_input("N° de vol :", value="")
    info_note = st.sidebar.text_area("Note complémentaire :")
    ref = st.sidebar.text_input("Code Contrat unique :", f"BBNH-{datetime.now().strftime('%d%H%S')}")
    
    if st.sidebar.button("⚡ ENREGISTRER ON THE PLANNING"):
        nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN:")[0]
        cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "")
        str_d1, str_d2 = d1.strftime("%Y-%m-%d"), d2.strftime("%Y-%m-%d")
        str_t1, str_t2 = t1.strftime("%H:%M"), t2.strftime("%H:%M")
        text_type = "Location" if "Contrat" in nature else nature
        
        img_cin_b64 = encoder_image_base64(f_cin)
        img_permis_b64 = encoder_image_base64(f_permis)
        
        if client_b == "-- Entrée manuelle --":
            executer("""
                INSERT OR REPLACE INTO clients ([Nom], [CIN], [Date Délivrance CIN], [N° Permis], [Date Délivrance Permis], [Image CIN], [Image Permis])
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nom_f, cin_f, dc_m.strftime("%Y-%m-%d"), permis_m, dp_m.strftime("%Y-%m-%d"), img_cin_b64, img_permis_b64), modifier=True)
        
        if "Contrat" in nature:
            executer("INSERT INTO contrats VALUES (?,?,?,?,?, ?, ?, ?, ?,?, 'Actif')", (ref, vehicule, nom_f, cin_f, str_d1, str_t1, str_d2, str_t2, str(prix_unitaire), str(montant_total)), modifier=True)
        
        executer("""
            INSERT INTO mouvements (Matricule, Type_Statut, Date_Debut, Heure_Debut, Date_Fin, Heure_Fin, Client, Prix, Statut_Mouvement, Caution, Reste, Lieu_Reception, No_Vol, Info_Note, KM_Debut, KM_Fin) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'En cours', ?, ?, ?, ?, ?, ?, 0)
        """, (vehicule, text_type, str_d1, str_t1, str_d2, str_t2, nom_f, str(montant_total), str(caution), str(reste), l_reception, no_vol, info_note, int(km_debut)), modifier=True)
        
        executer("UPDATE vidanges SET KM_Recent = ?, Date_Mise_A_Jour = ? WHERE Matricule = ?", (int(km_debut), str_d1, vehicule), modifier=True)
        st.success("Fiche créée avec succès !")
        st.rerun()

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
                executer("INSERT OR REPLACE INTO stock ([Matricule], [Marque], [Modèle], [Année], [Marque/Model]) VALUES (?, ?, ?, ?, ?)", (nouveau_matricule, nouvelle_marque, nouveau_modele, nouvelle_annee, combinaison_modele), modifier=True)
                executer("INSERT OR IGNORE INTO vidanges (Matricule, Marque, Date_Mise_A_Jour, Date_Dernier_Vidange) VALUES (?, ?, ?, ?)", (nouveau_matricule, nouvelle_marque.upper(), datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d")), modifier=True)
                st.success("Véhicule enregistré !")
                st.rerun()

elif menu_action == "🗑️ Supprimer un Véhicule de la Flotte":
    if liste_vehicules_complets_opt:
        with st.sidebar.form("form_bbnh_delete_car"):
            vehicule_a_retirer = st.selectbox("Choisir le véhicule à supprimer :", liste_vehicules_complets_opt)
            confirmer_suppression = st.checkbox("Confirmer la suppression définitive")
            if st.form_submit_button("💥 SUPPRIMER LE VÉHICULE"):
                if confirmer_suppression:
                    matricule_pure = str(vehicule_a_retirer).split(" — ")[0].strip()
                    executer("DELETE FROM stock WHERE [Matricule] = ?", (matricule_pure,), modifier=True)
                    executer("DELETE FROM vidanges WHERE [Matricule] = ?", (matricule_pure,), modifier=True)
                    st.success("Véhicule retiré.")
                    st.rerun()

elif menu_action == "⚙️ Modifier un Dossier (Contrat/Réservation)":
    df_mouv_actifs = executer("SELECT * FROM mouvements WHERE Statut_Mouvement = 'En cours'")
    if not df_mouv_actifs.empty:
        liste_mouv_mod = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouv_actifs.iterrows()]
        mouv_selectionne = st.sidebar.selectbox("Sélectionner le dossier à éditer :", liste_mouv_mod)
        id_to_edit = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
        row_init = df_mouv_actifs[df_mouv_actifs['ID'] == id_to_edit].iloc[0]
        
        df_cli_spec = executer("SELECT * FROM clients WHERE [Nom] = ?", (str(row_init['Client']),))
        row_cli_init = df_cli_spec.iloc[0] if not df_cli_spec.empty else {}
        
        try: init_date_deb = datetime.strptime(str(row_init['Date_Debut']), "%Y-%m-%d").date()
        except: init_date_deb = datetime.now().date()
        try: init_date_fin = datetime.strptime(str(row_init['Date_Fin']), "%Y-%m-%d").date()
        except: init_date_fin = datetime.now().date()
        try: init_time_deb = datetime.strptime(formater_heure_propre(row_init['Heure_Debut']), "%H:%M").time()
        except: init_time_deb = time(9, 0)
        try: init_time_fin = datetime.strptime(formater_heure_propre(row_init['Heure_Fin']), "%H:%M").time()
        except: init_time_fin = time(12, 0)
        
        try: init_date_cin = datetime.strptime(str(row_cli_init.get('Date Délivrance CIN')), "%Y-%m-%d").date()
        except: init_date_cin = datetime.now().date()
        try: init_date_permis = datetime.strptime(str(row_cli_init.get('Date Délivrance Permis')), "%Y-%m-%d").date()
        except: init_date_permis = datetime.now().date()
        
        st.sidebar.markdown(f"### ⚙️ Édition Totale du Dossier #{id_to_edit}")
        mod_nature = st.sidebar.selectbox("Changer de Nature :", ["Location", "Réservation", "Maintenance / Garage"], index=["location", "réservation", "maintenance / garage"].index(str(row_init['Type_Statut']).lower()) if str(row_init['Type_Statut']).lower() in ["location", "réservation", "maintenance / garage"] else 0)
        idx_v_init = liste_vehicules_opt.index(str(row_init['Matricule']).strip()) if str(row_init['Matricule']).strip() in liste_vehicules_opt else 0
        mod_vehicule = st.sidebar.selectbox("Changer de véhicule :", liste_vehicules_opt, index=idx_v_init)
        
        st.sidebar.markdown("---")
        st.sidebar.markdown("👤 **Informations Conducteur**")
        mod_client = st.sidebar.text_input("Nom & Prénom du Conducteur :", value=str(row_init['Client']))
        mod_cin = st.sidebar.text_input("N° CIN :", value=str(row_cli_init.get('CIN', '')))
        mod_date_cin = st.sidebar.date_input("Date de Délivrance CIN :", init_date_cin)
        mod_permis = st.sidebar.text_input("N° Permis de Conduire :", value=str(row_cli_init.get('N° Permis', '')))
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
        
        df_contrat_spec = executer("SELECT [Tarif_Jour] FROM contrats WHERE [Num_Contrat] = ?", (str(id_to_edit),))
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
                executer("UPDATE clients SET [Image CIN] = ? WHERE [CIN] = ?", (encoder_image_base64(mod_f_cin), mod_cin), modifier=True)
            if mod_f_permis:
                executer("UPDATE clients SET [Image Permis] = ? WHERE [CIN] = ?", (encoder_image_base64(mod_f_permis), mod_cin), modifier=True)
            
            executer("""
                UPDATE clients 
                SET [Nom] = ?, [Date Délivrance CIN] = ?, [N° Permis] = ?, [Date Délivrance Permis] = ?
                WHERE [CIN] = ?
            """, (mod_client, mod_date_cin.strftime("%Y-%m-%d"), mod_permis, mod_date_permis.strftime("%Y-%m-%d"), mod_cin), modifier=True)
            
            executer("""
                UPDATE mouvements 
                SET Matricule = ?, Type_Statut = ?, Client = ?, Date_Debut = ?, Heure_Debut = ?, Date_Fin = ?, Heure_Fin = ?, 
                    Prix = ?, Caution = ?, Reste = ?, Lieu_Reception = ?, No_Vol = ?, Info_Note = ?, KM_Debut = ?
                WHERE ID = ?
            """, (
                mod_vehicule, mod_nature, mod_client, str_mod_d1, str_mod_t1, str_mod_d2, str_mod_t2,
                str(mod_prix), str(mod_caution), str(mod_reste), mod_lieu, mod_vol, mod_note, int(mod_km_deb), id_to_edit
            ), modifier=True)
            
            executer("UPDATE vidanges SET KM_Recent = ?, Date_Mise_A_Jour = ? WHERE Matricule = ?", (int(mod_km_deb), str_mod_d1, mod_vehicule), modifier=True)
            st.success("Toutes les données ont été mises à jour avec succès !")
            st.rerun()

elif menu_action == "❌ Supprimer une opération":
    df_mouv_actifs = executer("SELECT * FROM mouvements WHERE Statut_Mouvement = 'En cours'")
    if not df_mouv_actifs.empty:
        liste_mouv_del = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouv_actifs.iterrows()]
        with st.sidebar.form("form_bbnh_delete_mouv"):
            mouv_selectionne = st.selectbox("Choisir l'opération à détruire :", liste_mouv_del)
            confirmer_action = st.checkbox("Confirmer la suppression")
            if st.form_submit_button("💥 RETIRER DU PLANNING"):
                if confirmer_action:
                    id_to_delete = int(mouv_selectionne.split(" | ")[0].replace("ID: ", "").strip())
                    executer("DELETE FROM mouvements WHERE ID = ?", (id_to_delete,), modifier=True)
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
        st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
        btn_recherche_dispo = st.button("🔍 Vérifier les Disponibilités", use_container_width=True)

    if btn_recherche_dispo:
        str_s_start = search_date_debut.strftime("%Y-%m-%d")
        str_s_end = search_date_fin.strftime("%Y-%m-%d")
        
        if search_date_debut > search_date_fin:
            st.error("⚠️ La date de sortie ne peut pas être supérieure à la date de retour.")
        else:
            query_dispo = """
                SELECT * FROM stock 
                WHERE [Matricule] NOT IN (
                    SELECT DISTINCT Matricule FROM mouvements 
                    WHERE Statut_Mouvement = 'En cours'
                    AND Date_Debut <= ? 
                    AND Date_Fin >= ?
                )
            """
            df_disponibles = executer(query_dispo, (str_s_end, str_s_start))
            
            if not df_disponibles.empty:
                st.markdown(f"##### 🚗 {len(df_disponibles)} Véhicule(s) disponible(s) du `{str_s_start}` au `{str_s_end}` :")
                df_disponibles_affichage = df_disponibles[['Matricule', 'Marque', 'Modèle', 'Année']].rename(
                    columns={'Matricule': '🚘 Matricule / Plaque', 'Marque': 'Marque', 'Modèle': 'Modèle', 'Année': 'Année'}
                )
                st.dataframe(df_disponibles_affichage, use_container_width=True, hide_index=True)
            else:
                st.warning(f"❌ Désolé, aucun véhicule n'est disponible dans la flotte BBNH du {str_s_start} au {str_s_end}.")

st.markdown("<br>", unsafe_allow_html=True)

# --- NAVIGATION DES ONGLETS DE L'INTERFACE APPLICATION ---
tab_planning, tab_logistique, tab_analytics, tab_vidange, tab_crm, tab_admin = st.tabs([
    "🗓️ CORE PLANNING (365 JOURS)",
    "🔑 BOX RECEPTION RETOURS",
    "📊 SUIVI DES PERFORMANCES",
    "🔧 SUIVI DES VIDANGES",
    "👥 COMPTE CONDUCTEURS (CRM)",
    "⚙️ PANNEAU DE CONFIGURATION"
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
        recherche_date = st.date_input("📅 Aller à la date spécifique (Focus) :", datetime(2026, 6, 12))

    array_jours = [date_base + timedelta(days=i) for i in range(365)]
    nom_colonnes = [j.strftime("%d/%m") for j in array_jours]
    df_voitures_valides = df_voitures[df_voitures['Matricule'].notna() & (df_voitures['Matricule'].str.strip().str.lower() != 'nan')] if not df_voitures.empty else pd.DataFrame()

    if not df_voitures_valides.empty:
        build_matrix = []
        for _, car in df_voitures_valides.iterrows():
            immat = str(car.get('Matricule', '')).strip()
            if vehicule_recherche != "-- Toutes les voitures --" and immat != vehicule_recherche: continue
            modele = str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            ligne = {"Flotte BBNH": f"🚘 {modele} — [{immat}]"}
            for col_j in nom_colonnes: ligne[col_j] = "● Disponible"
            build_matrix.append(ligne)

        if len(build_matrix) > 0:
            df_final_grid = pd.DataFrame(build_matrix)
            if not df_mouvs.empty and not df_final_grid.empty:
                suivi_jours = {}
                for _, mv in df_mouvs.iterrows():
                    if pd.isna(mv.get('Matricule')) or pd.isna(mv.get('Date_Debut')) or pd.isna(mv.get('Date_Fin')): continue
                    m_v = str(mv['Matricule']).strip()
                    s_v = str(mv['Type_Statut']).strip().lower()
                    client_v = str(mv['Client']).strip()
                    h_deb_label = formater_heure_propre(mv.get('Heure_Debut'))
                    h_fin_label = formater_heure_propre(mv.get('Heure_Fin'))

                    try:
                        d_debut_mv = pd.to_datetime(mv['Date_Debut'], errors='coerce', format='mixed').date()
                        d_fin_mv = pd.to_datetime(mv['Date_Fin'], errors='coerce', format='mixed').date()
                        if m_v not in suivi_jours: suivi_jours[m_v] = {}
                            
                        for j in array_jours:
                            if d_debut_mv <= j <= d_fin_mv:
                                key_day = j.strftime("%d/%m")
                                if key_day not in suivi_jours[m_v]:
                                    suivi_jours[m_v][key_day] = {
                                        "depart": False, "fin": False, 
                                        "client_sortant": "", "client_entrant": "",
                                        "heure_sortie": "00:00", "heure_retour": "00:00", 
                                        "desc": "", "type": s_v
                                    }
                                if j == d_debut_mv: 
                                    suivi_jours[m_v][key_day]["depart"] = True
                                    suivi_jours[m_v][key_day]["client_sortant"] = client_v
                                    suivi_jours[m_v][key_day]["heure_sortie"] = h_deb_label
                                if j == d_fin_mv: 
                                    suivi_jours[m_v][key_day]["fin"] = True
                                    suivi_jours[m_v][key_day]["client_entrant"] = client_v
                                    suivi_jours[m_v][key_day]["heure_retour"] = h_fin_label
                                
                                if not (suivi_jours[m_v][key_day]["depart"] and suivi_jours[m_v][key_day]["fin"]):
                                    if "garage" in s_v or "maintenance" in s_v: 
                                        suivi_jours[m_v][key_day]["desc"] = f"🛠️ GARAGE : {client_v}"
                                    elif "réservation" in s_v: 
                                        suivi_jours[m_v][key_day]["desc"] = f"🔴 [{h_deb_label}➔{h_fin_label}] {client_v}"
                                    else: 
                                        suivi_jours[m_v][key_day]["desc"] = f"🟢 [{h_deb_label}➔{h_fin_label}] {client_v}"
                    except: pass

                for idx, row in df_final_grid.iterrows():
                    mat_extracted = row["Flotte BBNH"].split("[")[-1].replace("]", "").strip()
                    if mat_extracted in suivi_jours:
                        for key_day, data in suivi_jours[mat_extracted].items():
                            if key_day in df_final_grid.columns:
                                if data["depart"] and data["fin"]:
                                    df_final_grid.at[idx, key_day] = f"🔵 🛬{data['heure_retour']} {data['client_entrant']} / 🛫{data['heure_sortie']} {data['client_sortant']}"
                                elif data["desc"] != "": 
                                    df_final_grid.at[idx, key_day] = data["desc"]

            def style_bbnh_theme(val):
                val_str = str(val)
                if "● Disponible" in val_str: return "background-color: #ffffff; color: #111827; font-size: 11px; font-weight: 600; text-align: center; border: 1px solid #e5e7eb;"
                elif "🔵" in val_str: return "background-color: #1d4ed8; color: #ffffff; font-weight: 700; font-size: 10px; border: 2px solid #60a5fa;"
                elif "🛠️" in val_str: return "background-color: #eab308; color: #1e1b4b; font-weight: 700; font-size: 11px;"
                elif "🔴" in val_str: return "background-color: #dc2626; color: #ffffff; font-weight: 600; font-size: 11px;"
                elif "🟢" in val_str: return "background-color: #16a34a; color: #ffffff; font-weight: 600; font-size: 11px;"
                return "background-color: #090b0e; color: #ffffff; font-weight: 700; font-size: 12px; border-right: 3px solid #e60000;"

            target_col_str = recherche_date.strftime("%d/%m")
            cols_ordonnees = ['Flotte BBNH']
            if target_col_str in nom_colonnes:
                idx_target = nom_colonnes.index(target_col_str)
                cols_ordonnees += nom_colonnes[max(0, idx_target - 2):min(365, idx_target + 21)]
            else: cols_ordonnees += nom_colonnes[:20]

            st.dataframe(df_final_grid[cols_ordonnees].style.map(style_bbnh_theme, subset=[c for c in cols_ordonnees if c != 'Flotte BBNH']), use_container_width=True, height=800)

# --- TAB 2 : RECEPTION LOGISTIQUE ---
with tab_logistique:
    st.markdown("### 🔑 Terminal de Restitution et Clôture")
    df_actifs = executer("SELECT * FROM mouvements WHERE Statut_Mouvement = 'En cours'")
    if not df_actifs.empty:
        choix_actifs = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_actifs.iterrows()]
        col_list, col_details = st.columns([1, 1])
        with col_list:
            target_v = st.selectbox("Sélectionner le véhicule rentrant :", choix_actifs)
            d_reel = st.date_input("Date de retour physique effective :", datetime.now())
            t_reel = st.time_input("Heure de retour effective :", datetime.now().time())
            l_retour = st.text_input("Lieu de retour effectif :", value="Siège Monastir")
            id_mouv_temp = int(target_v.split(" | ")[0].replace("ID: ", "").strip()) if target_v else 0
            km_dep_de_base = 0
            if id_mouv_temp > 0:
                res_dep = df_actifs[df_actifs['ID'] == id_mouv_temp]
                if not res_dep.empty:
                    try: km_dep_de_base = int(float(str(res_dep.iloc[0].get('KM_Debut', 0)).replace(' ', '')))
                    except: km_dep_de_base = 0
            km_fin = st.number_input("Kilométrage au Retour :", min_value=km_dep_de_base, value=km_dep_de_base, step=1)
            if st.button("✅ VALIDATION DU RETOUR", use_container_width=True):
                id_mouv = target_v.split(" | ")[0].replace("ID: ", "").strip()
                str_t_reel = t_reel.strftime("%H:%M")
                vehicule_rentre = str(res_dep.iloc[0].get('Matricule'))
                
                executer("UPDATE mouvements SET Statut_Mouvement = 'Retourné', Date_Fin = ?, Heure_Fin = ?, Lieu_Reception = ?, KM_Fin = ? WHERE ID = ?", 
                         (d_reel.strftime("%Y-%m-%d"), str_t_reel, l_retour, int(km_fin), id_mouv), modifier=True)
                executer("UPDATE vidanges SET KM_Recent = ?, Date_Mise_A_Jour = ? WHERE Matricule = ?", (int(km_fin), d_reel.strftime("%Y-%m-%d"), vehicule_rentre), modifier=True)
                st.success("Le retour a été validé et mis à jour pour le suivi des vidanges !")
                st.rerun()
        with col_details:
            id_sel = int(target_v.split(" | ")[0].replace("ID: ", "").strip()) if target_v else None
            if id_sel:
                row_sel = df_actifs[df_actifs['ID'] == id_sel].iloc[0]
                diff_km = int(km_fin) - int(km_dep_de_base)
                st.markdown(f"**📊 Distance Parcourue :** <span style='color:#4ade80; font-weight:bold; font-size:22px;'>{diff_km} KM</span>", unsafe_allow_html=True)
                st.write(f"**Reste dû :** {row_sel.get('Reste', '0')} DT")
    else: st.info("Aucun déplacement en cours.")

# --- TAB 3 : PERFORMANCE ---
with tab_analytics:
    st.markdown("### 📊 Chiffre d'Affaires & Synthèse Logistique du Jour")
    day_target = st.date_input("Sélectionner la journée d'analyse :", datetime.now())
    if not df_mouvs.empty:
        df_stats = df_mouvs.copy()
        df_stats['Clean_D'] = pd.to_datetime(df_stats['Date_Debut'], errors='coerce', format='mixed').dt.date
        df_stats['Clean_F'] = pd.to_datetime(df_stats['Date_Fin'], errors='coerce', format='mixed').dt.date
        df_stats['KM_Debut'] = pd.to_numeric(df_stats['KM_Debut'], errors='coerce').fillna(0).astype(int)
        df_stats['KM_Fin'] = pd.to_numeric(df_stats['KM_Fin'], errors='coerce').fillna(0).astype(int)
        df_stats['Val_Prix'] = df_stats['Prix'].astype(str).str.replace(' ', '').str.replace('DT', '').str.replace(',','.')
        df_stats['Val_Prix'] = pd.to_numeric(df_stats['Val_Prix'], errors='coerce').fillna(0.0)
        
        sorties = df_stats[df_stats['Clean_D'] == day_target]
        entrees = df_stats[df_stats['Clean_F'] == day_target]
        
        k1, k2, k3 = st.columns(3)
        with k1: st.metric("📈 DÉPARTS CONSTATÉS", f"{len(sorties)} Véhicule(s)")
        with k2: st.metric("🔑 RETOURS ENREGISTRÉS", f"{len(entrees)} Véhicule(s)")
        with k3: st.metric("💰 CA DU JOUR (DÉPARTS)", f"{sorties['Val_Prix'].sum():,.2f} DT")
            
        st.markdown("<br><hr>", unsafe_allow_html=True)
        col_gauche, col_droite = st.columns(2)
        with col_gauche:
            st.markdown("### 🛫 1. VOITURES SORTIES (DÉPARTS)")
            # --- LE CORRECTIF EST ICI ---
            if not sorties.empty:
                sorties_final = sorties[['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Prix', 'KM_Debut']].rename(columns={'Matricule': '🚘 Matricule', 'Client': '👤 Client / Conducteur', 'Date_Debut': '📅 DATE SORTIE', 'Date_Fin': '📅 DATE RETOUR PRÉVUE', 'Prix': '💰 PRIX (DT)', 'KM_Debut': '🔢 KM SORTIE'})
                st.dataframe(sorties_final, use_container_width=True, hide_index=True)
            else: st.info("Aucun véhicule n'est parti à cette date.")
        with col_droite:
            st.markdown("### 🛬 2. VOITURES RETOURNÉES (RETOURS)")
            if not entrees.empty:
                entrees['KM Roulé'] = entrees.apply(lambda r: (r['KM_Fin'] - r['KM_Debut']) if r['KM_Fin'] > r['KM_Debut'] else 0, axis=1)
                entrees['Heure_Retour_Propre'] = entrees['Heure_Fin'].apply(formater_heure_propre)
                entrees_final = entrees[['Matricule', 'Client', 'Date_Debut', 'Date_Fin', 'Heure_Retour_Propre', 'Lieu_Reception', 'Prix', 'KM_Debut', 'KM_Fin', 'KM Roulé']].rename(columns={'Matricule': '🚘 Matricule', 'Client': '👤 Client / Conducteur', 'Date_Debut': '📅 DATE SORTIE', 'Date_Fin': '📅 DATE RETOUR', 'Heure_Retour_Propre': '🕒 HEURE RETOUR', 'Lieu_Reception': '📍 LIEU DE RETOUR', 'Prix': '💰 PRIX TOTAL (DT)', 'KM_Debut': '🔢 KM SORTIE', 'KM_Fin': '🔢 KM RETOUR', 'KM Roulé': '🔥 KM ROULÉ'})
                st.dataframe(entrees_final, use_container_width=True, hide_index=True)
            else: st.info("Aucun retour physique enregistré à cette date.")

# --- TAB 4 : VIDANGES ---
with tab_vidange:
    st.markdown("### 🔧 Tableau de bord de Maintenance & Vidanges Automatisé")
    df_v_base = executer("SELECT * FROM vidanges")
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
                date_effective = st.date_input("Date effective de l'opération :", datetime.now())
                action_sync = st.checkbox("Vidange effectuée aujourd'hui (Synchronise le dernier KM et remet à zéro)", value=False)
            
            if st.button("💾 ENREGISTRER ET RECALCULER DIRECTEMENT", use_container_width=True):
                date_operation_str = date_effective.strftime("%Y-%m-%d")
                date_historique_str = date_dernier_manuel.strftime("%Y-%m-%d")
                if action_sync:
                    executer("UPDATE vidanges SET KM_Recent = ?, KM_Dernier_Vidange = ?, Date_Dernier_Vidange = ?, Date_Mise_A_Jour = ? WHERE Matricule = ?", (int(nouveau_km_actuel), int(nouveau_km_actuel), date_operation_str, date_operation_str, v_select), modifier=True)
                else:
                    executer("UPDATE vidanges SET KM_Recent = ?, KM_Dernier_Vidange = ?, Date_Dernier_Vidange = ?, Date_Mise_A_Jour = ? WHERE Matricule = ?", (int(nouveau_km_actuel), int(dernier_km_vidange_input), date_historique_str, date_operation_str, v_select), modifier=True)
                st.success("Calculs mis à jour instantanément !")
                st.rerun()

# --- TAB 5 : COMPTE CONDUCTEURS / CRM ---
with tab_crm:
    st.markdown("### 👥 Banque d'Information des Conducteurs & Profils Clients")
    c1, c2 = st.columns([5, 4])
    
    with c1:
        st.markdown("#### 🔍 Consultation & Actions")
        search_query = st.text_input("Rechercher un profil (Nom, Prénom, CIN) :", key="crm_search_field")
        
        if search_query:
            clients_trouves = executer("SELECT * FROM clients WHERE [Nom] LIKE ? OR [Prénom] LIKE ? OR [CIN] LIKE ?", (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"))
            
            if not clients_trouves.empty:
                for idx, cli in clients_trouves.iterrows():
                    cin_client_actuel = str(cli['CIN']).strip()
                    unique_suffix = f"{idx}_{cin_client_actuel}"
                    
                    with st.expander(f"👤 {str(cli['Nom']).upper()} {cli['Prénom']} (CIN: {cin_client_actuel})", expanded=True):
                        st.write(f"**📞 Téléphone :** `{cli.get('Numéro de téléphone', 'N/A')}` | **🚗 N° Permis :** `{cli.get('N° Permis', 'N/A')}`")
                        st.write(f"📅 **Délivrance CIN :** `{cli.get('Date Délivrance CIN', 'N/A')}` | 📅 **Délivrance Permis :** `{cli.get('Date Délivrance Permis', 'N/A')}`")
                        
                        col_img1, col_img2 = st.columns(2)
                        with col_img1:
                            if cli.get('Image CIN'):
                                try: st.image(base64.b64decode(cli['Image CIN']), caption="Pièce d'identité (CIN)", use_container_width=True)
                                except: pass
                        with col_img2:
                            if cli.get('Image Permis'):
                                try: st.image(base64.b64decode(cli['Image Permis']), caption="Permis de conduire", use_container_width=True)
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
                                    executer("DELETE FROM clients WHERE [CIN] = ?", (cin_client_actuel,), modifier=True)
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
                                e_tel = st.text_input("Téléphone", value=str(cli.get('Numéro de téléphone', '')))
                                e_permis = st.text_input("N° Permis", value=str(cli.get('N° Permis', '')))
                                
                                try: e_init_d_cin = datetime.strptime(str(cli.get('Date Délivrance CIN')), "%Y-%m-%d").date()
                                except: e_init_d_cin = datetime.now().date()
                                try: e_init_d_per = datetime.strptime(str(cli.get('Date Délivrance Permis')), "%Y-%m-%d").date()
                                except: e_init_d_per = datetime.now().date()
                                    
                                e_d_cin = st.date_input("Date Délivrance CIN", value=e_init_d_cin)
                                e_d_per = st.date_input("Date Délivrance Permis", value=e_init_d_per)
                                
                                f_cin_remplace = st.file_uploader("Remplacer l'image CIN (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_cin_{unique_suffix}")
                                f_per_remplace = st.file_uploader("Remplacer l'image Permis (Optionnel)", type=["png", "jpg", "jpeg"], key=f"file_per_{unique_suffix}")
                                
                                c_form_b1, c_form_b2 = st.columns(2)
                                with c_form_b1:
                                    if st.form_submit_button("💾 SAUVEGARDER LES MODIFICATIONS"):
                                        executer("""
                                            UPDATE clients 
                                            SET [Prénom] = ?, [Nom] = ?, [Numéro de téléphone] = ?, [N° Permis] = ?, 
                                                [Date Délivrance CIN] = ?, [Date Délivrance Permis] = ?
                                            WHERE [CIN] = ?
                                        """, (e_prenom, e_nom, e_tel, e_permis, e_d_cin.strftime("%Y-%m-%d"), e_d_per.strftime("%Y-%m-%d"), cin_client_actuel), modifier=True)
                                        
                                        if f_cin_remplace:
                                            executer("UPDATE clients SET [Image CIN] = ? WHERE [CIN] = ?", (encoder_image_base64(f_cin_remplace), cin_client_actuel), modifier=True)
                                        if f_per_remplace:
                                            executer("UPDATE clients SET [Image Permis] = ? WHERE [CIN] = ?", (encoder_image_base64(f_per_remplace), cin_client_actuel), modifier=True)
                                            
                                        st.success("Données du client mises à jour !")
                                        st.session_state[f"mode_edition_{unique_suffix}"] = False
                                        st.rerun()
                                with c_form_b2:
                                    if st.form_submit_button("❌ ANNULER"):
                                        st.session_state[f"mode_edition_{unique_suffix}"] = False
                                        st.rerun()
            else:
                st.info("Aucun client trouvé avec ces critères de recherche.")
                
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(executer("SELECT [Nom], [Prénom], [CIN], [N° Permis], [Date Délivrance CIN], [Date Délivrance Permis], [Numéro de téléphone] FROM clients ORDER BY [Nom] ASC"), use_container_width=True)

    with c2:
        with st.form("form_crm_bbnh_new", clear_on_submit=True):
            st.markdown("### ➕ Créer un nouveau profil Client")
            p_add, n_add, c_add = st.text_input("Prénom *"), st.text_input("Nom *"), st.text_input("N° CIN *")
            dc_add = st.date_input("Date de Délivrance CIN")
            t_add, pm_add = st.text_input("Téléphone"), st.text_input("N° Permis")
            dp_add = st.date_input("Date de Délivrance Permis")
            
            f_cin_crm = st.file_uploader("Fichier CIN :", type=["png", "jpg", "jpeg", "pdf"], key="f_cin_crm")
            f_per_crm = st.file_uploader("Fichier Permis :", type=["png", "jpg", "jpeg", "pdf"], key="f_per_crm")
            
            if st.form_submit_button("💾 SAUVEGARDER DIRECTEMENT"):
                if p_add and n_add and c_add:
                    img_c = encoder_image_base64(f_cin_crm)
                    img_p = encoder_image_base64(f_per_crm)
                    executer("""
                        INSERT OR REPLACE INTO clients ([Prénom], [Nom], [CIN], [Date Délivrance CIN], [Numéro de téléphone], [N° Permis], [Date Délivrance Permis], [Image CIN], [Image Permis]) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (p_add, n_add, c_add, dc_add.strftime("%Y-%m-%d"), t_add, pm_add, dp_add.strftime("%Y-%m-%d"), img_c, img_p), modifier=True)
                    st.success("Dossier sauvegardé !")
                    st.rerun()

# --- TAB 6 : ADMINISTRATION INTERNE ---
with tab_admin:
    st.markdown("### ⚙️ Console Administrative de Purge")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("🗑️ PURGER TOUS LES MOUVEMENTS", use_container_width=True): executer("DELETE FROM mouvements", modifier=True); st.rerun()
    with col_b2:
        if st.button("💥 HARD RESET COMPLET", use_container_width=True):
            for t in ["mouvements", "contrats", "clients", "stock", "vidanges"]: executer(f"DELETE FROM {t}", modifier=True)
            st.rerun()
