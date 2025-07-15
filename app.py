import streamlit as st
import pandas as pd
from utils.recommender import recommend_parfum, load_data, save_history, load_history

# Konfigurasi layout halaman web
st.set_page_config(layout="wide", page_title="Parfum Recommender")

# CSS Custom
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #fff9f4;
    }
    section.main, .block-container {
        background-color: #eff5fa !important;
    }
    .custom-title {
        font-size: 40px;
        font-weight: bold;
        color: #2f456f;
        text-align: center;
        margin-bottom: 30px;
    }
    section[data-testid="stSidebar"] {
        background-color: #c7dbec !important;
    }
    .sidebar-title {
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #2f456f;
    }
    .stButton > button,
    div.stForm button {
        padding: 10px 20px;
        border-radius: 10px;
        background-color: #5374ac !important;
        color: #ffffff !important;
        font-weight: bold;
        border: none;
        transition: background-color 0.3s ease;
        text-align: left !important;
        display: inline-block !important;
    }
    .stButton > button:hover,
    div.stForm button:hover {
        background-color: #2f456f !important;
        color: #ffffff !important;
        box-shadow: none !important;
    }
    .stButton > button:focus,
    .stButton > button:active,
    div.stForm button:focus,
    div.stForm button:active {
        background-color: #2f456f !important;
        color: #ffffff !important;
        outline: none !important;
        box-shadow: none !important;
    }
    label {
        font-weight: bold;
        color: #2f456f !important;
    }
    div[data-baseweb="select"] > div {
        background-color: #c7dbec !important;
        border-radius: 8px;
        color: #2f456f;
        border: 1px solid #2f456f !important;
    }
    div[data-baseweb="select"] input {
        color: #2f456f !important;
        font-weight: bold;
    }
    div[data-baseweb="menu"] {
        background-color: #e3eff9 !important;
        color: #2f456f;
    }
    div[data-baseweb="option"]:hover {
        background-color: #b2cde3 !important;
        color: #1e3555 !important;
    }
    div[data-baseweb="option"][aria-selected="true"] {
        background-color: #5374ac !important;
        color: #ffffff !important;
    }
    .rekomendasi-title {
        font-size: 24px;
        font-weight: bold;
        color: #2f456f;
        margin-top: 30px;
        margin-bottom: 15px;
    }
    .perfume-card {
        background-color: #8bafd0;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
        margin-bottom: 25px;
    }
    .perfume-title {
        font-size: 22px;
        font-weight: bold;
        color: #f5f5f5;
        margin-bottom: 10px;
    }
    .perfume-details {
        font-size: 16px;
        color: #f5f5f5;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Load dataset parfum dari file CSV
df = load_data()

# Sidebar: menampilkan riwayat rekomendasi sebelumnya
st.sidebar.markdown('<div class="sidebar-title">Riwayat Rekomendasi</div>', unsafe_allow_html=True)
history = load_history()

# Tampilkan daftar riwayat sebagai tombol di sidebar (maks. 10 terakhir)
for i, item in enumerate(history[::-1]): # ditampilkan dari yang terbaru
    timestamp = item.get("timestamp", "")[:16].replace("T", " ") # format tanggal singkat
    label = f"{item['aktivitas']} ({item['waktu']}) - {timestamp}"
    if st.sidebar.button(label, key=f"history_{i}"):
        # Jika tombol diklik, isi ulang form dan hasil rekomendasi sebelumnya
        st.session_state['form_input'] = {
            "aktivitas": item["aktivitas"],
            "waktu": item["waktu"],
            "durasi": item["durasi"]
        }
        st.session_state['recommendation'] = item["rekomendasi"]

# Judul utama halaman
st.markdown('<div class="custom-title">Rekomendasi Parfum Berdasarkan Aktivitasmu</div>', unsafe_allow_html=True)

# Form input user
with st.form("form_parfum"):
    aktivitas = st.selectbox("Pilih Jenis Aktivitas", df['aktivitas'].unique())
    waktu = st.selectbox("Pilih Waktu Aktivitas", df['waktu'].unique())
    durasi = st.selectbox("Pilih Durasi Aktivitas", df['durasi'].unique())
    submitted = st.form_submit_button("Dapatkan Rekomendasi")

    if submitted:
        # Input disimpan dalam dictionary
        input_data = {"aktivitas": aktivitas, "waktu": waktu, "durasi": durasi}
        # Lakukan proses rekomendasi parfum
        results = recommend_parfum(df, input_data)
        # Simpan ke session agar bisa ditampilkan kembali
        st.session_state['form_input'] = input_data
        st.session_state['recommendation'] = results.to_dict(orient="records")
        # Simpan ke riwayat (max 10 terakhir)
        save_history(input_data, results)

# Tampilkan Rekomendasi
if 'form_input' in st.session_state and 'recommendation' in st.session_state:
    st.markdown('<div class="rekomendasi-title">Rekomendasi Parfum</div>', unsafe_allow_html=True)
    results = pd.DataFrame(st.session_state['recommendation'])

    # Untuk setiap parfum yang direkomendasikan, tampilkan info dan gambar
    for _, row in results.iterrows():
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                # Menampilkan gambar parfum
                st.image(f"data/images/{row['image']}", width=150)
            with col2:
                # Menampilkan detail parfum
                st.markdown(f"""
                    <div class="perfume-card">
                        <div class="perfume-title">{row['nama']} ({row['merek']})</div>
                        <div class="perfume-details"><strong>Notes:</strong> {row['notes']}</div>
                        <div class="perfume-details"><strong>Harga:</strong> ${row['harga']}</div>
                        <div class="perfume-details"><strong>Rating:</strong> ⭐{row['rating']}</div>
                        <div class="perfume-details"><strong>Gender:</strong> {row['gender']}</div>
                    </div>
                """, unsafe_allow_html=True)

                