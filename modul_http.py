import streamlit as st
import requests

def render():
    st.markdown("**Modul Analisis Header & Keamanan HTTP (Deep Inspector)**")
    st.caption("Periksa header keamanan web server, proteksi firewall, dan sertifikat transport.")
    
    url_target = st.text_input("Masukkan URL Target (contoh: https://example.com):", "https://")
    
    if st.button("Inspeksi Header Server"):
        if url_target and url_target != "https://":
            try:
                res = requests.get(url_target, timeout=10)
                st.success(f"Inspeksi berhasil! Status HTTP: `{res.status_code}`")
                
                headers = res.headers
                sec_headers = {
                    "Strict-Transport-Security (HSTS)": headers.get('Strict-Transport-Security', '❌ Tidak Ditemukan'),
                    "X-Frame-Options (Clickjacking Protect)": headers.get('X-Frame-Options', '❌ Tidak Ditemukan'),
                    "Content-Security-Policy (CSP)": headers.get('Content-Security-Policy', '❌ Tidak Ditemukan'),
                    "X-Content-Type-Options": headers.get('X-Content-Type-Options', '❌ Tidak Ditemukan'),
                    "Server Software": headers.get('Server', 'Disembunyikan / Unknown')
                }
                
                st.markdown("**Pemeriksaan Keamanan Header:**")
                for k, v in sec_headers.items():
                    if "❌" in str(v):
                        st.warning(f"**{k}**: {v}")
                    else:
                        st.success(f"**{k}**: {v}")
                        
                with st.expander("Lihat Seluruh Response Headers"):
                    st.json(dict(headers))
            except Exception as e:
                st.error(f"Gagal melakukan inspeksi HTTP: {e}")
        else:
            st.warning("Masukkan URL yang valid.")