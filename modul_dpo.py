import streamlit as st
import requests
import pandas as pd

# --- ENGINE PENARIK DATA INTERPOL RED NOTICE ---
@st.cache_data(ttl=3600) # Refresh tiap 1 jam
def cari_dpo_interpol(nama_target=""):
    url = "https://ws-public.interpol.int/notices/v1/red"
    
    # Parameter API: Jika tidak ada nama yang dicari, tampilkan buronan asal Indonesia (ID)
    params = {"resultPerPage": 20}
    if nama_target:
        params["name"] = nama_target
    else:
        params["nationality"] = "ID" 
        
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url, params=params, headers=headers, timeout=10)
        
        if res.status_code == 200:
            data = res.json()
            notices = data.get('_embedded', {}).get('notices', [])
            
            if not notices:
                return pd.DataFrame()
                
            hasil_dpo = []
            for n in notices:
                hasil_dpo.append({
                    "Nama Lengkap": f"{n.get('forename', '')} {n.get('name', '')}".strip().upper(),
                    "Tgl Lahir": n.get('date_of_birth', 'Disembunyikan'),
                    "Negara Asal": ", ".join(n.get('nationalities', [])) if n.get('nationalities') else "Unknown",
                    "ID Interpol": n.get('entity_id', '-'),
                    # URL foto thumbnail dari server Interpol
                    "Link Foto": n.get('_links', {}).get('thumbnail', {}).get('href', '')
                })
            return pd.DataFrame(hasil_dpo)
    except Exception as e:
        st.error(f"Satelit INTERPOL gagal merespons: {e}")
        
    return pd.DataFrame()

# --- MERAKIT ANTARMUKA MODUL ---
def render():
    st.markdown("### 🚨 Radar Daftar Pencarian Orang (INTERPOL Red Notice)")
    st.caption("Terhubung langsung dengan basis data buronan internasional. Secara default menampilkan buronan asal Indonesia.")
    
    # 1. Fitur Pencarian Universal API
    col_search, col_btn = st.columns([4, 1])
    with col_search:
        search_query = st.text_input("Cari Buronan Global (Berdasarkan Nama):", placeholder="Contoh: Harun, Escobar, dll...")
    
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True) # Spasi agar tombol sejajar dengan input
        btn_cari = st.button("🔍 Pindai Jaringan")
    
    st.divider()
    
    # 2. Menjalankan Engine & Merender Hasil
    with st.spinner("Mengakses jaringan aman INTERPOL..."):
        # Jika tombol ditekan dan ada isinya, cari nama tersebut. Jika tidak, tampilkan default.
        if btn_cari and search_query:
            df_dpo = cari_dpo_interpol(search_query)
        else:
            df_dpo = cari_dpo_interpol() # Default: Buronan WNI
            
    if not df_dpo.empty:
        st.success(f"✅ Menemukan {len(df_dpo)} profil buronan yang cocok di database INTERPOL.")
        
        # Merender hasil dalam bentuk Grid/Kartu agar foto bisa terlihat
        kolom_grid = st.columns(3)
        for idx, baris in df_dpo.iterrows():
            with kolom_grid[idx % 3]:
                with st.container(border=True):
                    # Menampilkan foto jika tersedia di server Interpol
                    if baris['Link Foto']:
                        st.image(baris['Link Foto'], width=120)
                    else:
                        st.info("🚫 Tanpa Foto")
                        
                    st.markdown(f"**{baris['Nama Lengkap']}**")
                    st.caption(f"ID: {baris['ID Interpol']}")
                    st.write(f"📅 Lahir: {baris['Tgl Lahir']}")
                    st.write(f"🌍 Kewarganegaraan: {baris['Negara Asal']}")
                    
                    # Link menuju halaman detail resmi Interpol
                    link_resmi = f"https://www.interpol.int/en/How-we-work/Notices/View-Red-Notices#/{baris['ID Interpol'].replace('/', '-')}"
                    st.link_button("Lihat Berkas Resmi", link_resmi, use_container_width=True)
    else:
        st.warning("Tidak ditemukan target dengan kriteria tersebut di database INTERPOL.")