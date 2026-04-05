import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Sayfa Ayarları
st.set_page_config(page_title="AI Analiz Pro", layout="wide")

# --- HAFIZA YÖNETİMİ (Session State) ---
# Bu kısım sayfa yenilense de verilerin silinmemesini sağlar
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "maclar" not in st.session_state:
    st.session_state["maclar"] = []
if "bulten_tarihi" not in st.session_state:
    st.session_state["bulten_tarihi"] = None

# --- MODEL BAĞLANTI FONKSİYONU ---
def ai_getir(prompt):
    try:
        # En güncel ve stabil model ismini doğrudan string olarak veriyoruz
        genai.configure(api_key=st.session_state["api_key"])
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Hata Detayı: {str(e)}"

# --- YAN PANEL (API ANAHTARI BURADA ÇAKILI KALACAK) ---
with st.sidebar:
    st.title("🛡️ Panel Ayarları")
    # Kullanıcıdan key alırken mevcut hafızadaki key'i gösteriyoruz
    key_input = st.text_input("Gemini API Key:", value=st.session_state["api_key"], type="password")
    
    if st.button("Anahtarı Kaydet ve Kilitle"):
        st.session_state["api_key"] = key_input
        st.success("Anahtar hafızaya alındı!")
    
    if st.session_state["api_key"]:
        st.write("✅ Anahtar Aktif")
    else:
        st.warning("⚠️ Anahtar Bekleniyor")

# --- ANA EKRAN ---
st.title("⚽ Akıllı Maç Bülteni ve Analiz")

if not st.session_state["api_key"]:
    st.info("Lütfen sol taraftaki menüden API anahtarınızı girip 'Kaydet' butonuna basın. Bir kez yapmanız yeterlidir.")
else:
    # 1. ADIM: BÜLTENİ ÇEK
    tarih = st.date_input("Analiz Tarihi Seçin", datetime.now())
    
    # Eğer tarih değişirse maç listesini sıfırla ki eski maçlar görünmesin
    if st.session_state["bulten_tarihi"] != tarih:
        st.session_state["bulten_tarihi"] = tarih
        st.session_state["maclar"] = []

    if st.button("📅 Seçili Tarihin Maçlarını Listele"):
        with st.spinner("Yapay Zeka o günün bültenini tarıyor..."):
            prompt = f"{tarih} tarihindeki tüm popüler futbol liglerini ve önemli maçları 'Ev Sahibi - Deplasman' formatında, aralarına sadece virgül koyarak yaz. Başka hiçbir açıklama yapma."
            ham_veri = ai_getir(prompt)
            
            if "Hata" not in ham_veri:
                # Gelen metni listeye çevir ve boşlukları temizle
                liste = [m.strip() for m in ham_veri.split(",") if "-" in m]
                if liste:
                    st.session_state["maclar"] = liste
                    st.success(f"{len(liste)} maç bulundu!")
                else:
                    st.error("Maç listesi boş geldi. Lütfen tekrar 'Listele' butonuna basın.")
            else:
                st.error(ham_veri)

    # 2. ADIM: MAÇ SEÇİMİ VE ANALİZ
    if st.session_state["maclar"]:
        secilen_mac = st.selectbox("Analiz edilecek maçı listeden seçin:", st.session_state["maclar"])
        lig_adi = st.text_input("Lig Adı (Opsiyonel):", "Süper Lig")

        if st.button("🔥 ŞİMDİ DETAYLI ANALİZ ET"):
            with st.spinner(f"{secilen_mac} verileri toplanıyor..."):
                analiz_prompt = f"""
                Bugün {tarih}, {lig_adi} liginde {secilen_mac} maçı oynanacak.
                1. Bu maçın ligin kaçıncı haftası olduğunu kesin bul.
                2. Her iki takımın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı tabloda göster. 
                Sütunlar: Sezon, Karşılaşma (Ev-Dep), İY, MS, İY/MS.
                3. 'AI Strateji' başlığıyla takımların o haftadaki karakteristiğini ve İY/MS sürprizlerini yorumla.
                """
                sonuc = ai_getir(analiz_prompt)
                st.markdown(sonuc)
