import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Inisialisasi Database Lokal
def init_db():
    conn = sqlite3.connect('intel_arsip.db')
    c = conn.cursor()
    # Membuat tabel jika belum ada
    c.execute('''CREATE TABLE IF NOT EXISTS log_aktivitas
                 (waktu TEXT, kategori TEXT, keterangan TEXT)''')
    conn.commit()
    return conn

def render():
    st.markdown("### 🗄️ Arsip & Basis Data Internal (Local DB)")
    st.caption("Penyimpanan log aktivitas operasi intelijen menggunakan SQLite.")
    
    conn = init_db()
    col1, col2 = st.columns([1, 2])
    
    # Form Input di Kolom Kiri
    with col1:
        st.subheader("Catat Jurnal Baru")
        kategori = st.selectbox("Kategori Operasi", ["Investigasi Siber", "Media Monitoring", "Pemantauan Cuaca", "Lainnya"])
        keterangan = st.text_area("Catatan / Temuan Intelijen")
        
        if st.button("Simpan ke Database"):
            if keterangan:
                waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                c = conn.cursor()
                # Query SQL Insert Data
                c.execute("INSERT INTO log_aktivitas VALUES (?, ?, ?)", (waktu_sekarang, kategori, keterangan))
                conn.commit()
                st.success("Jurnal berhasil disimpan permanen ke Database!")
            else:
                st.warning("Keterangan tidak boleh kosong.")
                
    # Tabel Output di Kolom Kanan
    with col2:
        st.subheader("Buku Arsip Historis")
        # Query SQL Select Data
        df_log = pd.read_sql_query("SELECT * FROM log_aktivitas ORDER BY waktu DESC", conn)
        if not df_log.empty:
            st.dataframe(df_log, use_container_width=True, hide_index=True)
        else:
            st.info("Database masih kosong. Belum ada jurnal yang dicatat.")
    
    conn.close()