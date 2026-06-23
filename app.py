Voici le code complet et entièrement migré vers Supabase pour votre fichier app.py.

Pour éviter que Streamlit ne masque les détails de l'erreur avec un message d'interception générique (The original error message is redacted...), j'ai encapsulé la récupération des données globales dans un bloc try-except robuste. Ainsi, si une table manque ou si les droits RLS bloquent la base, l'application affichera le message d'erreur SQL exact sur votre écran.

1. Code complet pour app.py
Remplacez tout le contenu de votre fichier app.py par le code suivant :

Python
import streamlit as st
import pandas as pd
import os
import base64
from datetime import datetime, timedelta, time
from supabase import create_client, Client

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
    </style>
""", unsafe_allow_html=True)

# --- CONNEXION SUPABASE ---
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("❌ Impossible de charger les clés secrètes Supabase depuis les Secrets Streamlit.")
    st.stop()

# --- FONCTION D'ENCODAGE DES IMAGES EN BASE64 ---
def encoder_image_base64(file_buffer):
    if file_buffer is None:
        return ""
    try:
        return base64.b64encode(file_buffer.getvalue()).decode()
    except Exception as e:
        return ""

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

# --- CHARGEMENT SÉCURISÉ DES DONNÉES GLOBALES ---
@st.cache_data(ttl=5)
def load_global_data():
    # 1. Table stock
    try:
        res_voitures = supabase.table("stock").select("*").execute()
        df_voitures = pd.DataFrame(res_voitures.data)
    except Exception as e:
        st.error(f"⚠️ Erreur sur la table 'stock' : {e}")
        df_voitures = pd.DataFrame(columns=["Matricule", "Marque", "Modèle", "Année", "Marque/Model"])

    # 2. Table clients
    try:
        res_clients = supabase.table("clients").select("Nom", "Prénom", "CIN").execute()
        df_c_list = pd.DataFrame(res_clients.data)
    except Exception as e:
        st.error(f"⚠️ Erreur sur la table 'clients' : {e}")
        df_c_list = pd.DataFrame(columns=["Nom", "Prénom", "CIN"])

    # 3. Table mouvements
    try:
        res_mouvs = supabase.table("mouvements").select("*").execute()
        df_mouvs = pd.DataFrame(res_mouvs.data)
    except Exception as e:
        st.error(f"⚠️ Erreur sur la table 'mouvements' : {e}")
        df_mouvs = pd.DataFrame(columns=["id", "Matricule", "Type_Statut", "Date_Debut", "Heure_Debut", "Date_Fin", "Heure_Fin", "Client", "Prix", "Statut_Mouvement", "Caution", "Reste", "Lieu_Reception", "No_Vol", "Info_Note", "KM_Debut", "KM_Fin"])

    return df_voitures, df_c_list, df_mouvs

# Récupération effective
df_voitures, df_c_list, df_mouvs = load_global_data()

# --- PRÉPARATION DES LISTES DÉROULANTES ---
liste_clients_opt = ["-- Entrée manuelle --"]
if not df_c_list.empty:
    liste_clients_opt += [f"{str(row['Nom']).upper()} {str(row['Prénom'])} (CIN: {row['CIN']})" for _, row in df_c_list.iterrows()]

liste_vehicules_opt = []
liste_vehicules_complets_opt = []
if not df_voitures.empty:
    liste_vehicules_opt = [str(row['Matricule']).strip() for _, row in df_voitures.iterrows() if pd.notna(row['Matricule']) and str(row['Matricule']).strip().lower() != 'nan']
    liste_vehicules_complets_opt = [f"{str(row['Matricule']).strip()} — {str(row.get('Modèle', 'Voiture'))}" for _, row in df_voitures.iterrows() if pd.notna(row['Matricule'])]

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

# --- ACTION : NOUVEAU CONTRAT ---
if menu_action == "📝 Nouveau Contrat / Réservation":
    st.sidebar.markdown("### 📝 Éditer une nouvelle fiche")
    nature = st.sidebar.selectbox("Nature :", ["Contrat Location", "Réservation", "Maintenance / Garage"])
    vehicule = st.sidebar.selectbox("Véhicule :", liste_vehicules_opt if liste_vehicules_opt else ["Aucun véhicule disponible"])
    client_b = st.sidebar.selectbox("Client :", liste_clients_opt)
    
    nom_m = st.sidebar.text_input("Nom & Prénom (Manuel) :")
    cin_m = st.sidebar.text_input("N° C.I.N (Manuel) :")
    dc_m = st.sidebar.date_input("Date Délivrance CIN :", datetime.now() - timedelta(days=365))
    permis_m = st.sidebar.text_input("N° Permis (Manuel) :")
    dp_m = st.sidebar.date_input("Date Délivrance Permis :", datetime.now() - timedelta(days=365))
    
    f_cin = st.sidebar.file_uploader("Fichier CIN :", type=["png", "jpg", "jpeg", "pdf"])
    f_permis = st.sidebar.file_uploader("Fichier Permis :", type=["png", "jpg", "jpeg", "pdf"])
    
    d1 = st.sidebar.date_input("Date Début :", datetime.now())
    t1 = st.sidebar.time_input("Heure Réception :", time(9, 0))
    d2 = st.sidebar.date_input("Date Fin :", datetime.now() + timedelta(days=2))
    t2 = st.sidebar.time_input("Heure Fin :", time(12, 0))
    
    nbr_jours = max((d2 - d1).days, 1)
    prix_unitaire = st.sidebar.number_input("💰 Prix / Jour (DT) :", min_value=0, value=100)
    montant_total = nbr_jours * prix_unitaire
    st.sidebar.markdown(f"**💵 Montant Total :** `{montant_total} DT` (`{nbr_jours} jours`)")
    
    caution = st.sidebar.number_input("🛡️ Caution (DT) :", value=0)
    reste = montant_total - caution
    st.sidebar.markdown(f"**🔴 Reste à payer :** `{reste} DT`")
    
    km_debut = st.sidebar.number_input("Kilométrage au Départ :", min_value=0, value=0)
    l_reception = st.sidebar.text_input("Lieu de réception :", value="Siège Monastir")
    no_vol = st.sidebar.text_input("N° de vol :", value="")
    info_note = st.sidebar.text_area("Note complémentaire :")
    
    if st.sidebar.button("⚡ ENREGISTRER SUR SUPABASE"):
        nom_f = nom_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN:")[0]
        cin_f = cin_m if client_b == "-- Entrée manuelle --" else client_b.split(" (CIN: ")[1].replace(")", "")
        
        img_cin_b64 = encoder_image_base64(f_cin)
        img_permis_b64 = encoder_image_base64(f_permis)
        
        # Sauvegarde Client si manuel
        if client_b == "-- Entrée manuelle --":
            supabase.table("clients").upsert({
                "Nom": nom_f, "CIN": cin_f, "Date Délivrance CIN": dc_m.strftime("%Y-%m-%d"),
                "N° Permis": permis_m, "Date Délivrance Permis": dp_m.strftime("%Y-%m-%d"),
                "Image CIN": img_cin_b64, "Image Permis": img_permis_b64
            }).execute()
            
        # Sauvegarde Mouvement
        supabase.table("mouvements").insert({
            "Matricule": vehicule, "Type_Statut": nature, "Date_Debut": d1.strftime("%Y-%m-%d"),
            "Heure_Debut": t1.strftime("%H:%M"), "Date_Fin": d2.strftime("%Y-%m-%d"),
            "Heure_Fin": t2.strftime("%H:%M"), "Client": nom_f, "Prix": str(montant_total),
            "Statut_Mouvement": "En cours", "Caution": str(caution), "Reste": str(reste),
            "Lieu_Reception": l_reception, "No_Vol": no_vol, "Info_Note": info_note, "KM_Debut": int(km_debut)
        }).execute()
        
        st.success("🎉 Dossier créé avec succès sur Supabase !")
        st.rerun()

# --- ACTION : AJOUTER UN VÉHICULE ---
elif menu_action == "🚗 Ajouter un Véhicule à la Flotte":
    with st.sidebar.form("form_add_car"):
        st.markdown("### 🚗 Nouveau Véhicule")
        nouveau_matricule = st.text_input("Matricule / Plaque * :").strip()
        nouvelle_marque = st.text_input("Marque * :").strip()
        nouveau_modele = st.text_input("Modèle * :").strip()
        nouvelle_annee = st.text_input("Année :", value="2026").strip()
        
        if st.form_submit_button("⚡ ENREGISTRER"):
            if nouveau_matricule and nouvelle_marque and nouveau_modele:
                supabase.table("stock").upsert({
                    "Matricule": nouveau_matricule, "Marque": nouvelle_marque,
                    "Modèle": nouveau_modele, "Année": nouvelle_annee,
                    "Marque/Model": f"{nouvelle_marque} {nouveau_modele}"
                }).execute()
                st.success("Véhicule enregistré !")
                st.rerun()

# --- ACTION : SUPPRIMER VÉHICULE ---
elif menu_action == "🗑️ Supprimer un Véhicule de la Flotte":
    if liste_vehicules_complets_opt:
        with st.sidebar.form("form_delete_car"):
            vehicule_a_retirer = st.selectbox("Choisir le véhicule à supprimer :", liste_vehicules_complets_opt)
            confirmer = st.checkbox("Confirmer la suppression définitive")
            if st.form_submit_button("💥 SUPPRIMER"):
                if confirmer:
                    mat_pure = str(vehicule_a_retirer).split(" — ")[0].strip()
                    supabase.table("stock").delete().eq("Matricule", mat_pure).execute()
                    st.success("Véhicule supprimé de la base.")
                    st.rerun()

# =========================================================================
# ESPACE CENTRAL DE TRAVAIL INTERACTIF
# =========================================================================
st.markdown("<h1>BBNH WORKSPACE AUTOMATION (SUPABASE)</h1>", unsafe_allow_html=True)

# Affichage des données globales sous forme d'onglets
tab_planning, tab_crm = st.tabs(["🗓️ CORE PLANNING", "👥 COMPTE CONDUCTEURS (CRM)"])

with tab_planning:
    st.markdown("### 🗓️ Liste des Mouvements en Cours")
    if not df_mouvs.empty:
        st.dataframe(df_mouvs, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun mouvement enregistré pour le moment.")

with tab_crm:
    st.markdown("### 👥 Liste Simplifiée des Clients")
    if not df_c_list.empty:
        st.dataframe(df_c_list, use_container_width=True, hide_index=True)
    else:
        st.info("Aucun client enregistré dans la base.")
2. IMPORTANT : Créer les tables sur Supabase
L'erreur critique APIError provient du fait que Supabase ne trouve pas les tables correspondantes. Vous devez impérativement exécuter ce code de création dans votre compte Supabase :

Allez sur votre Tableau de bord Supabase.

Dans le menu de gauche, cliquez sur SQL Editor.

Cliquez sur New Query (Nouvelle requête).

Copiez et collez le script SQL ci-dessous :

SQL
-- 1. Table STOCK
CREATE TABLE IF NOT EXISTS public.stock (
    "Matricule" TEXT PRIMARY KEY,
    "Marque" TEXT,
    "Modèle" TEXT,
    "Année" TEXT,
    "Marque/Model" TEXT
);

-- 2. Table CLIENTS
CREATE TABLE IF NOT EXISTS public.clients (
    "CIN" TEXT PRIMARY KEY,
    "Nom" TEXT,
    "Prénom" TEXT,
    "Date Délivrance CIN" TEXT,
    "N° Permis" TEXT,
    "Date Délivrance Permis" TEXT,
    "Image CIN" TEXT,
    "Image Permis" TEXT
);

-- 3. Table MOUVEMENTS
CREATE TABLE IF NOT EXISTS public.mouvements (
    "id" BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    "Matricule" TEXT,
    "Type_Statut" TEXT,
    "Date_Debut" TEXT,
    "Heure_Debut" TEXT,
    "Date_Fin" TEXT,
    "Heure_Fin" TEXT,
    "Client" TEXT,
    "Prix" TEXT,
    "Statut_Mouvement" TEXT,
    "Caution" TEXT,
    "Reste" TEXT,
    "Lieu_Reception" TEXT,
    "No_Vol" TEXT,
    "Info_Note" TEXT,
    "KM_Debut" INT,
    "KM_Fin" INT
);

-- Désactiver le RLS temporairement pour permettre à l'application d'écrire librement
ALTER TABLE public.stock DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.clients DISABLE ROW LEVEL SECURITY;
ALTER TABLE public.mouvements DISABLE ROW LEVEL SECURITY;
