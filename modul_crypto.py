import streamlit as st
import base64
import urllib.parse
import hashlib

def render():
    st.markdown("**Modul Kalkulator Kriptografi & Dekode Sandi (Cyber Toolbox)**")
    st.caption("Alat bantu cepat untuk konversi teks, Base64, URL Encoding, dan kalkulasi Hash MD5/SHA.")
    
    tab_enc, tab_hash = st.tabs(["🔤 Konversi & Enkode", "🔐 Hash Calculator"])
    
    with tab_enc:
        teks_input = st.text_area("Masukkan Teks Target:", "Contoh teks investigasi...")
        operasi = st.selectbox("Pilih Operasi:", [
            "Base64 Encode", "Base64 Decode", 
            "URL Encode", "URL Decode"
        ])
        
        if st.button("Eksekusi Konversi"):
            try:
                if operasi == "Base64 Encode":
                    hasil = base64.b64encode(teks_input.encode('utf-8')).decode('utf-8')
                elif operasi == "Base64 Decode":
                    hasil = base64.b64decode(teks_input.encode('utf-8')).decode('utf-8')
                elif operasi == "URL Encode":
                    hasil = urllib.parse.quote(teks_input)
                elif operasi == "URL Decode":
                    hasil = urllib.parse.unquote(teks_input)
                
                st.text_area("Hasil Konversi:", value=hasil, height=100)
            except Exception as e:
                st.error(f"Kesalahan pemrosesan format: {e}")
                
    with tab_hash:
        teks_hash = st.text_input("Masukkan Teks untuk Dihitung Hash-nya:")
        if st.button("Hitung Hash"):
            if teks_hash:
                b = teks_hash.encode('utf-8')
                st.write(f"**MD5:** `{hashlib.md5(b).hexdigest()}`")
                st.write(f"**SHA-1:** `{hashlib.sha1(b).hexdigest()}`")
                st.write(f"**SHA-256:** `{hashlib.sha256(b).hexdigest()}`")
            else:
                st.warning("Masukkan teks terlebih dahulu.")