import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(page_title="AI Analiz Pro", layout="wide")

if "api_key" not in st.session_state: st.session_state["api_key"] = ""
if "maclar" not in st.session_state: st.session_state["maclar"] = []

# --- MODEL AYARI (EN STABİL SÜRÜM) ---
# Hata aldığın 'gemini-3-flash' yerine en geniş destekli 'gemini-1.5-flash' kullanıyoruz.
MODEL_NAME = 'gemini-1.5-flash'

def ai_getir(prompt):
    try:
        genai.configure(api_key=st.session_state["api_key"])
        model = genai.GenerativeModel(MODEL_NAME)
        # Güvenlik ayarlarını gevşeterek maç verilerinin engellenmesini önlüyoruz
        response = model.generate_content(prompt, safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ])
        return response.text
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

# --- YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Panel Ayarları")
    key = st.text_input("Gemini API Key:", value=st.session_state["api_key"], type="password")
    if st.button("Anahtarı Tanımla"):
        st.session_state["api_key"] = key
        st.success("Aktif!")

# --- ANA EKRAN ---
st.title("⚽ Akıllı Maç Bülteni ve Analiz")

if not st.session_state["api_key"]:
    st.warning("Lütfen sol menüden API Key girip 'Tanımla' butonuna basın.")
else:
    tarih = st.date_input("Bir Tarih Seçin", datetime.now())
    
    if st.button("📅 Seçili Tarihin Maçlarını Listele"):
        with st.spinner("Bülten taranıyor..."):
            prompt = f"{tarih} tarihindeki önemli futbol maçlarını 'Ev Sahibi - Deplasman' formatında, aralarına sadece virgül koyarak yaz. Başka hiçbir açıklama yapma."
            ham_veri = ai_getir(prompt)
            if "Hata" not in ham_veri:
                st.session_state["maclar"] = [m.strip() for m in ham_veri.split(",") if "-" in m]
                st.success(f"{len(st.session_state['maclar'])} maç bulundu!")
            else:
                st.error(ham_veri)

    if st.session_state["maclar"]:
        secilen_mac = st.selectbox("Analiz edilecek maçı listeden seçin:", st.session_state["maclar"])
        lig_adi = st.text_input("Lig Adı:", "Süper Lig")

        if st.button("🔥 ŞİMDİ ANALİZ ET"):
            with st.spinner(f"{secilen_mac} analiz ediliyor..."):
                analiz_prompt = f"""
                Bugün {tarih}, {lig_adi} liginde {secilen_mac} maçı oynanacak.
                1. Bu maçın ligin kaçıncı haftası olduğunu bul.
                2. Her iki takımın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı Markdown tablosunda göster. 
                Sütunlar: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                3. 'AI Strateji' başlığıyla takımların o haftadaki karakteristiğini ve İY/MS sürprizlerini yorumla.
                """
                sonuc = ai_getir(analiz_prompt)
                st.markdown(sonuc)
