import streamlit as st
import requests

def render():
    st.markdown("**Modul Intelijen Domain & WHOIS Tracker**")
    st.caption("Lacak rekam jejak pendaftaran domain, server, dan data administratif secara pasif menggunakan protokol RDAP.")
    
    domain_target = st.text_input("Masukkan Nama Domain (contoh: google.com):", "google.com")
    
    if st.button("Pindai Domain"):
        if domain_target:
            url = f"https://rdap.org/domain/{domain_target.strip()}"
            try:
                res = requests.get(url, timeout=10)
                if res.status_code == 200:
                    data = res.json()
                    st.success(f"Berhasil menarik data RDAP untuk **{domain_target}**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Status Domain:**", ", ".join(data.get('status', ['Tidak Diketahui'])))
                        st.write("**Handle:**", data.get('handle', '-'))
                    with col2:
                        entities = data.get('entities', [])
                        st.write("**Jumlah Entitas Terdaftar:**", len(entities))
                        
                    with st.expander("Lihat Data Mentah JSON (Raw RDAP)"):
                        st.json(data)
                else:
                    st.error(f"Domain tidak ditemukan atau server RDAP menolak permintaan (Kode: {res.status_code})")
            except Exception as e:
                st.error(f"Gagal terhubung ke jaringan RDAP: {e}")
        else:
            st.warning("Masukkan nama domain terlebih dahulu.")