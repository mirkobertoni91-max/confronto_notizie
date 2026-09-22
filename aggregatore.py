#!/usr/bin/env python3
"""
Aggregatore di notizie multilingua con traduzione automatica in italiano.
Utilizza feed RSS e LibreTranslate (o Google Translate non ufficiale).
"""

import feedparser
import json
import requests
import time
from datetime import datetime
from pathlib import Path

# ============ CONFIGURAZIONE ============
FEEDS = [
    # Feed in inglese
    {"url": "https://feeds.bbci.co.uk/news/world/rss.xml", "lingua": "en", "fonte": "BBC World"},
    {"url": "https://rss.cnn.com/rss/edition_world.rss", "lingua": "en", "fonte": "CNN World"},
    {"url": "https://feeds.reuters.com/reuters/worldNews", "lingua": "en", "fonte": "Reuters World"},
    # Feed in spagnolo
    {"url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada", "lingua": "es", "fonte": "El País"},
    # Feed in francese
    {"url": "https://www.lemonde.fr/international/rss_full.xml", "lingua": "fr", "fonte": "Le Monde"},
    # Feed in tedesco
    {"url": "https://www.spiegel.de/international/index.rss", "lingua": "de", "fonte": "Der Spiegel"},
    # Feed in italiano (non tradotti)
    {"url": "https://www.ansa.it/sito/ansait_rss.xml", "lingua": "it", "fonte": "ANSA"},
    {"url": "https://www.repubblica.it/rss/homepage/rss2.0.xml", "lingua": "it", "fonte": "Repubblica"},
]

# Usa l'endpoint non ufficiale di Google Translate (gratuito, senza chiave)
TRANSLATE_URL = "https://translate.googleapis.com/translate_a/single"

def traduci_testo(testo, lingua_sorgente="auto", lingua_target="it"):
    """Traduce un testo usando l'endpoint non ufficiale di Google Translate."""
    if not testo or lingua_sorgente == lingua_target:
        return testo
    
    try:
        params = {
            "client": "gtx",
            "sl": lingua_sorgente,
            "tl": lingua_target,
            "dt": "t",
            "q": testo
        }
        response = requests.get(TRANSLATE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Estrai il testo tradotto dalla risposta
        if data and data[0]:
            return "".join([segmento[0] for segmento in data[0] if segmento[0]])
        return testo
    except Exception as e:
        print(f"Errore traduzione: {e}")
        return testo  # Restituisci l'originale in caso di errore

def raccogli_notizie():
    """Raccoglie le notizie da tutti i feed RSS configurati."""
    tutte_le_notizie = []
    
    for feed_config in FEEDS:
        print(f"📡 Raccolta da: {feed_config['fonte']}...")
        try:
            feed = feedparser.parse(feed_config["url"])
            
            for entry in feed.entries[:10]:  # Prendi le prime 10 notizie per feed
                titolo = entry.get("title", "")
                sommario = entry.get("summary", entry.get("description", ""))[:500]
                link = entry.get("link", "#")
                
                # Traduci se la lingua non è italiano
                if feed_config["lingua"] != "it":
                    print(f"   🌐 Traduzione: {titolo[:50]}...")
                    titolo_it = traduci_testo(titolo, feed_config["lingua"], "it")
                    sommario_it = traduci_testo(sommario, feed_config["lingua"], "it")
                    time.sleep(0.5)  # Rispetta i limiti di velocità
                else:
                    titolo_it = titolo
                    sommario_it = sommario
                
                tutte_le_notizie.append({
                    "titolo": titolo_it,
                    "titolo_originale": titolo,
                    "sommario": sommario_it,
                    "link": link,
                    "fonte": feed_config["fonte"],
                    "lingua_originale": feed_config["lingua"],
                    "data": entry.get("published", datetime.now().isoformat())
                })
        except Exception as e:
            print(f"   ❌ Errore con {feed_config['fonte']}: {e}")
    
    return tutte_le_notizie

def salva_json(notizie):
    """Salva le notizie in un file JSON per il frontend."""
    output_dir = Path("data")
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / "notizie.json"
    
    risultato = {
        "aggiornato": datetime.now().isoformat(),
        "totale_notizie": len(notizie),
        "notizie": notizie
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(risultato, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Salvate {len(notizie)} notizie in {output_file}")

def main():
    print("🚀 Avvio aggregatore di notizie...\n")
    notizie = raccogli_notizie()
    salva_json(notizie)
    print("🎉 Completato!")

if _name_ == "_main_":
    main()
