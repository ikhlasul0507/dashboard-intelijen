import sys
from streamlit.web import cli as stcli
import os

if __name__ == '__main__':
    # Mengatur direktori kerja otomatis ke folder aplikasi
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--global.developmentMode=false",
        "--server.headless=true"
    ]
    sys.exit(stcli.main())