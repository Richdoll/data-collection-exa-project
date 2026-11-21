import re
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def clean_number(text):
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", str(text))
    return float(digits) if digits else None

def scrape_and_clean_gaaraas(start_page=1, end_page=100):
    driver = get_driver()
    records = []
    
    try:
        for page in range(start_page, end_page + 1):
            url = f"https://www.gaaraas.com/fr/users/dakar-auto?page={page}"
            driver.get(url)
            time.sleep(2)
            
            ad_links = [
                el.get_attribute("href")
                for el in driver.find_elements(By.CSS_SELECTOR, "a[href*='/fr/']")
                if "/annonces/" in (el.get_attribute("href") or "")
            ]
            ad_links = list(dict.fromkeys(ad_links))
            
            for ad_url in ad_links:
                driver.get(ad_url)
                time.sleep(1)
                
                specs = {}
                spec_items = driver.find_elements(By.CSS_SELECTOR, "li, tr, div.spec-item")
                for item in spec_items:
                    txt = item.text.strip()
                    if ":" in txt:
                        k, v = txt.split(":", 1)
                        specs[k.strip().lower()] = v.strip()
                
                raw_price = ""
                price_els = driver.find_elements(By.CSS_SELECTOR, ".price, [class*='price']")
                if price_els:
                    raw_price = price_els[0].text
                
                records.append({
                    "marque": specs.get("marque", "Non spécifié").title(),
                    "modele": specs.get("modèle", specs.get("modele", "Non spécifié")).title(),
                    "annee": int(clean_number(specs.get("année", specs.get("annee", 0))) or 0),
                    "prix": clean_number(raw_price),
                    "kilometrage": clean_number(specs.get("kilométrage", specs.get("kilometrage", 0))),
                    "boite_vitesses": specs.get("boîte de vitesses", specs.get("boite de vitesses", "Non spécifié")).capitalize(),
                    "region": specs.get("région", specs.get("region", "Dakar")).title()
                })
    finally:
        driver.quit()
        
    df = pd.DataFrame(records)
    if not df.empty:
        df = df.dropna(subset=["prix"])
        df = df[df["annee"] > 1980]
        df = df.drop_duplicates()
    return df
