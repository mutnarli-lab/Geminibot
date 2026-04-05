import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="AI Analiz Pro", layout="wide")

# --- KESİN HAFIZA KİLİDİ ---
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "maclar" not in st.session_state:
    st.session_state.maclar = []

# --- MODEL BAĞLANTI (GÜNCELLENMİŞ PROTOKOL) ---
def ai_getir(prompt):
    try:
        genai.configure(api_key=st.session_state.api_key)
        # Model ismini 'latest' takısıyla çağırarak v1beta çakışmasını aşıyoruz
        model = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Eğer yine hata verirse alternatif model ismini dene
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model.generate_content(prompt).text
        except:
            return f"Kritik Bağlantı Hatası: {str(e)}"

# --- YAN PANEL ---
with st.sidebar:
    st.title("🛡️ Ayarlar")
    # Hafızadaki key'i inputa bağla
    st.session_state.api_key = st.text_input("Gemini API Key:", value=st.session_state.api_key, type="password")
    if st.button("Anahtarı Sisteme Kilitle"):
        st.success("Anahtar başarıyla kaydedildi!")

# --- ANA EKRAN ---
st.title("⚽ Akıllı Maç Bülteni ve Analiz")

if not st.session_state.api_key:
    st.info("Lütfen sol taraftan API Key girip 'Kilitle' butonuna basın.")
else:
    tarih = st.date_input("Analiz Tarihi", datetime.now())
    
    if st.button("📅 Maçları Listele"):
        with st.spinner("Bülten taranıyor..."):
            prompt = f"{tarih} tarihindeki önemli futbol maçlarını 'Ev Sahibi - Deplasman' formatında, aralarına sadece virgül koyarak yaz."
            ham_veri = ai_getir(prompt)
            
            if "Hata" not in ham_veri:
                liste = [m.strip() for m in ham_veri.split(",") if "-" in m]
                st.session_state.maclar = liste
                st.success(f"{len(liste)} maç bulundu!")
            else:
                st.error(ham_veri)

    if st.session_state.maclar:
        secilen_mac = st.selectbox("Maç Seçin:", st.session_state.maclar)
        
        if st.button("🔥 ANALİZ ET"):
            with st.spinner("Tablolar oluşturuluyor..."):
                analiz_prompt = f"""
                Bugün {tarih}, {secilen_mac} maçı oynanacak.
                1. Bu maçın ligin kaçıncı haftası olduğunu bul.
                2. Her iki takımın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı tabloda göster. 
                Sütunlar: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                3. 'AI Strateji' başlığıyla yorumla.
                """
                st.markdown(ai_getir(analiz_prompt))
