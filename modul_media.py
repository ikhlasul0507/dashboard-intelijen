import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime, timedelta

# --- 1. ENGINE PENARIK DATA WILAYAH INDONESIA ---

@st.cache_data(ttl=86400) # Cache disimpan selama 1 hari agar sangat cepat
def get_provinsi():
    # Mengambil master data 38 Provinsi di Indonesia
    url = "https://emsifa.github.io/api-wilayah-indonesia/api/provinces.json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            data = sorted(res.json(), key=lambda x: x['name'])
            # Mengembalikan dictionary { 'Jawa Barat': '32', 'DKI Jakarta': '31' }
            return {item['name'].title(): item['id'] for item in data}
    except Exception:
        pass
    # Fallback minimal jika koneksi terputus
    return {"Jawa Barat": "32", "DKI Jakarta": "31", "Banten": "36", "Jawa Tengah": "33"}

@st.cache_data(ttl=86400)
def get_kabupaten(prov_id):
    if not prov_id: return []
    # Mengambil data Kabupaten berdasarkan ID Provinsi yang dipilih
    url = f"https://emsifa.github.io/api-wilayah-indonesia/api/regencies/{prov_id}.json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            kab_list = []
            for item in res.json():
                # Membuang atribut awalan agar pencarian berita (Google News) lebih akurat
                nama = item['name'].replace("KABUPATEN ", "").replace("KOTA ", "").title()
                kab_list.append(nama)
            return sorted(kab_list)
    except Exception:
        pass
    return ["Sukabumi", "Bandung", "Bogor"] # Fallback

# --- 2. ANTARMUKA DAN LOGIKA PENCARIAN ---

def render():
    st.markdown("### 🗣️ Social & Media Listening")
    st.caption("Lacak perbincangan spesifik berdasarkan kata kunci, 38 Provinsi, 514 Kabupaten/Kota, dan rentang waktu.")
    
    # Menarik referensi wilayah
    dict_provinsi = get_provinsi()
    list_nama_provinsi = ["Semua Provinsi"] + list(dict_provinsi.keys())
    
    # Merakit Filter UI
    col1, col2, col3 = st.columns(3)
    
    with col1:
        keyword = st.text_input("Kata Kunci Topik:", "Pilkada")
        
    with col2:
        # Mengatur default pilihan langsung ke Jawa Barat agar mempercepat kerja Anda
        default_prov_idx = list_nama_provinsi.index("Jawa Barat") if "Jawa Barat" in list_nama_provinsi else 0
        pilih_provinsi = st.selectbox("Wilayah Provinsi:", list_nama_provinsi, index=default_prov_idx)
        
    with col3:
        if pilih_provinsi == "Semua Provinsi":
            opsi_kab = ["Semua Kabupaten"]
        else:
            # Secara dinamis memanggil kabupaten berdasarkan provinsi
            prov_id = dict_provinsi[pilih_provinsi]
            opsi_kab = ["Semua Kabupaten"] + get_kabupaten(prov_id)
            
        # Mengatur default pilihan ke Sukabumi
        default_kab_idx = opsi_kab.index("Sukabumi") if "Sukabumi" in opsi_kab else 0
        pilih_kabupaten = st.selectbox("Kabupaten/Kota:", opsi_kab, index=default_kab_idx)

    hari_ini = datetime.now().date()
    tujuh_hari_lalu = hari_ini - timedelta(days=7)
    rentang_tanggal = st.date_input("Rentang Tanggal Publikasi:", [tujuh_hari_lalu, hari_ini])
    
    st.divider()

    # Eksekusi Radar Berita
    if st.button("🚀 Pindai Radar Berita"):
        with st.spinner("Menyisir database media nasional berdasarkan wilayah..."):
            
            # Merakit kueri berdasarkan filter
            q_parts = []
            if keyword: q_parts.append(keyword)
            if pilih_provinsi != "Semua Provinsi": q_parts.append(pilih_provinsi)
            if pilih_kabupaten != "Semua Kabupaten": q_parts.append(pilih_kabupaten)
            
            query_str = " ".join(q_parts)
            
            if len(rentang_tanggal) == 2:
                tanggal_mulai = rentang_tanggal[0].strftime("%Y-%m-%d")
                tanggal_akhir = rentang_tanggal[1].strftime("%Y-%m-%d")
                query_str += f" after:{tanggal_mulai} before:{tanggal_akhir}"
            
            url = f"https://news.google.com/rss/search?q={query_str}&hl=id&gl=ID&ceid=ID:id"
            
            try:
                res = requests.get(url, timeout=10)
                root = ET.fromstring(res.content)
                
                hasil = []
                for item in root.findall('.//item')[:20]:
                    hasil.append({
                        "Waktu": item.find('pubDate').text,
                        "Judul": item.find('title').text,
                        "Sumber": item.find('source').text if item.find('source') is not None else "Tidak Diketahui",
                        "Link": item.find('link').text
                    })
                
                # Merender UI Kartu
                if hasil:
                    st.success(f"✅ Radar menangkap {len(hasil)} publikasi terkait '{query_str}'.")
                    
                    kolom_hasil = st.columns(2)
                    for idx, h in enumerate(hasil):
                        with kolom_hasil[idx % 2]:
                            with st.container(border=True):
                                st.markdown(f"**{h['Judul']}**")
                                st.caption(f"📰 {h['Sumber']} | 🕒 {h['Waktu']}")
                                st.link_button("🔗 Buka Artikel Asli", h['Link'], use_container_width=True)
                else:
                    st.info(f"Berdasarkan wilayah dan tanggal tersebut, tidak ada perbincangan signifikan terkait '{keyword}'.")
                    
            except Exception as e:
                st.error(f"🚨 Gagal menyadap agregator berita. Detail: {e}")