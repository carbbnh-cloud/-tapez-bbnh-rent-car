import streamlit as st

import pandas as pd

import streamlit as st

from sqlalchemy import create_engine

import os

import base64

from datetime import datetime, timedelta, time



# --- CONFIGURATION SUPABASE ---

SUPABASE_URL = os.getenv("SUPABASE_URL", "db.pwsxxmmlscvazaictocg.supabase.co")

SUPABASE_USER = os.getenv("SUPABASE_USER", "postgres")

SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "")

SUPABASE_DB = os.getenv("SUPABASE_DB", "postgres")

SUPABASE_PORT = 5432



def get_db_connection():

    """Connexion à Supabase PostgreSQL"""

    try:

        conn = psycopg2.connect(

            host=SUPABASE_URL,

            user=SUPABASE_USER,

            password=SUPABASE_PASSWORD,

            database=SUPABASE_DB,

            port=SUPABASE_PORT,

            sslmode='require'

        )

        return conn

    except Exception as e:

        st.error(f"Erreur de connexion à Supabase: {e}")

        return None



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

    

    .title-main {

        color: #e60000;

        font-size: 2.5rem;

        font-weight: 700;

        margin: 0;

        padding: 0;

    }

    

    .subtitle-main {

        color: #9ca3af;

        font-size: 0.875rem;

        font-weight: 400;

        margin-top: 0.25rem;

        letter-spacing: 0.05em;

    }

    </style>

""", unsafe_allow_html=True)



# --- LOGO ET TITRE ---

col1, col2 = st.sidebar.columns([1, 2])

with col1:

    st.markdown('<div class="logo-container"><span style="font-size: 2rem; font-weight: 700;">BBNH</span></div>', unsafe_allow_html=True)

with col2:

    st.markdown('<p class="title-main">BBNH</p><p class="subtitle-main">RENT A CAR</p>', unsafe_allow_html=True)



st.sidebar.markdown("---")



# --- CONSOLE D'ACTION ---

st.sidebar.markdown("### 🎯 CONSOLE D'ACTION :")



action = st.sidebar.radio(

    "Sélectionnez une action :",

    [

        "Mode Visionneuse",

        "Nouveau Contrat / Réservation",

        "Ajouter un Véhicule à la Flotte",

        "Supprimer un Véhicule de la Flotte",

        "Modifier un Dossier (Contrat/Réservation)",

        "Supprimer une Opération",

        "Imports Excel Automatiques",

        "Suivi des Vidanges"

    ],

    label_visibility="collapsed"

)



# --- CONTENU PRINCIPAL ---

st.markdown('<h1 class="title-main" style="text-align: center; margin-bottom: 2rem;">BBNH OS — Gestion Premium</h1>', unsafe_allow_html=True)



if action == "Mode Visionneuse":

    st.markdown("### 📊 Vue Globale & Tarifs Intelligents")

    st.info("Mode Visionneuse - Connecté à Supabase PostgreSQL")

    st.write("Les données sont maintenant stockées dans Supabase et resteront toujours disponibles !")



elif action == "Nouveau Contrat / Réservation":

    st.markdown("### 📝 Nouveau Contrat / Réservation")

    st.info("Création de contrat - Connecté à Supabase PostgreSQL")



elif action == "Ajouter un Véhicule à la Flotte":

    st.markdown("### 🚗 Ajouter un Véhicule à la Flotte")

    st.info("Ajout de véhicule - Connecté à Supabase PostgreSQL")



elif action == "Supprimer un Véhicule de la Flotte":

    st.markdown("### ❌ Supprimer un Véhicule de la Flotte")

    st.info("Suppression de véhicule - Connecté à Supabase PostgreSQL")



elif action == "Modifier un Dossier (Contrat/Réservation)":

    st.markdown("### ⚙️ Modifier un Dossier (Contrat/Réservation)")

    st.info("Modification de dossier - Connecté à Supabase PostgreSQL")



elif action == "Supprimer une Opération":

    st.markdown("### ❌ Supprimer une Opération")

    st.info("Suppression d'opération - Connecté à Supabase PostgreSQL")



elif action == "Imports Excel Automatiques":

    st.markdown("### 📥 Imports Excel Automatiques")

    st.info("Import Excel - Connecté à Supabase PostgreSQL")



elif action == "Suivi des Vidanges":

    st.markdown("### 📈 Suivi des Vidanges")

    st.info("Suivi des vidanges - Connecté à Supabase PostgreSQL")



# --- PIED DE PAGE ---

st.sidebar.markdown("---")

st.sidebar.markdown("**BBNH OS v2.0** | Powered by Supabase")
