import streamlit as st
import requests
import pandas as pd
import re

@st.cache_data(ttl=300)
def ambil_berita_dari_sumber(url_rss):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        res = requests.get(url_rss, headers=headers, timeout=10)
        
        if res.status_code == 200:
            items = re.findall(r'<item>(.*?)</item>', res.text, re.DOTALL)
            berita_list = []
            
            for item in items[:15]:
                title_match = re.search(r'<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>', item, re.DOTALL)
                link_match = re.search(r'<link>(.*?)</link>', item, re.DOTALL)
                date_match = re.search(r'<pubDate>(.*?)</pubDate>', item, re.DOTALL)
                
                judul = title_match.group(1).strip() if title_match else "Tanpa Judul"
                judul = re.sub(r'<.*?>', '', judul)
                
                link = link_match.group(1).strip() if link_match else "#"
                waktu = date_match.group(1).strip() if date_match else "Waktu tidak diketahui"
                
                berita_list.append({
                    "Waktu": waktu,
                    "Judul": judul,
                    "Link": link
                })
                
            return pd.DataFrame(berita_list)
    except Exception:
        pass
        
    return pd.DataFrame()

def render():
    st.markdown("### 📡 Berita Nasional & Ekonomi Terkini (Real-Time)")
    st.caption("Pusat pantauan radar berita nasional terintegrasi dengan pilihan portal media horizontal.")
    
    # Kamus 14 Pilihan Sumber Berita Nasional dan URL RSS-nya
    sumber_berita = {
        "CNBC Indonesia": "https://www.cnbcindonesia.com/news/rss",
        "CNN Indonesia": "https://www.cnnindonesia.com/nasional/rss",
        "Detik News": "https://news.detik.com/berita/rss",
        "Detik Finance": "https://finance.detik.com/rss",
        "Liputan6": "https://www.liputan6.com/rss/news",
        "Antara News": "https://www.antaranews.com/rss/top-news.xml",
        "Republika": "https://www.republika.co.id/rss/nasional/",
        "Tempo Nasional": "http://rss.tempo.co/nasional",
        "Tempo Bisnis": "http://rss.tempo.co/bisnis",
        "Suara.com": "https://www.suara.com/rss/news",
        "Okezone": "https://sindikasi.okezone.com/index.php/okezone/RSS2.0",
        "Sindo News": "https://arnas.sindonews.com/rss",
        "Tribun News": "https://www.tribunnews.com/rss",
        "JPNN": "https://www.jpnn.com/rss"
    }
    
    st.markdown("**Pilih Portal Berita Nasional:**")
    
    # Menggunakan st.pills atau st.radio horizontal agar pilihan berjejer menyamping
    daftar_portal = list(sumber_berita.keys())
    
    # Jika versi streamlit mendukung st.pills, gunakan pills. Jika tidak, gunakan radio horizontal.
    try:
        pilihan_portal = st.pills("Portal:", daftar_portal, default=daftar_portal[0], label_visibility="collapsed")
        if not pilihan_portal:
            pilihan_portal = daftar_portal[0]
    except Exception:
        pilihan_portal = st.radio("Portal:", daftar_portal, horizontal=True, label_visibility="collapsed")
        
    url_terpilih = sumber_berita[pilihan_portal]
    
    st.divider()
    
    with st.spinner(f"Menarik siaran radar terbaru dari {pilihan_portal}..."):
        df_berita = ambil_berita_dari_sumber(url_terpilih)
        
    if not df_berita.empty:
        st.success(f"✅ Berhasil menyadap {len(df_berita)} radar berita dari **{pilihan_portal}**.")
        
        kolom_hasil = st.columns(2)
        for index, row in df_berita.iterrows():
            with kolom_hasil[index % 2]:
                with st.container(border=True):
                    st.markdown(f"**{row['Judul']}**")
                    st.caption(f"🕒 {row['Waktu']}")
                    st.link_button("🔗 Buka Artikel Asli", row['Link'], use_container_width=True)
    else:
        st.warning(f"Sistem sedang menyinkronkan jalur transmisi RSS dengan {pilihan_portal}. Silakan pilih media alternatif lainnya jika kendala berlanjut.")