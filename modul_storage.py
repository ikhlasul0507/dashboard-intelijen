import streamlit as st
import os
import pandas as pd
import base64
from datetime import datetime

UPLOAD_DIR = "cloud_storage_repo"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# --- FUNGSI POP-UP PRATINJAU DENGAN RENDER PDF HTML ---
@st.dialog("Pratinjau Berkas (View)", width="large")
def modal_view_file(nama_file, file_path, ukuran, waktu):
    st.markdown(f"**Nama Berkas:** `{nama_file}`")
    st.caption(f"Waktu Unggah: {waktu} | Ukuran: {ukuran} KB")
    st.divider()
    
    ext = nama_file.split('.')[-1].lower()
    
    if ext in ['png', 'jpg', 'jpeg']:
        # Pratinjau Gambar
        st.image(file_path, caption=nama_file, use_container_width=True)
        
    elif ext == 'pdf':
        # Pratinjau PDF menggunakan Base64 Embedding agar tampil langsung di pop-up
        try:
            with open(file_path, "rb") as f:
                base64_pdf = base64.b64encode(f.read()).decode('utf-8')
            
            pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="500px" type="application/pdf"></iframe>'
            st.markdown(pdf_display, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Gagal merender dokumen PDF: {e}")
            
    elif ext in ['txt', 'csv', 'md', 'py', 'json']:
        # Pratinjau Teks / Kode
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                konten = f.read()
            st.text_area("Isi Berkas:", konten, height=300)
        except Exception:
            st.info("Berkas teks tidak dapat dibaca dengan enkripsi ini.")
    else:
        st.info(f"ℹ️ Pratinjau visual langsung tidak tersedia untuk format `.{ext}`. Silakan unduh berkas untuk membukanya.")
        
    st.divider()
    with open(file_path, "rb") as fp:
        st.download_button(
            label="📥 Unduh Berkas Ini",
            data=fp,
            file_name=nama_file,
            use_container_width=True
        )

def render():
    st.markdown("### ☁️ Cloud Storage (Pusat Berkas & Dokumen)")
    st.caption("Repositori terpusat dengan dukungan pratinjau PDF langsung, unggah multi-berkas, dan manajemen file.")
    
    col_upload, col_list = st.columns([1, 2])
    
    with col_upload:
        st.subheader("📤 Unggah Berkas (Multi-File)")
        with st.form("form_upload", clear_on_submit=True):
            uploaded_files = st.file_uploader(
                "Pilih satu atau banyak berkas sekaligus:", 
                accept_multiple_files=True
            )
            
            submit_btn = st.form_submit_button("Unggah Semua ke Cloud")
            
            if submit_btn:
                if uploaded_files:
                    jumlah_sukses = 0
                    for uploaded_file in uploaded_files:
                        nama_asli = uploaded_file.name
                        timestamp_prefix = datetime.now().strftime("%Y%m%d_%H%M%S_")
                        nama_tersimpan = timestamp_prefix + nama_asli
                        file_path = os.path.join(UPLOAD_DIR, nama_tersimpan)
                        
                        try:
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            jumlah_sukses += 1
                        except Exception:
                            pass
                            
                    st.success(f"Berhasil mengunggah {jumlah_sukses} berkas!")
                else:
                    st.warning("Pilih minimal satu berkas terlebih dahulu!")
                    
    with col_list:
        st.subheader("📂 Daftar Berkas Tersimpan")
        
        if os.path.exists(UPLOAD_DIR):
            files = os.listdir(UPLOAD_DIR)
            
            if files:
                file_data = []
                for f in files:
                    full_path = os.path.join(UPLOAD_DIR, f)
                    if os.path.isfile(full_path):
                        size_kb = round(os.path.getsize(full_path) / 1024, 2)
                        waktu_mod = datetime.fromtimestamp(os.path.getmtime(full_path)).strftime("%Y-%m-%d %H:%M:%S")
                        
                        file_data.append({
                            "Nama Berkas": f,
                            "Ukuran (KB)": size_kb,
                            "Waktu Unggah": waktu_mod,
                            "Path": full_path
                        })
                        
                for idx, row in enumerate(file_data):
                    with st.container(border=True):
                        c1, c2, c3, c4 = st.columns([1.8, 0.7, 0.7, 0.7])
                        with c1:
                            nama_tampil = row['Nama Berkas'].split('_', 2)[-1] if len(row['Nama Berkas'].split('_')) > 2 else row['Nama Berkas']
                            st.markdown(f"**📁 {nama_tampil}**")
                            st.caption(f"🕒 {row['Waktu Unggah']} | 📦 {row['Ukuran (KB)']} KB")
                        with c2:
                            if st.button("👁️ View", key=f"view_{idx}", use_container_width=True):
                                modal_view_file(nama_tampil, row['Path'], row['Ukuran (KB)'], row['Waktu Unggah'])
                        with c3:
                            with open(row['Path'], "rb") as file_download:
                                st.download_button(
                                    label="📥 Unduh",
                                    data=file_download,
                                    file_name=nama_tampil,
                                    key=f"download_{idx}",
                                    use_container_width=True
                                )
                        with c4:
                            if st.button("🗑️ Hapus", key=f"del_{idx}", use_container_width=True):
                                os.remove(row['Path'])
                                st.rerun()
            else:
                st.info("Belum ada berkas yang diunggah ke dalam repositori cloud.")