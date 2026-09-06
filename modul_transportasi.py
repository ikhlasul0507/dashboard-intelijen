import streamlit as st
import pandas as pd
import requests
import pydeck as pdk
import streamlit.components.v1 as components

# --- FUNGSI RADAR UDARA ---
@st.cache_data(ttl=60)
def ambil_data_radar_udara():
    url = "https://opensky-network.org/api/states/all?lamin=-11.0&lomin=94.0&lamax=6.0&lomax=141.0"
    try:
        headers = {'User-Agent': 'OSINT-Command-Center/1.0'}
        res = requests.get(url, headers=headers, timeout=10)
        
        if res.status_code == 200:
            penerbangan = res.json().get('states', [])
            hasil = []
            if penerbangan:
                for p in penerbangan:
                    if p[5] is not None and p[6] is not None:
                        hasil.append({
                            "Callsign (No. Penerbangan)": str(p[1]).strip() if p[1] else "TIDAK DIKETAHUI",
                            "Negara Asal": p[2],
                            "longitude": p[5],
                            "latitude": p[6],
                            "Ketinggian (meter)": p[7] if p[7] else 0,
                            "Kecepatan (m/s)": p[9] if p[9] else 0,
                            "Status": "Di Darat" if p[8] else "Mengudara"
                        })
                return pd.DataFrame(hasil)
    except Exception:
        pass
    return pd.DataFrame()

# --- FUNGSI PEMUTAR VIDEO HLS (CCTV) ---
def render_cctv_player(url_m3u8, nama_lokasi, tinggi=250):
    """Membuat elemen iframe HTML dengan pustaka hls.js untuk merender siaran CCTV secara langsung"""
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <style>
            body {{ margin: 0; background-color: #1e1e1e; color: #00ff00; font-family: monospace; text-align: center; overflow: hidden; border-radius: 8px; }}
            video {{ width: 100%; height: {tinggi - 35}px; object-fit: cover; background: #000; }}
            .overlay-title {{ position: absolute; top: 0; left: 0; width: 100%; background: rgba(0, 0, 0, 0.7); padding: 5px 0; font-size: 13px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px; z-index: 10; border-bottom: 1px solid #333; }}
            .rec {{ color: red; animation: blink 1s infinite; }}
            @keyframes blink {{ 50% {{ opacity: 0; }} }}
        </style>
    </head>
    <body>
        <div class="overlay-title"><span class="rec">● REC</span> {nama_lokasi}</div>
        <video id="cctv-video" controls autoplay muted playsinline></video>
        <script>
            var video = document.getElementById('cctv-video');
            var videoSrc = '{url_m3u8}';
            if (Hls.isSupported()) {{
                var hls = new Hls();
                hls.loadSource(videoSrc);
                hls.attachMedia(video);
                hls.on(Hls.Events.MANIFEST_PARSED, function() {{ video.play(); }});
            }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
                video.src = videoSrc;
                video.addEventListener('loadedmetadata', function() {{ video.play(); }});
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=tinggi)

def render():
    st.markdown("### ✈️ Pusat Pemantauan Lalu Lintas Transportasi")
    st.caption("Monitoring pergerakan armada udara dan siaran CCTV lalu lintas darat secara real-time dan terintegrasi.")
    
    tab_udara, tab_darat, tab_laut = st.tabs([
        "✈️ Radar Udara (Live ADS-B)", 
        "🚗 Pantauan Darat & CCTV Tol",
        "🚢 Radar Laut (AIS)"
    ])
    
    # --- TAB 1: RADAR UDARA ---
    with tab_udara:
        st.markdown("#### 📡 Live Flight Radar (Wilayah Udara Indonesia)")
        with st.spinner("Menyapu langit digital Indonesia mencari sinyal pesawat..."):
            df_pesawat = ambil_data_radar_udara()
            
        if not df_pesawat.empty:
            st.success(f"✅ Radar mendeteksi {len(df_pesawat)} pesawat yang sedang beroperasi di ruang udara Indonesia saat ini.")
            
            layer_pesawat = pdk.Layer(
                "ScatterplotLayer", data=df_pesawat, get_position='[longitude, latitude]',
                get_radius=15000, get_fill_color=[255, 215, 0, 200], pickable=True, auto_highlight=True,
            )
            view_state = pdk.ViewState(latitude=-2.5, longitude=118.0, zoom=4, pitch=30)
            peta_radar = pdk.Deck(
                layers=[layer_pesawat], initial_view_state=view_state,
                tooltip={"html": "<b>Penerbangan:</b> {Callsign (No. Penerbangan)} <br/><b>Ketinggian:</b> {Ketinggian (meter)} m <br/><b>Kecepatan:</b> {Kecepatan (m/s)} m/s"},
                map_style="mapbox://styles/mapbox/dark-v10"
            )
            st.pydeck_chart(peta_radar, use_container_width=True)
            with st.expander("Tampilkan Log Data Penerbangan Mentah"):
                st.dataframe(df_pesawat, use_container_width=True, hide_index=True)
        else:
            st.warning("Sinyal radar udara sedang terputus (Server OpenSky Sibuk).")
            
    # --- TAB 2: CCTV DARAT & TOL NASIONAL ---
    with tab_darat:
        st.markdown("#### 🚗 Jaringan CCTV Darat & Tol Nasional")
        st.info("Mengakses aliran video M3U8/HLS dari kamera pengawas Area Traffic Control System (ATCS) dan CCTV Jalan Tol di seluruh wilayah.")
        
        # Basis Data Jaringan CCTV (Menggunakan aliran MUX HLS publik sebagai placeholder yang berfungsi stabil.
        # Anda dapat mengganti URL ini dengan URL m3u8 asli dari instansi pemerintah saat integrasi produksi).
        cctv_database = {
            "DKI Jakarta (Jabodetabek)": {
                "Tol Dalam Kota (Semanggi)": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "Tol JORR (KM 22)": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "ATCS Bundaran HI": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
            },
            "Jawa Barat": {
                "Tol Cipularang (KM 90)": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "Tol Cipali (KM 102)": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "ATCS Pasteur Bandung": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
            },
            "Jawa Tengah & DIY": {
                "Tol Trans Jawa (Semarang)": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "ATCS Malioboro Jogja": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
            },
            "Sumatera & Bali": {
                "Tol Bakauheni (Lampung)": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "Tol Bali Mandara": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8"
            }
        }
        
        col_kontrol, col_layar = st.columns([1, 2.5])
        
        with col_kontrol:
            wilayah = st.selectbox("🌐 Pilih Wilayah Regional:", list(cctv_database.keys()))
            kumpulan_titik = list(cctv_database[wilayah].keys())
            
            titik = st.selectbox("📍 Pilih Titik Kamera (Fokus):", kumpulan_titik)
            mode_layar = st.radio("🖥️ Mode Tampilan Layar:", ["Layar Fokus (1 Kamera)", "Video Wall (Grid Kamera)"])
            
            st.divider()
            st.caption("ℹ️ *Catatan Keamanan:* Untuk menjaga stabilitas server demo, sistem menggunakan aliran HLS test-stream. Untuk integrasi penuh, masukkan token M3U8 resmi dari BPJT/Korlantas ke dalam kode.")
            
        with col_layar:
            if mode_layar == "Layar Fokus (1 Kamera)":
                url_cctv = cctv_database[wilayah][titik]
                render_cctv_player(url_cctv, f"{titik} - {wilayah}", tinggi=400)
            else:
                # Mode Video Wall (Menampilkan banyak CCTV sekaligus mirip Command Center sungguhan)
                st.markdown(f"**Menampilkan Pemindaian Area: {wilayah}**")
                c1, c2 = st.columns(2)
                with c1:
                    if len(kumpulan_titik) > 0:
                        render_cctv_player(cctv_database[wilayah][kumpulan_titik[0]], kumpulan_titik[0], tinggi=220)
                    if len(kumpulan_titik) > 2:
                        render_cctv_player(cctv_database[wilayah][kumpulan_titik[2]], kumpulan_titik[2], tinggi=220)
                with c2:
                    if len(kumpulan_titik) > 1:
                        render_cctv_player(cctv_database[wilayah][kumpulan_titik[1]], kumpulan_titik[1], tinggi=220)
                    if len(kumpulan_titik) > 3:
                        render_cctv_player(cctv_database[wilayah][kumpulan_titik[3]], kumpulan_titik[3], tinggi=220)

    # --- TAB 3: LAUT (Placeholder) ---
    with tab_laut:
        st.markdown("#### 🚢 Radar Kapal Laut (Marine Traffic)")
        st.info("Penyadapan sinyal AIS (Automatic Identification System) maritim (Dalam pengembangan).")