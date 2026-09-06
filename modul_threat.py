import streamlit as st
import requests
import hashlib

def cek_kebocoran_password(password):
    # Menggunakan metode k-anonymity (Sangat Aman)
    # Hanya 5 karakter hash pertama yang dikirim ke jaringan publik
    sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
    prefix5, tail = sha1_password[:5], sha1_password[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix5}"
    
    res = requests.get(url)
    if res.status_code == 200:
        hashes = (line.split(':') for line in res.text.splitlines())
        for h, count in hashes:
            if h == tail:
                return int(count) # Mengembalikan jumlah kebocoran
    return 0

def render():
    st.markdown("### 🕵️‍♂️ Radar Kebocoran Data (Data Breach)")
    st.caption("Periksa apakah sebuah kata sandi pernah terekspos dalam insiden peretasan global.")
    
    password_uji = st.text_input("Masukkan Kata Sandi untuk diuji keamanannya:", type="password")
    
    if st.button("Periksa Keamanan di Database Global"):
        if password_uji:
            with st.spinner("Mencocokkan dengan miliaran database peretas..."):
                jumlah_bocor = cek_kebocoran_password(password_uji)
                
                if jumlah_bocor > 0:
                    st.error(f"🚨 BAHAYA! Sandi ini telah bocor sebanyak **{jumlah_bocor:,}** kali di internet. Risiko peretasan sangat tinggi!")
                else:
                    st.success("✅ AMAN. Kata sandi ini belum pernah ditemukan dalam database peretas publik.")
        else:
            st.warning("Masukkan sandi terlebih dahulu.")