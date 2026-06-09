import streamlit as st
import requests

# --- 1. SAYFA AYARLARI VE CSS ---
st.set_page_config(page_title="Hafıza Kampüsü", layout="wide")

st.markdown("""
    <style>
    /* Mevcut Stiller */
    .saray-baslik { color: #00E5FF; font-weight: 800; font-size: 26px; border-bottom: 2px solid #00E5FF; padding-bottom:10px;}
    .durak-baslik { color: #FFD700; font-weight: bold; font-size: 18px; margin-top:10px;}
    .anahtar-kelime { color: #FF9100; font-weight: bold; background-color: #1e1e1e; padding: 5px 12px; border-radius: 6px; border: 1px solid #FF9100;}
    .senaryo-metni { font-size: 16px; line-height: 1.6; color: #E0E0E0;}

    /* --- YENİ VIP ASANSÖR EKLENTİSİ --- */
    [data-testid="stSidebar"] {
        background-color: #111111;
        border-right: 2px solid #00fff2;
        color: #e0e0e0;
    }
    .asansor-baslik {
        font-family: 'Space Mono', monospace;
        font-size: 28px;
        font-weight: bold;
        color: #00fff2;
        text-align: center;
        padding: 10px;
        border-bottom: 2px solid #00fff2;
        margin-bottom: 10px;
        text-shadow: 0 0 10px #00fff2;
    }
    .asansor-alt-baslik {
        font-family: 'Space Mono', monospace;
        font-size: 14px;
        color: #aaaaaa;
        text-align: center;
        margin-bottom: 30px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] {
        gap: 15px;
        padding-left: 10px;
        padding-right: 10px;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        font-family: 'Roboto Mono', monospace;
        background-color: #222222;
        color: #e0e0e0;
        border: 1px solid #333333;
        border-radius: 10px;
        padding: 12px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    /* TİTREMEYİ ÖNLEYEN YENİ HOVER KISMI (Sağa kayma silindi) */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        border-color: #00fff2;
        box-shadow: 0 0 15px rgba(0, 255, 242, 0.6);
        background-color: #1a1a1a;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label[data-selected="true"] {
        background-color: #00fff2 !important;
        color: #111111 !important;
        border-color: #00fff2 !important;
        font-weight: bold !important;
        box-shadow: 0 0 20px rgba(0, 255, 242, 1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. API İLE SUPABASE BAĞLANTISI ---
@st.cache_data
def get_supabase_data():
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]
    
    endpoint = f"{supabase_url}/rest/v1/hafiza_sarayi"
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }
    
    # Sıralama koduna bina_adi da eklendi
    params = {
        "select": "*",
        "order": "bina_adi.asc,kat_adi.asc,durak_no.asc"
    }
    
    try:
        response = requests.get(endpoint, headers=headers, params=params)
        response.raise_for_status() 
        return response.json()
    except Exception as e:
        st.error(f"Veri çekilemedi: {e}")
        return []

# --- 3. ANA EKRAN TASARIMI VE ASANSÖR ---
st.title("🏛️ Dijital Hafıza Kampüsü")
st.markdown("*SMMM Sınavı Çoktan Seçmeli Soruları İçin Zihinsel Görsel Taktikler*")
st.divider()

veriler = get_supabase_data()

if veriler:
    # --- YENİ: KAMPÜS BİNA SEÇİMİ ---
    binalar = []
    for v in veriler:
        b = v.get("bina_adi")
        if not b:
            b = "Vergi Hukuku"
        if b not in binalar:
            binalar.append(b)
            
    st.sidebar.markdown('<p class="asansor-baslik">🧭 KAMPÜS</p>', unsafe_allow_html=True)
    st.sidebar.markdown('<p class="asansor-alt-baslik">Hangi binaya girmek istersiniz?</p>', unsafe_allow_html=True)
    
    secilen_bina = st.sidebar.selectbox("Bina Seçin:", binalar, label_visibility="collapsed")
    st.sidebar.divider()

    # O binaya ait verileri filtrele
    bina_verileri = [v for v in veriler if v.get("bina_adi", "Vergi Hukuku") == secilen_bina]

    # --- SENİN ORİJİNAL ASANSÖRÜN BURADAN İTİBAREN BAŞLIYOR ---
    st.sidebar.markdown('<p class="asansor-baslik">🛗 ASANSÖR</p>', unsafe_allow_html=True)
    st.sidebar.markdown('<p class="asansor-alt-baslik">Sarayın hangi katına çıkmak istersiniz?</p>', unsafe_allow_html=True)

    kat_listesi = []
    for v in bina_verileri:
        if v["kat_adi"] not in kat_listesi:
            kat_listesi.append(v["kat_adi"])

    # --- ASANSÖRÜ DOĞRU SIRALAMA MANTIĞI (TÜM BİNALAR İÇİN) ---
    def kat_sirasi(kat_adi):
        # Eğer kat isminde "Zemin" geçiyorsa en başa (0. sıraya) sabitle
        if "Zemin" in kat_adi:
            return 0
        try:
            # "10. Kat: Finansman" veya "1. Kat: GVK" metninden sadece baştaki rakamı çek
            return int(kat_adi.split('.')[0])
        except:
            # Eğer rakam bulamazsa en sona at
            return 99

    # Listeyi yukarıdaki zeki kurala göre sırala
    kat_listesi = sorted(kat_listesi, key=kat_sirasi)
    # ----------------------------------------------------------

    if kat_listesi:
        # Kat listesine ikonlar ekleyerek asansörü görselleştiriyoruz
        kat_icons = {
            "Zemin Kat: VUK Lobisi": "🏛️",
            "1. Kat: GVK Çarşısı": "🛍️",
            "2. Kat: KVK Gökdeleni": "🏢",
            "3. Kat: KDV Fabrikası": "🏭",
            "4. Kat: ÖTV VIP Garajı": "🏎️",
            "5. Kat: Tahsilat Zindanı": "⛓️",
            "6. Kat: Yargı Salonu": "⚖️",
            "7. Kat: Gizli Kasa Odası": "🔐",
            "1. Kat: Likidite Bölümü": "🔬",
            "2. Kat: Asit-Test Bölümü": "🧪",
            "3. Kat: Nakit Oran Bölümü": "💰",
            "4. Kat: Stok Bağımlılık Bölümü": "📦",
            "5. Kat: Stok Devir Bölümü": "⚙️",
            "6. Kat: Alacak Tahsil Bölümü": "🧲",
            "7. Kat: Aktif Devir Bölümü": "🌋",
            "8. Kat: Özkaynak Devir Bölümü": "👑",
            "9. Kat: Kaldıraç Bölümü": "⚖️",
            "10. Kat: Finansman Bölümü": "🛡️",
            "11. Kat: Faiz Karşılama Bölümü": "🧯",
            "12. Kat: Aktif Kârlılık Bölümü": "💎",
            "13. Kat: Özkaynak Kârlılık Bölümü": "💍",
            "14. Kat: Net Kâr Marjı Bölümü": "💧"
        }
        
        styled_kat_listesi = []
        for kat in kat_listesi:
            icon = kat_icons.get(kat, "📌")
            styled_kat_listesi.append(f"{icon} {kat}")

        # VIP Asansör Radyo Butonları
        secilen_styled_kat = st.sidebar.radio("Kat Seçimi:", styled_kat_listesi, key="ana_asansor_styled", label_visibility="collapsed")
        
        # Seçili olan ikonlu ismi, veritabanındaki orijinal haline geri çeviriyoruz
        secilen_kat = secilen_styled_kat.split(" ", 1)[1] if " " in secilen_styled_kat else secilen_styled_kat
        
        filtrelenmis_veriler = [v for v in bina_verileri if v["kat_adi"] == secilen_kat]

        col1, col2 = st.columns(2, gap="large")

        with col2:
            st.markdown("### 🧠 Zihinsel Duraklar", unsafe_allow_html=True)
            durak_isimleri = [f"Durak {d['durak_no']}: {d['baslik']}" for d in filtrelenmis_veriler]
            
            # İç menü için benzersiz anahtar ekliyoruz
            secilen_durak_ismi = st.radio("İncelemek istediğiniz durağı seçin:", durak_isimleri, key=f"durak_secim_{secilen_kat}")
            
            secilen_durak_data = next(d for d in filtrelenmis_veriler if f"Durak {d['durak_no']}: {d['baslik']}" == secilen_durak_ismi)
            
            st.markdown(f'<br><span class="anahtar-kelime">Şifre: {secilen_durak_data["anahtar_kelime"]}</span>', unsafe_allow_html=True)
            st.markdown(f'<p class="senaryo-metni"><br>{secilen_durak_data["senaryo"]}</p>', unsafe_allow_html=True)

        with col1:
            st.markdown(f'<p class="saray-baslik">{secilen_kat}</p>', unsafe_allow_html=True)
            # KATIN ana resmini gösteriyoruz
            if filtrelenmis_veriler and filtrelenmis_veriler[0].get("gorsel_url"):
                st.image(filtrelenmis_veriler[0]["gorsel_url"], use_container_width=True)
            else:
                st.info("Bu durak için görsel henüz eklenmedi.")
    else:
        st.warning("Bu binada henüz hiçbir kat inşa edilmedi.")
else:
    st.warning("Henüz sarayda hiçbir kat inşa edilmedi.")
    st.write("") # Sayfa sonuna boş bir satır ekler
# veya
st.markdown("<br><br>", unsafe_allow_html=True)