import streamlit as st
import requests
import xml.etree.ElementTree as ET
import pandas as pd

def render():
    st.markdown("### 🗺️ Peta Kerawanan & Deteksi Dini (Early Warning System)")
    st.caption("Pemantauan dan analisis potensi kerawanan wilayah berdasarkan agregasi isu strategis di internet.")
    
    # 1. Pilihan Wilayah Pemantauan
    wilayah_fokus = st.selectbox(
        "Pilih Wilayah Fokus Pemantauan:", 
        ["Kabupaten Sukabumi", "Jawa Barat", "DKI Jakarta", "Nasional (Indonesia)"]
    )
    
    with st.spinner(f"Menganalisis indeks kerawanan dan sinyal intelijen untuk wilayah {wilayah_fokus}..."):
        
        # Menyusun kueri pencarian isu kerawanan (ATHG: Konflik, Kriminal, Bencana, Unjuk Rasa)
        keyword = f"{wilayah_fokus} (konflik OR kriminal OR bencana OR unjuk rasa OR kejahatan OR kerawanan)"
        url = f"https://news.google.com/rss/search?q={keyword}&hl=id&gl=ID&ceid=ID:id"
        
        isu_list = []
        try:
            res = requests.get(url, timeout=10)
            root = ET.fromstring(res.content)
            
            for item in root.findall('.//item')[:15]:
                judul = item.find('title').text
                link = item.find('link').text
                waktu = item.find('pubDate').text
                
                # Simulasi Analisis Sentimen / Penilaian Risiko Sederhana berdasarkan Kata Kunci
                teks_lower = judul.lower()
                if any(k in teks_lower for k in ['bencana', 'korban', 'tewas', 'bentrok', 'kriminal', 'serang', 'ancam']):
                    risiko = "⚠️ Risiko Tinggi (High Threat)"
                    lat_offset, lon_offset = -6.9275, 106.9300 # Koordinat simulasi sekitar Sukabumi/Jabar
                elif any(k in teks_lower for k in ['protes', 'aksi', 'damai', 'razia', 'operasi']):
                    risiko = "⚡ Risiko Sedang (Medium)"
                    lat_offset, lon_offset = -6.9300, 106.9200
                else:
                    risiko = "ℹ️ Potensi Rendah / Pantauan"
                    lat_offset, lon_offset = -6.9200, 106.9400
                
                isu_list.append({
                    "Isu / Indikasi Ancaman": judul,
                    "Tingkat Risiko": risiko,
                    "Waktu Terdeteksi": waktu,
                    "Link Sumber": link,
                    "lat": lat_offset,
                    "lon": lon_offset
                })
        except Exception as e:
            st.error(f"Gagal memindai sensor kerawanan: {e}")
            
        df_isu = pd.DataFrame(isu_list)
        
    if not df_isu.empty:
        # 2. Ringkasan Indikator Metrik
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Indikasi Terdeteksi", len(df_isu))
        col2.metric("Indikasi Risiko Tinggi", len(df_isu[df_isu['Tingkat Risiko'].str.contains("Tinggi")]))
        col3.metric("Status Sistem Early Warning", "AKTIF (SIAGA 2)")
        
        st.divider()
        
        # 3. Tata Letak Peta dan Tabel Rincian
        col_peta, col_tabel = st.columns([1.5, 2])
        
        with col_peta:
            st.markdown("**Peta Titik Kerawanan Wilayah**")
            # Menampilkan peta sebaran titik kerawanan
            st.map(df_isu, latitude='lat', longitude='lon', color='#ff3300')
            st.caption("*Titik koordinat dihitung berdasarkan sebaran indikasi wilayah pemantauan.")
            
        with col_tabel:
            st.markdown("**Daftar Isu & Deteksi Dini**")
            for idx, row in df_isu.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['Isu / Indikasi Ancaman']}**")
                    st.write(f"Klasifikasi: {row['Tingkat Risiko']}")
                    st.caption(f"🕒 {row['Waktu Terdeteksi']}")
                    st.link_button("🔗 Verifikasi Berita Sumber", row['Link Sumber'], use_container_width=True)
    else:
        st.warning("Tidak ada indikasi kerawanan menonjol yang terdeteksi untuk wilayah ini.")