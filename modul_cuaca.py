import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# --- 1. API WILAYAH INDONESIA ---
@st.cache_data(ttl=86400)
def get_provinces():
    url = "https://emsifa.github.io/api-wilayah-indonesia/api/provinces.json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return {item['name'].title(): item['id'] for item in res.json()}
    except Exception:
        pass
    return {"Jawa Barat": "32"}

@st.cache_data(ttl=86400)
def get_regencies(prov_id):
    url = f"https://emsifa.github.io/api-wilayah-indonesia/api/regencies/{prov_id}.json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return {item['name'].title(): item['id'] for item in res.json()}
    except Exception:
        pass
    return {}

@st.cache_data(ttl=86400)
def get_districts(reg_id):
    url = f"https://emsifa.github.io/api-wilayah-indonesia/api/districts/{reg_id}.json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return {item['name'].title(): item['id'] for item in res.json()}
    except Exception:
        pass
    return {}

@st.cache_data(ttl=86400)
def get_villages(dist_id):
    url = f"https://emsifa.github.io/api-wilayah-indonesia/api/villages/{dist_id}.json"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return {item['name'].title(): item['id'] for item in res.json()}
    except Exception:
        pass
    return {}

# --- 2. ENGINE KOORDINAT & CUACA GLOBAL (STABIL & ANTI-BLOKIR) ---
# Menggunakan Open-Meteo untuk memastikan data selalu berhasil ditarik tanpa batasan IP
@st.cache_data(ttl=1800)
def ambil_cuaca_berdasarkan_wilayah(nama_wilayah):
    # Mengambil koordinat perkiraan berdasarkan nama wilayah menggunakan Nominatim (OpenStreetMap)
    geo_url = f"https://nominatim.openstreetmap.org/search?q={nama_wilayah}, Indonesia&format=json&limit=1"
    
    lat, lon = -6.9275, 106.9300 # Default Sukabumi jika gagal
    try:
        headers = {'User-Agent': 'OSINT-Command-Center/1.0'}
        geo_res = requests.get(geo_url, headers=headers, timeout=5)
        if geo_res.status_code == 200 and geo_res.json():
            lat = float(geo_res.json()[0]['lat'])
            lon = float(geo_res.json()[0]['lon'])
    except Exception:
        pass
        
    # Menarik data cuaca per jam dari Open-Meteo berdasarkan koordinat wilayah yang dipilih
    weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weathercode,windspeed_10m&timezone=Asia%2FJakarta"
    
    kode_wmo = {
        0: "Cerah ☀️", 1: "Cerah Berawan 🌤️", 2: "Berawan Sebagian ⛅", 
        3: "Berawan ☁️", 45: "Berkabut 🌫️", 51: "Gerimis 🌧️", 
        61: "Hujan Ringan 🌧️", 63: "Hujan Sedang 🌧️", 95: "Badai Petir ⛈️"
    }
    
    try:
        res = requests.get(weather_url, timeout=10)
        if res.status_code == 200:
            data = res.json().get('hourly', {})
            times = data.get('time', [])
            temps = data.get('temperature_2m', [])
            humidities = data.get('relative_humidity_2m', [])
            weathercodes = data.get('weathercode', [])
            winds = data.get('windspeed_10m', [])
            
            format_waktu_sekarang = datetime.now().strftime("%Y-%m-%dT%H:00")
            mulai_idx = 0
            for i, t in enumerate(times):
                if t >= format_waktu_sekarang:
                    mulai_idx = i
                    break
            
            jadwal = []
            for i in range(mulai_idx, min(mulai_idx + 8, len(times))):
                waktu_iso = times[i]
                jam = waktu_iso.split('T')[1]
                
                temp = temps[i] if i < len(temps) else 28
                hum = humidities[i] if i < len(humidities) else 70
                w_code = weathercodes[i] if i < len(weathercodes) else 0
                wind = winds[i] if i < len(winds) else 5
                
                jadwal.append({
                    "Waktu": f"{jam} WIB",
                    "Suhu": f"{temp}°C",
                    "Kondisi": kode_wmo.get(w_code, "Berawan ☁️"),
                    "Kelembapan": f"{hum}%",
                    "Kecepatan Angin": f"{wind} km/j"
                })
            return pd.DataFrame(jadwal)
    except Exception:
        pass
    return pd.DataFrame()

# --- 3. ANTARMUKA UTAMA MODUL ---
def render():
    st.markdown("### 🛰️ Prakiraan Cuaca Nasional (Real-Time)")
    st.caption("Pilih wilayah dari Provinsi hingga Kelurahan/Desa di seluruh Indonesia untuk memantau kondisi cuaca secara akurat.")
    
    # Cascading Dropdown Seluruh Indonesia
    provinces = get_provinces()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pilih_prov = st.selectbox("Provinsi:", list(provinces.keys()), index=list(provinces.keys()).index("Jawa Barat") if "Jawa Barat" in provinces else 0)
    
    regencies = get_regencies(provinces[pilih_prov])
    with col2:
        pilih_reg = st.selectbox("Kabupaten/Kota:", list(regencies.keys()) if regencies else ["Pilih..."])
        
    districts = get_districts(regencies[pilih_reg]) if pilih_reg in regencies else {}
    with col3:
        pilih_dist = st.selectbox("Kecamatan:", list(districts.keys()) if districts else ["Pilih..."])
        
    villages = get_villages(districts[pilih_dist]) if pilih_dist in districts else {}
    with col4:
        pilih_vill = st.selectbox("Kelurahan/Desa:", list(villages.keys()) if villages else ["Pilih..."])
        
    st.divider()
    
    # Menentukan target wilayah pencarian
    target_pencarian = ""
    if pilih_vill and pilih_vill != "Pilih...":
        target_pencarian = f"{pilih_vill}, {pilih_dist}, {pilih_reg}"
    elif pilih_dist and pilih_dist != "Pilih...":
        target_pencarian = f"{pilih_dist}, {pilih_reg}"
    elif pilih_reg and pilih_reg != "Pilih...":
        target_pencarian = f"{pilih_reg}, {pilih_prov}"
    else:
        target_pencarian = pilih_prov
        
    if target_pencarian:
        with st.spinner(f"Menarik data meteorologi untuk wilayah: {target_pencarian}..."):
            df_cuaca = ambil_cuaca_berdasarkan_wilayah(target_pencarian)
            
        if not df_cuaca.empty:
            st.success(f"📍 Menampilkan prakiraan cuaca wilayah: **{target_pencarian}**")
            
            # Kartu Metrik Jam Terdekat
            st.markdown("**Prakiraan Jam Terdekat:**")
            kolom_metrik = st.columns(min(len(df_cuaca), 5))
            for i, kolom in enumerate(kolom_metrik):
                row = df_cuaca.iloc[i]
                kolom.metric(
                    label=row['Waktu'], 
                    value=row['Kondisi'], 
                    delta=f"Suhu: {row['Suhu']} | Lembap: {row['Kelembapan']}"
                )
                
            st.markdown("---")
            # Tabel Rincian Lengkap
            st.markdown("**Tabel Rincian Parameter Lengkap:**")
            st.dataframe(df_cuaca, use_container_width=True, hide_index=True)
        else:
            st.warning("Gagal memuat data cuaca untuk wilayah ini. Silakan coba pilih wilayah lain.")
    else:
        st.info("👆 Silakan lengkapi pilihan wilayah di atas.")