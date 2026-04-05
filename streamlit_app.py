import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Sayfa Yapılandırması
st.set_page_config(page_title="AI Futbol Analiz", layout="wide")

# --- HAFIZA YÖNETİMİ (Session State) ---
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""

# --- SOL MENÜ (API AYARI) ---
with st.sidebar:
    st.title("⚙️ Ayarlar")
    # Mevcut key'i hafızadan al, kutuya yaz
    temp_key = st.text_input("Gemini API Key Giriniz:", value=st.session_state["api_key"], type="password")
    
    if st.button("Anahtarı Uygula ve Kaydet"):
        st.session_state["api_key"] = temp_key
        st.success("API Anahtarı kaydedildi!")
    
    st.divider()
    st.info("Anahtarınız siz sayfayı yenileyene kadar hafızada tutulur.")

# --- ANA EKRAN ---
st.title("🤖 AI Destekli Maç Analiz Paneli")

# Form Yapısı (Butona basana kadar sayfa yenilenmez)
with st.form("analiz_formu"):
    col1, col2 = st.columns(2)
    with col1:
        tarih = st.date_input("Maç Tarihi", datetime.now())
        lig = st.selectbox("Lig Seçin", ["Süper Lig", "Premier Lig", "Brezilya Serie A", "Hollanda Eerste Divisie", "Bundesliga"])
    with col2:
        mac_adi = st.text_input("Maç (Örn: Fenerbahçe - Beşiktaş)")
    
    submit = st.form_submit_button("ANALİZİ BAŞLAT")

if submit:
    if not st.session_state["api_key"]:
        st.error("Lütfen önce sol menüden API Key girip 'Uygula ve Kaydet' butonuna basın!")
    elif not mac_adi:
        st.warning("Lütfen bir maç ismi girin.")
    else:
        try:
            genai.configure(api_key=st.session_state["api_key"])
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.spinner('Yapay Zeka verileri tarıyor ve tabloları oluşturuyor...'):
                prompt = f"""
                Bugün {tarih}, {lig} liginde {mac_adi} maçı oynanacak.
                1. Bu maçın ligin kaçıncı haftası olduğunu kesin olarak bul.
                2. Ev sahibi ve Deplasman takımlarının son 5 sezondaki O HAFTAYA denk gelen maçlarını bul.
                3. Verileri şu sütunlarla iki AYRI Markdown tablosu olarak sun: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                4. En alta 'AI Strateji ve Tahmin' başlığıyla; İY/MS sürprizleri, gol beklentisi ve takımların o haftadaki karakteristiğini yorumla.
                Not: Sadece gerçek verileri kullan, hata yapma.
                """
                
                response = model.generate_content(prompt)
                st.markdown(response.text)
                
        except Exception as e:
            st.error(f"Bir hata oluştu: {e}")
