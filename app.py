import os
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import Flask, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

app = Flask(__name__)

# Kendi bilgisayarındaki veri klasörü
BASE_DIR = "/tmp/deprem_api"  # Render platformu için geçici dizin
FORMATS = ["json", "xml", "html", "csv"]
for fmt in FORMATS:
    os.makedirs(os.path.join(BASE_DIR, fmt), exist_ok=True)

@app.route('/api/deprem', methods=['GET'])
def get_earthquakes():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Selenium WebDriver ayarları
    options = Options()
    options.add_argument('--headless')  # Tarayıcıyı arka planda çalıştırmak için
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    url = "http://www.koeri.boun.edu.tr/scripts/lst9.asp"
    driver.get(url)

    pre_tag = driver.find_element(By.TAG_NAME, "pre").text
    driver.quit()

    lines = pre_tag.split("\n")[6:]
    earthquakes = []

    for line in lines:
        parts = line.split()
        if len(parts) < 6:
            continue
        try:
            eq = {
                "tarih": parts[0],
                "saat": parts[1],
                "enlem": parts[2],
                "boylam": parts[3],
                "derinlik_km": parts[4],
                "buyukluk": parts[5],
                "yer": " ".join(parts[6:])
            }
            earthquakes.append(eq)
        except:
            continue

    if not earthquakes:
        return jsonify({"message": "Veri bulunamadı"}), 404

    # JSON dosyası oluştur
    json_path = os.path.join(BASE_DIR, "json", f"deprem_{now}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(earthquakes, f, ensure_ascii=False, indent=4)

    # XML
    root = ET.Element("depremler")
    for eq in earthquakes:
        item = ET.SubElement(root, "deprem")
        for key, value in eq.items():
            ET.SubElement(item, key).text = value
    xml_path = os.path.join(BASE_DIR, "xml", f"deprem_{now}.xml")
    tree = ET.ElementTree(root)
    tree.write(xml_path, encoding="utf-8", xml_declaration=True)

    # HTML
    html_content = "<html><body><h1>Son Depremler</h1><ul>"
    for eq in earthquakes:
        html_content += f"<li><strong>{eq['yer']}</strong> - {eq['tarih']} {eq['saat']} - M {eq['buyukluk']} - Derinlik: {eq['derinlik_km']} km</li><hr>"
    html_content += "</ul></body></html>"
    html_path = os.path.join(BASE_DIR, "html", f"deprem_{now}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # CSV
    csv_path = os.path.join(BASE_DIR, "csv", f"deprem_{now}.csv")
    with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["tarih", "saat", "enlem", "boylam", "derinlik_km", "buyukluk", "yer"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for eq in earthquakes:
            writer.writerow(eq)

    return jsonify(earthquakes)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
