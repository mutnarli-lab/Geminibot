import streamlit as st
import requests
import json
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="AI Analiz Pro", layout="wide")

# --- HAFIZA KİLİDİ ---
if "api_key" not in st.session_state: st.session_state.api_key = ""
if "maclar" not in st.session_state: st.session_state.maclar = []

# --- HAM API BAĞLANTISI (Kütüphane Kullanmadan) ---
def ai_getir(prompt):
    # Bu yöntem 'v1beta' hatasını %100 aşar çünkü doğrudan 'v1' kararlı sürümüne gider
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={st.session_state.api_key}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        res_json = response.json()
        
        if response.status_code == 200:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"API Hatası ({response.status_code}): {res_json.get('error', {}).get('message', 'Bilinmeyen Hata')}"
    except Exception as e:
        return f"Bağlantı Hatası: {str(e)}"

# --- YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Ayarlar")
    # Hafızadaki key'i inputa bağla
    key_input = st.text_input("Gemini API Key:", value=st.session_state.api_key, type="password")
    if st.button("Anahtarı Kaydet ve Kilitle"):
        st.session_state.api_key = key_input
        st.success("Anahtar başarıyla kilitlendi!")

# --- ANA EKRAN ---
st.title("⚽ Akıllı Maç Bülteni ve Analiz")

if not st.session_state.api_key:
    st.info("Lütfen sol taraftan API Key girip 'Kilitle' butonuna basın.")
else:
    tarih = st.date_input("Analiz Tarihi", datetime.now())
    
    if st.button("📅 Maçları Listele"):
        with st.spinner("Bülten taranıyor..."):
            prompt = f"{tarih} tarihindeki önemli futbol maçlarını 'Ev Sahibi - Deplasman' formatında, aralarına sadece virgül koyarak yaz. Başka hiçbir şey yazma."
            ham_veri = ai_getir(prompt)
            
            if "API Hatası" not in ham_veri:
                liste = [m.strip() for m in ham_veri.split(",") if "-" in m]
                st.session_state.maclar = liste
                st.success(f"{len(liste)} maç bulundu!")
            else:
                st.error(ham_veri)

    if st.session_state.maclar:
        secilen_mac = st.selectbox("Maç Seçin:", st.session_state.maclar)
        
        if st.button("🔥 ANALİZ ET"):
            with st.spinner("İstatistikler getiriliyor..."):
                analiz_prompt = f"""
                Bugün {tarih}, {secilen_mac} maçı oynanacak.
                1. Bu maçın ligin kaçıncı haftası olduğunu bul.
                2. Her iki takımın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı tabloda göster. 
                Sütunlar: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                3. 'AI Strateji' başlığıyla yorumla.
                """
                sonuc = ai_getir(analiz_prompt)
                st.markdown(sonuc)
