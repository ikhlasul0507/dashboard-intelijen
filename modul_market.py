import streamlit as st
import pandas as pd
import yfinance as yf

# --- ENGINE PENARIK DATA PASAR KEUANGAN ---
@st.cache_data(ttl=300) # Refresh otomatis setiap 5 menit
def ambil_data_ekonomi():
    # Daftar instrumen yang dipantau (IHSG, Kurs Rupiah, S&P 500 AS, dan Harga Emas)
    instrumen = {
        "IHSG (Bursa Efek Indonesia)": "^JKSE",
        "USD/IDR (Kurs Rupiah)": "IDR=X",
        "S&P 500 (Pasar Global)": "^GSPC",
        "Emas Berjangka (Gold)": "GC=F"
    }
    
    ringkasan = []
    riwayat_grafik = {}
    
    for nama, simbol in instrumen.items():
        try:
            ticker = yf.Ticker(simbol)
            # Menarik data riwayat perdagangan 1 bulan terakhir
            hist = ticker.history(period="1mo")
            
            if not hist.empty:
                # Mengambil data harga penutupan hari ini dan kemarin
                harga_hari_ini = hist['Close'].iloc[-1]
                harga_kemarin = hist['Close'].iloc[-2]
                
                # Kalkulasi selisih dan persentase
                selisih = harga_hari_ini - harga_kemarin
                persentase = (selisih / harga_kemarin) * 100
                
                # Format angka agar rapi
                simbol_mata_uang = "Rp " if "IDR" in nama else ("" if "IHSG" in nama else "$")
                
                ringkasan.append({
                    "Indikator": nama,
                    "Nilai Saat Ini": f"{simbol_mata_uang}{harga_hari_ini:,.2f}",
                    "Perubahan": selisih,
                    "Persentase": f"{persentase:+.2f}%"
                })
                
                # Menyimpan data tabel riwayat untuk grafik (Hanya kolom Close)
                hist.index = hist.index.strftime('%Y-%m-%d') # Merapikan format tanggal
                riwayat_grafik[nama] = hist[['Close']]
                
        except Exception as e:
            st.error(f"Gagal memuat {nama}: {e}")
            
    return pd.DataFrame(ringkasan), riwayat_grafik

# --- MERAKIT ANTARMUKA MODUL ---
def render():
    st.markdown("### 📊 Intelijen Pasar & Ekonomi Makro")
    st.caption("Memantau pergerakan IHSG, Nilai Tukar Rupiah, dan Indikator Global secara langsung dari bursa.")
    
    with st.spinner("Terhubung ke satelit pasar keuangan global..."):
        df_ringkasan, dict_grafik = ambil_data_ekonomi()
        
    if not df_ringkasan.empty:
        # 1. MENAMPILKAN KARTU METRIK (WIDGET ATAS)
        kolom_metrik = st.columns(len(df_ringkasan))
        
        for i, baris in df_ringkasan.iterrows():
            with kolom_metrik[i]:
                # Streamlit otomatis memberi warna hijau/merah berdasarkan nilai 'delta' (perubahan)
                st.metric(
                    label=baris['Indikator'],
                    value=baris['Nilai Saat Ini'],
                    delta=baris['Persentase']
                )
                
        st.divider()
        
        # 2. MENAMPILKAN GRAFIK ANALISIS TREN (1 BULAN TERAKHIR)
        st.markdown("**Tren Pergerakan (1 Bulan Terakhir)**")
        col_kiri, col_kanan = st.columns(2)
        
        with col_kiri:
            if "IHSG (Bursa Efek Indonesia)" in dict_grafik:
                st.write("📈 **IHSG (^JKSE)**")
                st.line_chart(dict_grafik["IHSG (Bursa Efek Indonesia)"])
                
            if "Emas Berjangka (Gold)" in dict_grafik:
                st.write("🥇 **Harga Emas (USD/Troy Ounce)**")
                st.line_chart(dict_grafik["Emas Berjangka (Gold)"])
                
        with col_kanan:
            if "USD/IDR (Kurs Rupiah)" in dict_grafik:
                st.write("💵 **Kurs USD ke IDR** *(Grafik naik berarti Rupiah melemah)*")
                st.line_chart(dict_grafik["USD/IDR (Kurs Rupiah)"])
                
            if "S&P 500 (Pasar Global)" in dict_grafik:
                st.write("📉 **S&P 500 (Bursa Amerika)**")
                st.line_chart(dict_grafik["S&P 500 (Pasar Global)"])
                
    else:
        st.warning("Gagal mengambil data pasar. Pastikan koneksi internet stabil atau coba beberapa saat lagi.")