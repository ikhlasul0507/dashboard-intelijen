import streamlit as st
import requests
import time

def render():
    st.markdown("### 🌐 Radar Infrastruktur Siber")
    st.caption("Pantau status aktif (uptime) dan waktu respons website target.")
    
    target_url = st.text_input("Masukkan URL Target (contoh: https://www.google.com):", "https://")
    
    if st.button("Pindai Target"):
        if target_url and target_url != "https://":
            try:
                start_time = time.time()
                res = requests.get(target_url, timeout=5)
                end_time = time.time()
                
                waktu_respons = round((end_time - start_time) * 1000, 2)
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Status Code HTTP", res.status_code)
                col2.metric("Waktu Respons", f"{waktu_respons} ms")
                col3.metric("Server Terdeteksi", res.headers.get('Server', 'Disembunyikan/Unknown'))
                
                if res.status_code == 200:
                    st.success("✅ Target beroperasi normal (Uptime OK).")
                else:
                    st.warning(f"⚠️ Target mengembalikan kode error: {res.status_code}")
                    
            except Exception as e:
                st.error(f"🚨 Gagal menjangkau target. Website mungkin down atau dilindungi firewall. Detail: {e}")
        else:
            st.warning("Masukkan URL yang valid.")