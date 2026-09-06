import streamlit as st
import pandas as pd
import requests
import pydeck as pdk

@st.cache_data(ttl=600)
def ambil_data_gempa_bmkg(tipe="terkini"):
    if tipe == "dirasakan":
        url = "https://data.bmkg.go.id/DataMKG/TEWS/gempadirasakan.json"
    else:
        url = "https://data.bmkg.go.id/DataMKG/TEWS/gempaterkini.json"
        
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            gempa_list = data.get('Infogempa', {}).get('gempa', [])
            hasil = []
            for g in gempa_list:
                coords = g.get('Coordinates', '0/0')
                if '/' in coords:
                    lat_str, lon_str = coords.split('/')
                else:
                    lat_str, lon_str = "0", "0"
                    
                try:
                    lat = float(lat_str.replace(' LS', '').replace(' LU', ''))
                    if 'LS' in lat_str: lat = -lat
                    lon = float(lon_str.replace(' BT', '').replace(' BB', ''))
                    if 'BB' in lon_str: lon = -lon
                except Exception:
                    lat, lon = 0.0, 0.0
                
                # Menyesuaikan nama kolom menjadi latitude & longitude agar terbaca oleh pemeta
                hasil.append({
                    "Tanggal": g.get('Tanggal'),
                    "Jam": g.get('Jam'),
                    "Wilayah": g.get('Wilayah'),
                    "Magnitudo": float(g.get('Magnitude', 0)),
                    "Kedalaman": g.get('Kedalaman'),
                    "Dirasakan": g.get('Dirasakan', '-'),
                    "Potensi": g.get('Potensi', '-'),
                    "latitude": lat,
                    "longitude": lon
                })
            return pd.DataFrame(hasil)
    except Exception:
        pass
    return pd.DataFrame()

def render():
    st.markdown("### ⚠️ Pusat Pemantauan Bencana & Mitigasi Darurat (Real-Time)")
    st.caption("Modul terintegrasi untuk memantau sebaran gempa bumi, status gunung api, dan kebencanaan nasional secara langsung.")
    
    tab_gempa, tab_gunung, tab_karhutla, tab_longsor, tab_banjir, tab_ekstrem = st.tabs([
        "🌍 Gempa Bumi (Live BMKG)", 
        "🌋 Gunung Meletus",
        "🔥 Karhutla", 
        "⛰️ Tanah Longsor", 
        "🌊 Banjir & Genangan", 
        "🌪️ Cuaca Ekstrem"
    ])
    
    # --- TAB 1: GEMPA BUMI REAL-TIME (DENGAN PYDECK & TITIK DIAMETER BESAR) ---
    with tab_gempa:
        st.markdown("#### 🌍 Aktivitas Gempabumi Terkini (Live Server BMKG)")
        
        kategori_gempa = st.radio(
            "Pilih Kategori Pemantauan Gempa:", 
            ["Gempa Terkini (Magnitudo 5.0+)", "Gempa Dirasakan Masyarakat"], 
            horizontal=True
        )
        
        st.divider()
        
        tipe_fetch = "terkini" if "Terkini" in kategori_gempa else "dirasakan"
        with st.spinner("Menarik data live dari server BMKG..."):
            df_gempa = ambil_data_gempa_bmkg(tipe_fetch)
            
        if not df_gempa.empty:
            st.success(f"✅ Berhasil menyinkronkan {len(df_gempa)} data gempabumi.")
            
            # Pengaturan Peta PyDeck dengan Titik Diameter Lebih Besar (ScatterplotLayer)
            layer = pdk.Layer(
                "ScatterplotLayer",
                data=df_gempa,
                get_position='[longitude, latitude]',
                get_radius=40000,  # Memperbesar diameter titik penanda (dalam meter)
                get_fill_color=[255, 69, 0, 180],  # Warna Oranye Kemerahan Transparan
                pickable=True,
                auto_highlight=True,
            )
            
            # Menentukan titik tengah peta (center) berdasarkan rata-rata koordinat data
            view_state = pdk.ViewState(
                latitude=float(df_gempa['latitude'].mean()),
                longitude=float(df_gempa['longitude'].mean()),
                zoom=4.5,
                pitch=0,
            )
            
            r = pdk.Deck(
                layers=[layer], 
                initial_view_state=view_state,
                tooltip={"text": "Wilayah: {Wilayah}\nMagnitudo: {Magnitudo}\nKedalaman: {Kedalaman}"}
            )
            
            st.pydeck_chart(r, use_container_width=True)
            
            # Menampilkan tabel data di bawah peta
            if tipe_fetch == "terkini":
                st.dataframe(df_gempa[['Tanggal', 'Jam', 'Wilayah', 'Magnitudo', 'Kedalaman', 'Potensi']], use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_gempa[['Tanggal', 'Jam', 'Wilayah', 'Magnitudo', 'Kedalaman', 'Dirasakan']], use_container_width=True, hide_index=True)
        else:
            st.warning("Gagal memuat data live gempabumi dari BMKG.")
            
    # --- TAB 2: GUNUNG MELETUS ---
    with tab_gunung:
        st.markdown("#### 🌋 Pantauan Status Aktivitas Gunung Berapi Nasional")
        df_gunung = pd.DataFrame({
            'Nama Gunung': ['Gunung Marapi', 'Gunung Ibu', 'Gunung Semeru', 'Gunung Lewotobi Laki-laki', 'Gunung Merapi (Jawa)', 'Gunung Anak Krakatau'],
            'Wilayah': ['Sumatera Barat', 'Halmahera Barat, Maluku Utara', 'Jawa Timur', 'Flores Timur, NTT', 'Jawa Tengah / DI Yogyakarta', 'Selat Sunda, Lampung'],
            'Status Level': ['Level III (Siaga)', 'Level III (Siaga)', 'Level III (Siaga)', 'Level III (Siaga)', 'Level II (Waspada)', 'Level II (Waspada)'],
            'latitude': [-0.38, 1.48, -8.10, -8.54, -7.54, -6.10],
            'longitude': [100.47, 127.63, 112.92, 122.78, 110.44, 105.42]
        })
        st.map(df_gunung, latitude='latitude', longitude='longitude', size=40, color='#8B0000')
        st.dataframe(df_gunung[['Nama Gunung', 'Wilayah', 'Status Level']], use_container_width=True, hide_index=True)
        
    # --- TAB 3: KARHUTLA ---
    with tab_karhutla:
        st.markdown("#### 🔥 Monitoring Hotspot & Karhutla Nasional")
        df_karhutla = pd.DataFrame({
            'Provinsi': ['Kalimantan Barat', 'Kalimantan Tengah', 'Sumatera Selatan'],
            'Kabupaten': ['Kubu Raya', 'Palangkaraya', 'Ogan Komering Ilir'],
            'latitude': [-0.1500, -2.2083, -3.3500],
            'longitude': [109.3333, 113.9160, 104.9167],
            'Tingkat Kepercayaan': ['96% (Tinggi)', '95% (Tinggi)', '85% (Sedang)'],
            'Satelit': ['NASA-MODIS', 'NASA-SNPP', 'NASA-NOAA20']
        })
        st.map(df_karhutla, latitude='latitude', longitude='longitude', size=40, color='#ff2200')
        st.dataframe(df_karhutla, use_container_width=True, hide_index=True)
        
    # --- TAB 4: TANAH LONGSOR ---
    with tab_longsor:
        st.markdown("#### ⛰️ Laporan Titik Rawan & Kejadian Longsor")
        df_longsor = pd.DataFrame({
            'Wilayah / Ruas Jalan': ['Jl. Raya Cikidang - Sukabumi', 'Kecamatan Cicurug, Sukabumi'],
            'Status Jalur': ['Tutup Sebagian', 'Buka Tutup'],
            'Tingkat Risiko': ['Tinggi (Rawan Susulan)', 'Sedang'],
            'latitude': [-6.9200, -6.8300],
            'longitude': [106.7500, 106.7800]
        })
        st.map(df_longsor, latitude='latitude', longitude='longitude', size=40, color='#8b4513')
        st.dataframe(df_longsor, use_container_width=True, hide_index=True)
        
    # --- TAB 5: BANJIR ---
    with tab_banjir:
        st.markdown("#### 🌊 Pantauan Genangan & Banjir Wilayah")
        df_banjir = pd.DataFrame({
            'Kawasan Terdampak': ['Kecamatan Pelabuhanratu (Pesisir)', 'Banjir Rob Sukabumi Selatan'],
            'Ketinggian Air': ['30 - 50 cm', '20 - 40 cm'],
            'Status Evakuasi': ['Terkendali / Waspada', 'Aman'],
            'latitude': [-6.9900, -7.0100],
            'longitude': [106.5500, 106.5800]
        })
        st.map(df_banjir, latitude='latitude', longitude='longitude', size=40, color='#0000ff')
        st.dataframe(df_banjir, use_container_width=True, hide_index=True)
        
    # --- TAB 6: CUACA EKSTREM ---
    with tab_ekstrem:
        st.markdown("#### 🌪️ Peringatan Dini Cuaca Ekstrem")
        df_ekstrem = pd.DataFrame({
            'Wilayah': ['Sukabumi Bagian Utara', 'Bogor & Cianjur'],
            'Jenis Fenomena': ['Puting Beliung / Angin Kencang', 'Hujan Lebat Disertai Petir'],
            'Estimasi Waktu': ['Sore - Malam Hari', 'Siang - Sore Hari']
        })
        st.dataframe(df_ekstrem, use_container_width=True, hide_index=True)