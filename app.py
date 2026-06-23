import streamlit as st
import pandas as pd
import sqlite3
import os
import base64
from datetime import datetime, timedelta, time

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
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght=300;400;500;600;700;800&display=swap');
    
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
                    
                    p_raw = row.get('Prix', 0)
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
                SET Matricule = ?, Type_Statut = ?, Client = ?, Date_Debut = ?, Heure_Debut = ?, Date_Fin = ?, Heure_Fin = ?, Prix = ?, Caution = ?, Reste = ?, Lieu_Reception = ?, No_Vol = ?, Info_Note = ?, KM_Debut = ?
                WHERE ID = ?
            """, (mod_vehicule, mod_nature, mod_client, str_mod_d1, str_mod_t1, str_mod_d2, str_mod_t2, str(mod_prix), str(mod_caution), str(mod_reste), mod_lieu, mod_vol, mod_note, int(mod_km_deb), id_to_edit), modifier=True)
            
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
    with c_search1: search_date_debut = st.date_input("📅 Date de Sortie souhaitée :", datetime.now(), key="adv_search_start")
    with c_search2: search_date_fin = st.date_input("📅 Date de Retour prévue :", datetime.now() + timedelta(days=3), key="adv_search_end")
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
                SELECT * FROM stock WHERE [Matricule] NOT IN (
                    SELECT DISTINCT Matricule FROM mouvements 
                    WHERE Statut_Mouvement = 'En cours' AND Date_Debut <= ? AND Date_Fin >= ?
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
tab_planning, tab_contrats, tab_logistique, tab_analytics, tab_vidange, tab_crm, tab_admin = st.tabs([
    "🗓️ CORE PLANNING (365 JOURS)",
    "📄 LISTE DE CONTRAT",
    "🔑 BOX RECEPTION RETOURS",
    "📊 SUIVI DES PERFORMANCES",
    "🔧 SUIVI DES VIDANGES",
    "👥 COMPTE CONDUCTEURS (CRM)",
    "⚙️ PANNEAU DE CONFIGURATION"
])

# --- TAB 1 : PLANNING 365 JOURS ---
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
            if vehicule_recherche != "-- Toutes les voitures --" and immat != vehicule_recherche:
                continue
            modele = str(car.get('Modèle', car.get('Marque', 'Véhicule')))
            ligne = {"Flotte BBNH": f"🚘 {modele} — [{immat}]"}
            for col_j in nom_colonnes:
                ligne[col_j] = "● Disponible"
            build_matrix.append(ligne)
            
        if len(build_matrix) > 0:
            df_final_grid = pd.DataFrame(build_matrix)
            if not df_mouvs.empty and not df_final_grid.empty:
                for _, mv in df_mouvs.iterrows():
                    if pd.isna(mv.get('Matricule')) or pd.isna(mv.get('Date_Debut')) or pd.isna(mv.get('Date_Fin')):
                        continue
                    m_v = str(mv['Matricule']).strip()
                    s_v = str(mv['Type_Statut']).strip().lower()
                    client_v = str(mv['Client']).strip()
                    h_deb_label = formater_heure_propre(mv.get('Heure_Debut'))
                    h_fin_label = formater_heure_propre(mv.get('Heure_Fin'))
                    
                    try: d_debut_mv = datetime.strptime(str(mv['Date_Debut']).split(" ")[0], "%Y-%m-%d").date()
                    except: continue
                    try: d_fin_mv = datetime.strptime(str(mv['Date_Fin']).split(" ")[0], "%Y-%m-%d").date()
                    except: continue
                    
                    for idx_lg, r_lg in df_final_grid.iterrows():
                        if f"[{m_v}]" in r_lg["Flotte BBNH"]:
                            cur_date = d_debut_mv
                            while cur_date <= d_fin_mv:
                                col_cible = cur_date.strftime("%d/%m")
                                if col_cible in df_final_grid.columns:
                                    if "location" in s_v:
                                        df_final_grid.at[idx_lg, col_cible] = f"🔴 {client_v} ({h_deb_label}➔{h_fin_label})"
                                    elif "réservation" in s_v or "reservation" in s_v:
                                        df_final_grid.at[idx_lg, col_cible] = f"🟡 [RÉS] {client_v}"
                                    else:
                                        df_final_grid.at[idx_lg, col_cible] = f"🛠️ {mv['Type_Statut']}"
                                cur_date += timedelta(days=1)
            
            idx_focus = nom_colonnes.index(recherche_date.strftime("%d/%m")) if recherche_date.strftime("%d/%m") in nom_colonnes else 0
            cols_ordonnees = ["Flotte BBNH"] + nom_colonnes[idx_focus:idx_focus+15]
            st.dataframe(df_final_grid[cols_ordonnees], use_container_width=True, hide_index=True)
        else:
            st.info("Aucun véhicule ne correspond au filtre.")
    else:
        st.warning("Aucun véhicule enregistré dans le stock.")

# --- TAB 2 : LISTE DE CONTRAT ---
with tab_contrats:
    st.markdown("### 📄 Contrats Récents & Génération à la volée")
    df_contrats_db = executer("SELECT * FROM contrats")
    if not df_contrats_db.empty:
        st.dataframe(df_contrats_db, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun contrat formel enregistré dans la table courante.")

# --- TAB 3 : BOX RECEPTION RETOURS ---
with tab_logistique:
    st.markdown("### 🔑 Clôture et Retour Véhicule (Calcul KM & Restitution)")
    df_mouvs_actifs = executer("SELECT * FROM mouvements WHERE Statut_Mouvement = 'En cours'")
    
    if not df_mouvs_actifs.empty:
        liste_box = [f"ID: {r['ID']} | {r['Matricule']} — {r['Client']}" for _, r in df_mouvs_actifs.iterrows()]
        mouv_reception = st.selectbox("Sélectionner le véhicule à restituer :", liste_box)
        
        id_mouv = int(mouv_reception.split(" | ")[0].replace("ID: ", "").strip())
        row_mouv = df_mouvs_actifs[df_mouvs_actifs['ID'] == id_mouv].iloc[0]
        
        col_box1, col_box2 = st.columns(2)
        with col_box1:
            km_depart_f = st.number_input("Kilométrage de Départ (Rappel) :", value=int(row_mouv.get('KM_Debut', 0)), disabled=True)
            km_retour_f = st.number_input("Kilométrage au Retour Historique * :", min_value=km_depart_f, value=km_depart_f + 100)
        with col_box2:
            st.markdown(f"**💰 Montant Global dû :** `{row_mouv['Prix']} DT`")
            st.markdown(f"**🛡️ Caution Récupérée :** `{row_mouv['Caution']} DT`")
            st.markdown(f"**🔴 Reste à solder à l'origine :** `{row_mouv['Reste']} DT`")
            
        if st.button("🏁 CONFIRMER LE RETOUR DU VEHICULE ET ARCHIVER"):
            executer("UPDATE mouvements SET Statut_Mouvement = 'Clôturé', KM_Fin = ? WHERE ID = ?", (int(km_retour_f), id_mouv), modifier=True)
            executer("UPDATE vidanges SET KM_Recent = ?, Date_Mise_A_Jour = ? WHERE Matricule = ?", (int(km_retour_f), datetime.now().strftime("%Y-%m-%d"), str(row_mouv['Matricule']).strip()), modifier=True)
            st.success(f"Véhicule {row_mouv['Matricule']} restitué avec succès. Kilométrage mis à jour.")
            st.rerun()
    else:
        st.success("🎉 Merveilleux ! Tous les véhicules de l'agence sont actuellement disponibles au garage.")

# --- TAB 4 : SUIVI DES PERFORMANCES ---
with tab_analytics:
    st.markdown("### 📊 Statistiques & Rentabilité")
    if not df_mouvs.empty:
        c_an1, c_an2, c_an3 = st.columns(3)
        with c_an1:
            total_ca = 0
            for p in df_mouvs['Prix']:
                try: total_ca += float(str(p).replace(' ', ''))
                except: pass
            st.metric("Chiffre d'Affaires Théorique Évalué", f"{int(total_ca)} DT")
        with c_an2:
            st.metric("Nombre total de dossiers traités", len(df_mouvs))
        with c_an3:
            locs_count = len(df_mouvs[df_mouvs['Type_Statut'].str.lower() == 'location'])
            st.metric("Total Contrats Signés", locs_count)
    else:
        st.info("Aucune statistique disponible pour le moment.")

# --- TAB 5 : SUIVI DES VIDANGES ---
with tab_vidange:
    st.markdown("### 🔧 Gestion & Alerte Vidange de la Flotte")
    df_vidanges_db = executer("SELECT * FROM vidanges")
    
    if not df_vidanges_db.empty:
        for idx_v, row_v in df_vidanges_db.iterrows():
            km_der = int(row_v.get('KM_Dernier_Vidange', 0))
            km_rec = int(row_v.get('KM_Recent', 0))
            diff_km = km_rec - km_der
            reste_avant_vidange = max(0, 10000 - diff_km)
            
            c_vid1, c_vid2 = st.columns([3, 1])
            with c_vid1:
                st.markdown(f"🚗 **Véhicule :** `{row_v['Matricule']}` ({row_v['Marque']}) | Dernier vidange effectué à : `{km_der} KM` | KM Actuel calculé : `{km_rec} KM`")
                if diff_km >= 10000:
                    st.error(f"🚨 ALERTE VIDANGE DÉPASSÉE de {diff_km - 10000} KM ! Action immédiate requise.")
                else:
                    st.info(f"⏳ Reste `{reste_avant_vidange} KM` avant le prochain vidange obligatoire.")
            with c_vid2:
                nouveau_km_v = st.number_input("Nouveau KM Vidange :", min_value=0, value=km_rec, key=f"v_km_{idx_v}")
                if st.button("🔧 Valider Vidange", key=f"btn_v_{idx_v}"):
                    executer("UPDATE vidanges SET KM_Dernier_Vidange = ?, KM_Recent = ?, Date_Dernier_Vidange = ? WHERE Matricule = ?", 
                             (int(nouveau_km_v), int(nouveau_km_v), datetime.now().strftime("%Y-%m-%d"), str(row_v['Matricule'])), modifier=True)
                    st.success("Vidange enregistré !")
                    st.rerun()
            st.markdown("---")
    else:
        st.info("Aucun véhicule configuré dans le module logistique des vidanges.")

# --- TAB 6 : COMPTE CONDUCTEURS (CRM) ---
with tab_crm:
    st.markdown("### 👥 CRM & Fiches Numériques Client")
    df_clients_complets = executer("SELECT * FROM clients")
    
    if not df_clients_complets.empty:
        for _, cli in df_clients_complets.iterrows():
            with st.expander(f"👤 {str(cli['Nom']).upper()} {str(cli.get('Prénom', ''))} (CIN: {cli['CIN']})", expanded=False):
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown(f"**N° Permis :** {cli.get('N° Permis', 'N/A')}")
                    st.markdown(f"**Date Délivrance CIN :** {cli.get('Date Délivrance CIN', 'N/A')}")
                    st.markdown(f"**Date Délivrance Permis :** {cli.get('Date Délivrance Permis', 'N/A')}")
                    st.markdown(f"**Téléphone :** {cli.get('Numéro de téléphone', 'N/A')}")
                    st.markdown(f"**Remarque client :** {cli.get('Remarque', 'Aucune')}")
                with col_col_img := col_c2:
                    img_cin_data = cli.get('Image CIN', '')
                    img_per_data = cli.get('Image Permis', '')
                    
                    if img_cin_data:
                        try: st.image(base64.b64decode(img_cin_data), caption="Numérisation C.I.N", width=200)
                        except: st.caption("🖼️ Fichier CIN stocké (Format non-image ou PDF)")
                    if img_per_data:
                        try: st.image(base64.b64decode(img_per_data), caption="Numérisation Permis de Conduire", width=200)
                        except: st.caption("🖼️ Fichier Permis stocké (Format non-image ou PDF)")
    else:
        st.info("Aucun conducteur enregistré dans la base de données locale.")
        
    st.markdown("#### ➕ Ajouter un Nouveau Client manuellement")
    with st.form("form_new_manual_client"):
        n_nom = st.text_input("Nom du Client * :")
        n_prenom = st.text_input("Prénom du Client :")
        n_cin = st.text_input("Numéro CIN * :")
        n_d_cin = st.date_input("Date Délivrance CIN :", datetime.now() - timedelta(days=365))
        n_permis = st.text_input("Numéro Permis * :")
        n_d_per = st.date_input("Date Délivrance Permis :", datetime.now() - timedelta(days=365))
        n_tel = st.text_input("Numéro de téléphone :")
        
        f_cin_new = st.file_uploader("Fichier image CIN * :", type=["jpg", "png", "jpeg"])
        f_per_new = st.file_uploader("Fichier image Permis * :", type=["jpg", "png", "jpeg"])
        
        if st.form_submit_button("💾 ENREGISTRER CLIENT"):
            if n_nom and n_cin and n_permis:
                executer("""
                    INSERT OR REPLACE INTO clients ([Prénom], [Nom], [CIN], [Numéro de téléphone], [N° Permis], [Date Délivrance CIN], [Date Délivrance Permis], [Image CIN], [Image Permis])
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (n_prenom, n_nom, n_cin, n_tel, n_permis, n_d_cin.strftime("%Y-%m-%d"), n_d_per.strftime("%Y-%m-%d"), encoder_image_base64(f_cin_new), encoder_image_base64(f_per_new)), modifier=True)
                st.success("Nouveau client enregistré !")
                st.rerun()
            else:
                st.error("Veuillez remplir les champs obligatoires (*)")

# --- TAB 7 : ADMIN ---
with tab_admin:
    st.markdown("### ⚙️ Panneau de Configuration Système")
    st.warning("Attention : Ces actions sont irréversibles.")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        if st.button("🗑️ PURGER TOUS LES MOUVEMENTS"):
            executer("DELETE FROM mouvements", modifier=True)
            st.success("Tous les mouvements ont été effacés.")
            st.rerun()
    with col_a2:
        if st.button("🗑️ RÉINITIALISER LA BASE CLIENTS"):
            executer("DELETE FROM clients", modifier=True)
            st.success("La base de données clients a été intégralement vidée.")
            st.rerun()
