import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="AI Futbol Analiz", layout="wide")

# --- SOL MENÜ (API AYARI) ---
with st.sidebar:
    st.title("⚙️ Ayarlar")
    api_key = st.text_input("Gemini API Key Giriniz:", type="password")
    st.info("API Key'i 'Google AI Studio' sitesinden ücretsiz alabilirsiniz.")

# --- ANA EKRAN ---
st.title("🤖 AI Destekli Maç Analiz Paneli")
st.write("Seçtiğiniz maçın lig haftasını bulur ve son 5 sezonun verilerini karşılaştırır.")

col1, col2, col3 = st.columns(3)
with col1:
    tarih = st.date_input("Maç Tarihi", datetime.now())
with col2:
    lig = st.selectbox("Lig Seçin", ["Süper Lig", "Premier Lig", "Brezilya Serie A", "Hollanda Eerste Divisie", "Bundesliga"])
with col3:
    mac_adi = st.text_input("Maç (Örn: Fenerbahçe - Beşiktaş)")

if st.button("ANALİZİ BAŞLAT"):
    if not api_key:
        st.error("Lütfen önce sol menüden API Key giriniz!")
    elif not mac_adi:
        st.warning("Lütfen bir maç ismi girin.")
    else:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('Yapay Zeka verileri tarıyor ve tabloları oluşturuyor...'):
                prompt = f"""
                Bugün {tarih}, {lig} liginde {mac_adi} maçı oynanacak.
                1. Bu maçın ligin kaçıncı haftası olduğunu kesin olarak bul.
                2. Ev sahibi ve Deplasman takımlarının son 5 sezondaki O HAFTAYA (örneğin 28. hafta) denk gelen maçlarını bul.
                3. Verileri şu sütunlarla iki ayrı Markdown tablosu olarak sun: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                4. En alta 'AI Strateji ve Tahmin' başlığıyla; İY/MS sürprizleri, gol beklentisi ve takımların o haftadaki karakteristiğini yorumla.
                Not: Sadece gerçek verileri kullan, 'Sıfır Hata' prensibiyle çalış.
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")

# Alt Bilgi
st.markdown("---")
st.caption("Veriler Gemini AI tarafından anlık olarak taranmaktadır.")
