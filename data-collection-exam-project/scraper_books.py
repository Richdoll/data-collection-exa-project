import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def scrape_and_clean_books(start_page=1, end_page=50):
    driver = get_driver()
    records = []
    
    try:
        for page in range(start_page, end_page + 1):
            url = f"https://books.toscrape.com/catalogue/page-{page}.html"
            driver.get(url)
            
            book_elements = driver.find_elements(By.CSS_SELECTOR, "article.product_pod h3 a")
            book_urls = [el.get_attribute("href") for el in book_elements]
            
            for book_url in book_urls:
                driver.get(book_url)
                
                titre = driver.find_element(By.CSS_SELECTOR, "div.product_main h1").text.strip()
                raw_price = driver.find_element(By.CSS_SELECTOR, "p.price_color").text
                prix = float(re.sub(r"[^\d.]", "", raw_price))
                
                raw_avail = driver.find_element(By.CSS_SELECTOR, "p.instock.availability").text.strip()
                disponibilite = "En stock" if "In stock" in raw_avail else "Rupture de stock"
                stock_match = re.search(r"\((\d+)\s+available\)", raw_avail)
                nombre_produits = int(stock_match.group(1)) if stock_match else 0
                
                rating_class = driver.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
                rating_word = [c for c in rating_class.split() if c != "star-rating"][0]
                note = RATING_MAP.get(rating_word, 0)
                
                desc_els = driver.find_elements(By.CSS_SELECTOR, "#product_description + p")
                description = desc_els[0].text.strip() if desc_els else "Aucune description"
                
                breadcrumbs = driver.find_elements(By.CSS_SELECTOR, "ul.breadcrumb li a")
                categorie = breadcrumbs[2].text.strip() if len(breadcrumbs) > 2 else "Inconnu"
                
                rows = driver.find_elements(By.CSS_SELECTOR, "table.table-striped tr")
                table_data = {}
                for row in rows:
                    th = row.find_element(By.TAG_NAME, "th").text.strip()
                    td = row.find_element(By.TAG_NAME, "td").text.strip()
                    table_data[th] = td
                
                tax = float(re.sub(r"[^\d.]", "", table_data.get("Tax", "0")))
                nombre_reviews = int(table_data.get("Number of reviews", 0))
                
                records.append({
                    "titre": titre,
                    "prix": prix,
                    "disponibilite": disponibilite,
                    "nombre_produits": nombre_produits,
                    "note": note,
                    "nombre_reviews": nombre_reviews,
                    "description": description,
                    "categorie": categorie,
                    "tax": tax
                })
    finally:
        driver.quit()
        
    df = pd.DataFrame(records).drop_duplicates(subset=["titre"])
    return df
