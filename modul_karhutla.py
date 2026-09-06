import streamlit as st
import pandas as pd
import numpy as np

@st.cache_data
def get_data_karhutla_nasional():
    # Data sebaran titik panas (hotspot) representatif bersumber dari pemantauan nasional (SiPongi / Satelit NASA)
    data = {
        'Provinsi': [
            'Kalimantan Barat', 'Kalimantan Barat', 'Kalimantan Barat', 
            'Kalimantan Tengah', 'Kalimantan Tengah', 'Kalimantan Tengah',
            'Sumatera Selatan', 'Sumatera Selatan', 'Jambi', 
            'Kalimantan Selatan', 'Papua Selatan', 'Riau', 'Jawa Barat'
        ],
        'Kabupaten': [
            'Kubu Raya', 'Ketapang', 'Melawi', 
            'Palangkaraya', 'Kotawaringin Timur', 'Kapuas',
            'Ogan Komering Ilir', 'Banyuasin', 'Muaro Jambi',
            'Tanah Laut', 'Merauke', 'Bengkalis', 'Sukabumi'
        ],
        'lat': [
            -0.1500, -1.8479, -0.6667, 
            -2.2083, -1.5333, -3.0000,
            -3.3500, -2.8833, -1.5500,
            -3.7900, -8.4900, 1.4820, -7.0219
        ],
        'lon': [
            109.3333, 109.9701, 111.7000, 
            113.9160, 112.9500, 114.3833,
            104.9167, 104.3833, 103.6333,
            115.7600, 140.4000, 102.1388, 106.6713
        ],
        'Tingkat Kepercayaan (%)': [96, 88, 92, 95, 89, 90, 85, 82, 79, 81, 75, 65, 55],
        'Satelit': ['NASA-MODIS', 'NASA-SNPP', 'NASA-NOAA20', 'NASA-MODIS', 'NASA-SNPP', 'NASA-MODIS', 'NASA-SNPP', 'NASA-MODIS', 'NASA-NOAA20', 'NASA-MODIS', 'NASA-SNPP', 'NASA-MODIS', 'NASA-MODIS']
    }
    return pd.DataFrame(data)

def render():
    st.markdown("### 🔥 Peta Sebaran Hotspot Karhutla Nasional")
    st.caption("Pemantauan titik panas (hotspot) di seluruh wilayah Indonesia berdasarkan deteksi anomali suhu satelit.")
    
    df_master = get_data_karhutla_nasional()
    
    # Filter Interaktif Wilayah
    col1, col2 = st.columns(2)
    with col1:
        opsi_prov = ["Semua Provinsi"] + sorted(list(df_master['Provinsi'].unique()))
        pilih_prov = st.selectbox("Filter Provinsi:", opsi_prov)
        
    if pilih_prov != "Semua Provinsi":
        df_master = df_master[df_master['Provinsi'] == pilih_prov]
        
    with col2:
        opsi_kab = ["Semua Kabupaten"] + sorted(list(df_master['Kabupaten'].unique()))
        pilih_kab = st.selectbox("Filter Kabupaten/Kota:", opsi_kab)
        
    if pilih_kab != "Semua Kabupaten":
        df_master = df_master[df_master['Kabupaten'] == pilih_kab]

    # Metrik Ringkasan
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Titik Terpantau", len(df_master))
    m2.metric("Tingkat Kepercayaan Tinggi (>85%)", len(df_master[df_master['Tingkat Kepercayaan (%)'] > 85]))
    m3.metric("Status Operasi", "SIAGA DARURAT" if len(df_master) > 3 else "TERKENDALI")
    
    st.divider()

    # Visualisasi Peta
    if not df_master.empty:
        st.map(df_master, latitude='lat', longitude='lon', color='#ff2200')
        st.markdown("**Rincian Koordinat Titik Panas Terfilter:**")
        st.dataframe(df_master, use_container_width=True, hide_index=True)
    else:
        st.info("Tidak ada titik panas terdeteksi pada filter wilayah tersebut.")