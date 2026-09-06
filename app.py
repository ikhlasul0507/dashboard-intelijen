import streamlit as st
import time

# --- MENGIMPOR MODUL (Karhutla diganti Bencana) ---
import modul_market
import modul_berita
import modul_cuaca
import modul_bencana # Modul Bencana Terpadu Baru
import modul_transportasi
import modul_cyber
import modul_media
import modul_threat
import modul_arsip
import modul_kalender_tim
import modul_dpo
import modul_kerawanan
import modul_storage
import modul_domain
import modul_http
import modul_crypto

st.set_page_config(page_title="Intel Command Center", layout="wide", page_icon="📡")
st.title("📡 OSINT Command Center")
st.caption(f"Sistem Aktif. Sinkronisasi Terakhir: {time.strftime('%Y-%m-%d %H:%M:%S')} WIB")

# --- MEMBUAT MENU TABS (Tab 4 diubah ke Bencana) ---
t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11, t12, t13, t14, t15, t16 = st.tabs([
    "📊 Market", "📰 Berita", "🌤️ Cuaca", "⚠️ Bencana", "✈️ Transportasi",
    "🌐 Siber", "🗣️ Media", "🕵️ Ancaman", "🗄️ Arsip DB", "🗓️ Kalender", 
    "🚨 DPO", "🗺️ Kerawanan", "☁️ Storage", "🌐 Domain", "🔍 HTTP", "🔐 Crypto"
])

# --- MENYALURKAN MODUL KE TABS ---
with t1: modul_market.render()
with t2: modul_berita.render()
with t3: modul_cuaca.render()
with t4: modul_bencana.render() # Menyalurkan Modul Bencana
with t5: modul_transportasi.render()
with t6: modul_cyber.render()
with t7: modul_media.render()
with t8: modul_threat.render()
with t9: modul_arsip.render()
with t10: modul_kalender_tim.render()
with t11: modul_dpo.render()
with t12: modul_kerawanan.render()
with t13: modul_storage.render()
with t14: modul_domain.render()
with t15: modul_http.render()
with t16: modul_crypto.render()

# --- SIDEBAR KONTROL ---
with st.sidebar:
    st.title("🎛️ Panel Kontrol Utama")
    st.markdown("Status Server: **ONLINE** 🟢")
    if st.button("🔄 Paksa Sinkronisasi Jaringan"):
        st.cache_data.clear()
        st.rerun()