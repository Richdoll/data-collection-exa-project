import streamlit as st
import pandas as pd
import plotly.express as px
from database import init_db, save_to_db, load_from_db
from scraper_books import scrape_and_clean_books
from scraper_gaaraas import scrape_and_clean_gaaraas

st.set_page_config(page_title="Data Collection & Dashboard", layout="wide")
init_db()

st.title("📊 Plateforme de Collecte, Nettoyage et Visualisation de Données")

menu = st.sidebar.radio(
    "Navigation",
    [
        "1. Scraping Multi-Pages (Selenium)",
        "2. Téléchargement Données Brutes (Web Scraper)",
        "3. Dashboard Données Nettoyées",
        "4. Évaluation de l'Application"
    ]
)

if menu == "1. Scraping Multi-Pages (Selenium)":
    st.header("🕷️ Collecte & Nettoyage de Données via Selenium")
    source = st.selectbox("Choisir la source de données :", ["Books to Scrape", "Gaaraas Auto Dakar"])
    
    col1, col2 = st.columns(2)
    max_p = 50 if source == "Books to Scrape" else 100
    start_page = col1.number_input("Page de début", min_value=1, max_value=max_p, value=1)
    end_page = col2.number_input("Page de fin", min_value=1, max_value=max_p, value=2)
    
    if st.button("Lancer le scraping et enregistrer en base SQL"):
        if start_page > end_page:
            st.error("La page de début doit être inférieure ou égale à la page de fin.")
        else:
            with st.spinner("Scraping et nettoyage en cours..."):
                if source == "Books to Scrape":
                    df_scraped = scrape_and_clean_books(start_page, end_page)
                    table = "books"
                else:
                    df_scraped = scrape_and_clean_gaaraas(start_page, end_page)
                    table = "gaaraas_auto"
                
                if not df_scraped.empty:
                    save_to_db(df_scraped, table, if_exists="append")
                    st.success(f"{len(df_scraped)} enregistrements nettoyés et sauvegardés dans '{table}' !")
                    st.dataframe(df_scraped)
                else:
                    st.warning("Aucune donnée extraite.")

elif menu == "2. Téléchargement Données Brutes (Web Scraper)":
    st.header("📥 Téléchargement des Données Brutes (No-Code Web Scraper)")
    st.write("Téléchargez les fichiers CSV bruts non nettoyés extraits via l'extension Chrome Web Scraper.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Source 1 : Books to Scrape")
        try:
            with open("data/raw_books_webscraper.csv", "rb") as f:
                st.download_button(
                    label="Télécharger CSV Brut - Books to Scrape",
                    data=f,
                    file_name="raw_books_webscraper.csv",
                    mime="text/csv"
                )
        except FileNotFoundError:
            st.info("Fichier raw_books_webscraper.csv en attente d'importation.")

    with col2:
        st.subheader("Source 2 : Gaaraas Auto Dakar")
        try:
            with open("data/raw_gaaraas_webscraper.csv", "rb") as f:
                st.download_button(
                    label="Télécharger CSV Brut - Gaaraas Auto",
                    data=f,
                    file_name="raw_gaaraas_webscraper.csv",
                    mime="text/csv"
                )
        except FileNotFoundError:
            st.info("Fichier raw_gaaraas_webscraper.csv en attente d'importation.")

elif menu == "3. Dashboard Données Nettoyées":
    st.header("📈 Tableau de Bord des Données Nettoyées (Base SQL)")
    tab1, tab2 = st.tabs(["Books to Scrape", "Gaaraas Auto Dakar"])
    
    with tab1:
        df_books = load_from_db("books")
        if df_books.empty:
            st.info("Aucune donnée disponible dans la table 'books'.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Livres", len(df_books))
            c2.metric("Prix Moyen (£)", f"{df_books['prix'].mean():.2f}")
            c3.metric("Note Moyenne", f"{df_books['note'].mean():.2f} / 5")
            
            fig_cat = px.bar(
                df_books["categorie"].value_counts().head(10).reset_index(),
                x="categorie", y="count", title="Top 10 Catégories de Livres"
            )
            st.plotly_chart(fig_cat, use_container_width=True)
            st.dataframe(df_books)

    with tab2:
        df_cars = load_from_db("gaaraas_auto")
        if df_cars.empty:
            st.info("Aucune donnée disponible dans la table 'gaaraas_auto'.")
        else:
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Annonces", len(df_cars))
            c2.metric("Prix Moyen (FCFA)", f"{df_cars['prix'].mean():,.0f}")
            c3.metric("Kilométrage Moyen", f"{df_cars['kilometrage'].mean():,.0f} km")
            
            fig_brand = px.bar(
                df_cars["marque"].value_counts().head(10).reset_index(),
                x="marque", y="count", title="Top 10 Marques Automobiles"
            )
            st.plotly_chart(fig_brand, use_container_width=True)
            st.dataframe(df_cars)

elif menu == "4. Évaluation de l'Application":
    st.header("📝 Évaluation de l'Application")
    st.write("Merci de remplir l'un des deux formulaires ci-dessous pour évaluer l'application :")
    
    KOBO_URL = "https://ee.kobotoolbox.org/x/VOTRE_LIEN_KOBO"
    GOOGLE_FORM_URL = "https://forms.gle/VOTRE_LIEN_GOOGLE_FORMS"
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Version KoboToolbox")
        st.link_button("Ouvrir le formulaire Kobo", KOBO_URL)
    with col2:
        st.subheader("Version Google Forms")
        st.link_button("Ouvrir le Google Form", GOOGLE_FORM_URL)
