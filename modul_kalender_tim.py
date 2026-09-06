import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

# --- INISIALISASI DATABASE & DATA AWAL ---
def init_db():
    conn = sqlite3.connect('intel_arsip.db') # Bergabung di file database yang sama
    c = conn.cursor()
    # Membuat tabel untuk Kalender Konten
    c.execute('''CREATE TABLE IF NOT EXISTS kalender_konten
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  tanggal TEXT, 
                  judul TEXT, 
                  platform TEXT, 
                  status TEXT, 
                  catatan TEXT)''')
    
    # Mengisi data awal operasional jika tabel masih kosong
    c.execute("SELECT COUNT(*) FROM kalender_konten")
    if c.fetchone()[0] == 0:
        default_data = [
            ('2026-03-10', 'Dokumentasi Kunjungan SMAN 1 Cicurug', 'Instagram', 'Dipublikasikan', 'Upload foto kegiatan dan caption edukasi'),
            ('2026-03-15', 'Dokumentasi Kunjungan SMAN 1 Cidahu', 'Instagram', 'Dipublikasikan', 'Sorotan antusiasme siswa dan sesi tanya jawab'),
            ('2026-04-10', 'Sosialisasi SOP Tim Media', 'Internal', 'Dipublikasikan', 'Implementasi standar operasional penyimpanan foto dan upload konten'),
            ('2026-04-20', 'Teaser Daster Cindo (Size Chart)', 'TikTok', 'Draft', 'Persiapan peluncuran visual, butuh review desain logo'),
            ((datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d'), 'Rapat Evaluasi SOP Baru', 'Internal', 'Terjadwal', 'Membahas alur kerja dan evaluasi engagement bulanan')
        ]
        c.executemany("INSERT INTO kalender_konten (tanggal, judul, platform, status, catatan) VALUES (?, ?, ?, ?, ?)", default_data)
        conn.commit()
    return conn

# --- MERAKIT ANTARMUKA MODUL ---
def render():
    st.markdown("### 🗓️ Kalender Konten & Manajemen Tim")
    st.caption("Pusat kendali penjadwalan publikasi, dokumentasi kegiatan, dan alur kerja operasional tim media.")
    
    conn = init_db()
    
    # 1. METRIK STATUS
    df_all = pd.read_sql_query("SELECT * FROM kalender_konten", conn)
    if not df_all.empty:
        total = len(df_all)
        terjadwal = len(df_all[df_all['status'] == 'Terjadwal'])
        draft = len(df_all[df_all['status'] == 'Draft'])
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Agenda/Konten", total)
        m2.metric("Menunggu Rilis (Terjadwal)", terjadwal)
        m3.metric("Dalam Pengerjaan (Draft)", draft)
    
    st.divider()
    
    col_input, col_tabel = st.columns([1, 2.5])
    
    # 2. PANEL INPUT AGENDA BARU
    with col_input:
        st.subheader("➕ Tambah Agenda")
        with st.form("form_konten"):
            tgl = st.date_input("Tanggal Pelaksanaan / Rilis")
            judul = st.text_input("Judul Konten / Kegiatan")
            platform = st.selectbox("Platform Target", ["Instagram", "TikTok", "Website", "Internal", "YouTube", "Lainnya"])
            status = st.selectbox("Status Pengerjaan", ["Draft", "Terjadwal", "Dipublikasikan"])
            catatan = st.text_area("Catatan Khusus (Instruksi/SOP)")
            
            submit = st.form_submit_button("Simpan Jadwal")
            
            if submit:
                if judul:
                    c = conn.cursor()
                    c.execute("INSERT INTO kalender_konten (tanggal, judul, platform, status, catatan) VALUES (?, ?, ?, ?, ?)", 
                              (tgl.strftime("%Y-%m-%d"), judul, platform, status, catatan))
                    conn.commit()
                    st.success("Berhasil ditambahkan!")
                    time.sleep(1) # Jeda agar pesan sukses terbaca sebelum reload
                    st.rerun()
                else:
                    st.warning("Judul wajib diisi!")

    # 3. PANEL TABEL (KANBAN STYLE)
    with col_tabel:
        st.subheader("📋 Papan Operasional (Kanban)")
        
        # Filter Status
        filter_status = st.radio("Saring berdasarkan status:", ["Semua", "Draft", "Terjadwal", "Dipublikasikan"], horizontal=True)
        
        query = "SELECT tanggal as Tanggal, judul as Judul, platform as Platform, status as Status, catatan as Catatan FROM kalender_konten"
        if filter_status != "Semua":
            query += f" WHERE status = '{filter_status}'"
        query += " ORDER BY tanggal DESC"
        
        df_tampil = pd.read_sql_query(query, conn)
        
        if not df_tampil.empty:
            st.dataframe(
                df_tampil, 
                use_container_width=True, 
                hide_index=True,
                height=350
            )
        else:
            st.info("Tidak ada data untuk status ini.")
            
    conn.close()