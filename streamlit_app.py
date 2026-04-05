import streamlit as st
import google.generativeai as genai
from datetime import datetime, timedelta

st.set_page_config(page_title="AI Maç Analizi", layout="wide")

# --- HAFIZA YÖNETİMİ ---
if "api_key" not in st.session_state: st.session_state["api_key"] = ""
if "bulten" not in st.session_state: st.session_state["bulten"] = {}

# --- YARDIMCI FONKSİYONLAR ---
def ai_sorgu(prompt):
    genai.configure(api_key=st.session_state["api_key"])
    model = genai.GenerativeModel('gemini-1.5-flash')
    return model.generate_content(prompt).text

# --- YAN MENÜ ---
with st.sidebar:
    st.title("⚙️ Kurulum")
    temp_key = st.text_input("API Key:", value=st.session_state["api_key"], type="password")
    if st.button("Anahtarı Kaydet"):
        st.session_state["api_key"] = temp_key
        st.success("Kaydedildi!")

# --- ANA EKRAN ---
st.title("⚽ Otomatik Maç Analiz İstasyonu")

if not st.session_state["api_key"]:
    st.warning("Lütfen önce API Key girin.")
else:
    # 1. TARİH SEÇİMİ VE BÜLTEN ÇEKME
    tarih = st.date_input("Analiz Tarihi Seçin", datetime.now())
    
    if st.button("Bu Tarihteki Maçları Getir"):
        with st.spinner("Bülten hazırlanıyor..."):
            prompt = f"{tarih} tarihinde oynanacak olan önemli futbol liglerini ve bu liglerdeki maçları 'Lig Adı: Takım A - Takım B, Takım C - Takım D' formatında listeleyebilir misin?"
            bulten_raw = ai_sorgu(prompt)
            # Basit bir parser (burası yapay zeka çıktısını temizler)
            st.session_state["bulten_metin"] = bulten_raw
            st.success("Bülten güncellendi!")

    if "bulten_metin" in st.session_state:
        st.info("Aşağıdaki kutucuğa maç ismini kopyalayıp yapıştırabilir veya direkt analizi başlatabilirsiniz.")
        st.text_area("Günün Maçları", st.session_state["bulten_metin"], height=150)
        
        mac_secimi = st.text_input("Analiz Edilecek Maçı Yazın (Örn: Fenerbahçe - Beşiktaş)")
        lig_adi = st.text_input("Lig Adı (Örn: Süper Lig)")

        if st.button("DETAYLI ANALİZİ BAŞLAT"):
            with st.spinner("Son 5 sezonun 28. hafta verileri taranıyor..."):
                final_prompt = f"""
                {tarih} tarihindeki {lig_adi} ligi {mac_secimi} maçı için:
                1. Bu maçın ligin kaçıncı haftası olduğunu bul.
                2. Her iki takımın son 5 sezondaki O HAFTAYA ait maçlarını iki ayrı tabloda (Sezon, Karşılaşma, İY, MS, İY/MS) göster.
                3. 'AI Strateji' başlığıyla İY/MS sürpriz, gol ve karakteristik yorumu yap.
                """
                analiz_sonucu = ai_sorgu(final_prompt)
                st.markdown(analiz_sonucu)

