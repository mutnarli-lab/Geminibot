import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="AI Analiz Pro", layout="wide")

# --- HAFIZA (Session State) ---
if "api_key" not in st.session_state: st.session_state["api_key"] = ""
if "maclar" not in st.session_state: st.session_state["maclar"] = []

# --- MODEL AYARI (2026 GÜNCEL) ---
# Hata veren 'gemini-1.5-flash' yerine en hızlı model olan 'gemini-3-flash' kullanıyoruz.
MODEL_NAME = 'gemini-3-flash'

def ai_getir(prompt):
    try:
        genai.configure(api_key=st.session_state["api_key"])
        model = genai.GenerativeModel(MODEL_NAME)
        return model.generate_content(prompt).text
    except Exception as e:
        return f"Hata: {str(e)}"

# --- YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Panel Ayarları")
    key = st.text_input("Gemini API Key:", value=st.session_state["api_key"], type="password")
    if st.button("Anahtarı Tanımla"):
        st.session_state["api_key"] = key
        st.success("Aktif!")
    st.info("Model: Gemini 3 Flash (Ultra Hızlı)")

# --- ANA EKRAN ---
st.title("⚽ Akıllı Maç Bülteni ve Analiz")

if not st.session_state["api_key"]:
    st.warning("Lütfen sol menüden API Key girip 'Tanımla' butonuna basın.")
else:
    # 1. ADIM: BÜLTENİ ÇEK
    tarih = st.date_input("Bir Tarih Seçin", datetime.now())
    
    if st.button("📅 Seçili Tarihin Maçlarını Listele"):
        with st.spinner("Bülten taranıyor..."):
            # Botun bülteni bir liste (array) gibi getirmesini istiyoruz
            prompt = f"{tarih} tarihindeki önemli futbol maçlarını 'Takım A - Takım B' şeklinde, aralarına virgül koyarak liste yap. Sadece maç isimlerini ver."
            ham_veri = ai_getir(prompt)
            # Gelen metni listeye çeviriyoruz
            st.session_state["maclar"] = [m.strip() for m in ham_veri.split(",") if "-" in m]
            st.success(f"{len(st.session_state['maclar'])} maç bulundu!")

    # 2. ADIM: OTOMATİK SEÇİM KUTUSU
    if st.session_state["maclar"]:
        secilen_mac = st.selectbox("Analiz edilecek maçı listeden seçin:", st.session_state["maclar"])
        lig_adi = st.text_input("Lig Adı (Opsiyonel):", "Süper Lig")

        if st.button("🔥 ŞİMDİ ANALİZ ET"):
            with st.spinner(f"{secilen_mac} için son 5 sezon taranıyor..."):
                analiz_prompt = f"""
                Bugün {tarih}, {lig_adi} liginde {secilen_mac} maçı var.
                1. Bu maçın ligin kaçıncı haftası olduğunu bul.
                2. Ev sahibi ve deplasmanın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı tabloda göster. 
                Sütunlar: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                3. 'AI Strateji' başlığıyla İY/MS sürprizlerini ve karakteristiklerini yorumla.
                """
                sonuc = ai_getir(analiz_prompt)
                st.markdown(sonuc)
