import streamlit as st
import google.generativeai as genai
from datetime import datetime

st.set_page_config(page_title="AI Analiz Pro", layout="wide")

if "api_key" not in st.session_state: st.session_state["api_key"] = ""
if "maclar" not in st.session_state: st.session_state["maclar"] = []

# --- MODEL AYARI (TAM YOL VE STABİL SÜRÜM) ---
# 404 hatasını önlemek için modelin tam sistem adını kullanıyoruz.
MODEL_NAME = 'models/gemini-1.5-flash'

def ai_getir(prompt):
    try:
        genai.configure(api_key=st.session_state["api_key"])
        # v1beta yerine standart stable sürümü hedefliyoruz
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hata mesajını daha detaylı görelim
        return f"Hata Detayı: {str(e)}"

# --- YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Panel Ayarları")
    key = st.text_input("Gemini API Key:", value=st.session_state["api_key"], type="password")
    if st.button("Anahtarı Tanımla"):
        st.session_state["api_key"] = key
        st.success("Sistem Hazır!")

# --- ANA EKRAN ---
st.title("⚽ Akıllı Maç Bülteni ve Analiz")

if not st.session_state["api_key"]:
    st.warning("Lütfen sol menüden API Key girip 'Tanımla' butonuna basın.")
else:
    tarih = st.date_input("Bir Tarih Seçin", datetime.now())
    
    if st.button("📅 Seçili Tarihin Maçlarını Listele"):
        with st.spinner("Bülten taranıyor..."):
            prompt = f"{tarih} tarihindeki önemli futbol maçlarını 'Ev Sahibi - Deplasman' formatında, aralarına sadece virgül koyarak yaz. Başka hiçbir şey yazma."
            ham_veri = ai_getir(prompt)
            
            if "Hata" not in ham_veri:
                # Gelen metni temizleyip listeye çeviriyoruz
                liste = [m.strip() for m in ham_veri.split(",") if "-" in m]
                if liste:
                    st.session_state["maclar"] = liste
                    st.success(f"{len(liste)} maç bulundu!")
                else:
                    st.error("Maç listesi alınamadı, lütfen tekrar deneyin.")
            else:
                st.error(ham_veri)

    if st.session_state["maclar"]:
        secilen_mac = st.selectbox("Analiz edilecek maçı seçin:", st.session_state["maclar"])
        lig_adi = st.text_input("Lig Adı:", "Süper Lig")

        if st.button("🔥 ŞİMDİ ANALİZ ET"):
            with st.spinner(f"{secilen_mac} analiz ediliyor..."):
                analiz_prompt = f"""
                Bugün {tarih}, {lig_adi} liginde {secilen_mac} maçı var.
                1. Bu maçın ligin kaçıncı haftası olduğunu bul.
                2. Her iki takımın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı Markdown tablosunda göster. 
                Sütunlar: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY / MS.
                3. 'AI Strateji' başlığıyla takımların o haftadaki karakteristiğini ve İY/MS sürprizlerini yorumla.
                """
                sonuc = ai_getir(analiz_prompt)
                st.markdown(sonuc)
