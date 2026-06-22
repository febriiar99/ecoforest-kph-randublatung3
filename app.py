import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import re
import datetime

# =====================================================
# PAGE CONFIG & CSS
# =====================================================
st.set_page_config(
    page_title="Eco-Forest Valuation KPH Randublatung",
    page_icon="🌳",
    layout="wide"
)

st.markdown("""
<style>
.block-container { padding-top:1rem; }
[data-testid="stMetric"] {
    border-radius:18px; padding:18px;
    border:1px solid rgba(120,120,120,.2);
    background:rgba(120,120,120,.05);
}
h1,h2,h3 { font-weight:700; }
.identity-card {
    background:#dff0e4; border-radius:12px;
    padding:20px; color:#1f7a3f;
    margin-top:15px; margin-bottom:20px;
}
.identity-card p { margin-bottom:12px; font-size:18px; }
.desc-box {
    background:#dff0e4; border-radius:12px;
    padding:18px 22px; color:#1a5c32; margin-top:10px;
    font-size:15px; line-height:1.7;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD CSV DATA
# =====================================================
# =====================================================
# LOAD EXCEL DATA
# =====================================================
@st.cache_data
def load_data():
    try:
        # Membaca data dari file Excel
        return pd.read_excel("data_hutan.xlsx", header=None)
    except FileNotFoundError:
        st.error("File 'data_hutan.xlsx' tidak ditemukan. Pastikan file ada di folder yang sama.")
        st.stop()

raw = load_data()

# =====================================================
# HELPER FUNCTIONS
# =====================================================
def extract_number(val):
    if pd.isna(val): return None
    txt = str(val)
    # Mencari angka desimal/bulat dalam teks
    m = re.search(r"[-+]?\d*\.?\d+", txt.replace(",", "."))
    return float(m.group()) if m else None

def fix_value(val):
    """Memperbaiki nilai '2 - 5' yang dibaca sebagai tanggal oleh Excel/CSV"""
    val_str = str(val)
    if "2026" in val_str or isinstance(val, datetime.datetime):
        return "2 - 5"
    return val

def table_height(df):
    return min(650, max(200, (len(df) + 1) * 35))

# =====================================================
# EXTRACT TABLES (Sesuai indeks baris/kolom)
# =====================================================
# --- PROFIL HUTAN ---
profil_hutan = raw.iloc[2:21, 1:6].copy()
profil_hutan.columns = ["Variable", "Value", "Unit", "Year", "Note"]
profil_hutan = profil_hutan.dropna(how="all").reset_index(drop=True)

# --- PRODUKSI KAYU ---
produksi_kayu = raw.iloc[2:10, 7:9].copy()
produksi_kayu.columns = ["Komponen", "Nilai / Rentang"]
produksi_kayu = produksi_kayu.dropna(how="all").reset_index(drop=True)

# --- MASTER DATA ---
master_data = raw.iloc[2:37, 10:15].copy()
master_data.columns = ["Variable", "Value", "Unit", "Year", "Note"]
master_data["Value"] = master_data["Value"].apply(fix_value)
master_data = master_data.dropna(how="all").reset_index(drop=True)

# --- PARAMETER SIMULASI ---
parameter = raw.iloc[2:16, 16:21].copy()
parameter.columns = ["Parameter", "Nilai Dasar", "Min", "Max", "Satuan"]
parameter = parameter.dropna(how="all").reset_index(drop=True)

# =====================================================
# PARAMETER VALUES (LOGIKA EKONOMI)
# =====================================================
try:
    luas_hutan   = float(parameter.loc[parameter["Parameter"] == "Luas Hutan", "Nilai Dasar"].values[0])
    produksi     = int(float(parameter.loc[parameter["Parameter"] == "Produksi Kayu Tahunan", "Nilai Dasar"].values[0]))
    harga_kayu   = int(float(parameter.loc[parameter["Parameter"] == "Harga Kayu Jati", "Nilai Dasar"].values[0]))
    stok_karbon  = float(parameter.loc[parameter["Parameter"] == "Stok Karbon", "Nilai Dasar"].values[0])
    harga_karbon = float(parameter.loc[parameter["Parameter"] == "Harga Karbon", "Nilai Dasar"].values[0])
except Exception as e:
    st.error(f"Terjadi kesalahan saat membaca parameter angka: {e}")
    st.stop()

# --- ASUMSI DASAR ---
kurs_usd      = 16000
margin_profit = 0.35  # Asumsi margin keuntungan bersih pengelolaan jati (35%)

# Menghitung Nilai Awal
nilai_kayu_bruto = produksi * harga_kayu
nilai_kayu_netto = nilai_kayu_bruto * margin_profit
nilai_karbon     = luas_hutan * stok_karbon * harga_karbon * kurs_usd
nilai_total      = nilai_kayu_netto + nilai_karbon

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
try:
    logo = Image.open("Logo Unisbaa.png")
    st.sidebar.image(logo, use_container_width=True)
except:
    pass

st.sidebar.markdown("## 🌳 Eco-Forest Valuation")
menu = st.sidebar.radio(
    "Navigasi",
    [
        "Beranda",
        "Profil Hutan",
        "Produksi Kayu",
        "Master Data",
        "Parameter Simulasi",
        "Dashboard Summary",
    ]
)

# =====================================================
# MENU 1: BERANDA
# =====================================================
if menu == "Beranda":
    st.title("🌳 Eco-Forest Valuation KPH Randublatung")
    st.caption("PBL 6 - Ekonomi Sumber Daya Hutan")

    st.markdown("## Mata Kuliah")
    st.write("Ekonomi Sumber Daya Alam dan Lingkungan")

    st.markdown("## Dosen Pengampu")
    st.write("Yuhka Sundaya, S.E., M.Si.")

    st.markdown("""
        <div class="identity-card">
        <h4>KELOMPOK 5</h4>
        <p>• Brian Yusditama (10090224005)</p>
        <p>• Yolandi Abbas Wibisono (10090224010)</p>
        <p>• Dzulfiqar Didaf (10090224024)</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Ringkasan Data yang Berhasil Dimuat")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🌳 Profil Hutan",  len(profil_hutan))
    c2.metric("🪵 Produksi Kayu", len(produksi_kayu))
    c3.metric("📊 Master Data",   len(master_data))
    c4.metric("⚙️ Parameter",     len(parameter))

    st.markdown("---")
    st.subheader("Deskripsi Dashboard")
    st.write("Dashboard ini digunakan untuk analisis dan valuasi ekonomi sumber daya hutan KPH Randublatung, berfokus pada analisis *trade-off* skenario pengelolaan kawasan hutan berbasis kayu vs integrasi pembayaran jasa lingkungan (karbon).")

# =====================================================
# MENU 2: PROFIL HUTAN
# =====================================================
elif menu == "Profil Hutan":
    st.title("🌳 Profil Hutan")
    st.dataframe(profil_hutan, use_container_width=True, hide_index=True, height=table_height(profil_hutan))

    chart = profil_hutan[["Variable", "Value"]].copy()
    chart["Value"] = chart["Value"].apply(extract_number)
    chart = chart.dropna()

    fig = px.bar(
        chart, x="Variable", y="Value", color="Value", text="Value",
        title="Grafik Profil Hutan KPH Randublatung",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=550, template="plotly_white", xaxis_tickangle=-35)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
        <div class="desc-box">
        Profil hutan di atas menggambarkan karakteristik utama KPH Randublatung yang berlokasi di Kabupaten Blora dan Grobogan, 
        Jawa Tengah. Dengan luas kawasan mencapai <b>{luas_hutan:,.2f} ha</b>, hutan ini didominasi oleh Hutan Produksi 
        dengan komoditas utama Jati (<i>Tectona grandis</i>). Total produksi kayu tahunan yang terencana adalah sebesar <b>{produksi:,.0f} m³/tahun</b>. 
        Asumsi harga dasar kayu rata-rata adalah <b>Rp {harga_kayu:,.0f}/m³</b>, yang menjadi basis utama ekonomi konvensional bagi pengelolaan kawasan ini.
        </div>
    """, unsafe_allow_html=True)

# =====================================================
# MENU 3: PRODUKSI KAYU & JASA EKOSISTEM
# =====================================================
elif menu == "Produksi Kayu":
    st.title("🪵 Produksi Kayu & Jasa Lingkungan")
    st.dataframe(produksi_kayu, use_container_width=True, hide_index=True)

    chart_je = produksi_kayu.copy()
    chart_je["Nilai Numerik"] = chart_je["Nilai / Rentang"].apply(extract_number)
    chart_je_num = chart_je.dropna(subset=["Nilai Numerik"])

    if not chart_je_num.empty:
        fig = px.bar(
            chart_je_num, x="Komponen", y="Nilai Numerik", color="Nilai Numerik", text="Nilai Numerik",
            title="Grafik Indikator Produksi & Lingkungan",
            color_continuous_scale="Greens"
        )
        fig.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
        fig.update_layout(height=500, template="plotly_white", xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(f"""
        <div class="desc-box">
        Selain sebagai penghasil kayu, kawasan KPH Randublatung juga memiliki nilai Jasa Lingkungan (<i>Ecosystem Services</i>) yang sangat krusial. 
        Kawasan ini diperkirakan memiliki stok karbon hingga <b>{stok_karbon:,.0f} ton CO₂/ha</b>. Dengan menjaga kelestarian tegakan jati 
        (menghindari praktik tebang habis/<i>clear-cutting</i>), hutan ini secara efektif mampu meregulasi air, mencegah tingkat erosi tanah yang parah, 
        serta mendukung kelestarian biodiversitas.
        </div>
    """, unsafe_allow_html=True)

# =====================================================
# MENU 4: MASTER DATA
# =====================================================
elif menu == "Master Data":
    st.title("📊 Master Data Terpadu")
    st.dataframe(master_data, use_container_width=True, hide_index=True, height=table_height(master_data))

    chart_md = master_data[["Variable", "Value"]].copy()
    chart_md["Value"] = chart_md["Value"].apply(extract_number)
    chart_md = chart_md.dropna()

    fig = px.bar(
        chart_md, x="Variable", y="Value", color="Value", text="Value",
        title="Visualisasi Numerik Master Data",
        color_continuous_scale="Blues"
    )
    fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig.update_layout(height=620, template="plotly_white", xaxis_tickangle=-40)
    st.plotly_chart(fig, use_container_width=True)

# =====================================================
# MENU 5: PARAMETER SIMULASI
# =====================================================
elif menu == "Parameter Simulasi":
    st.title("⚙️ Parameter Simulasi Interaktif")
    
    st.write("Silakan gunakan slider di bawah ini untuk menguji sensitivitas nilai ekonomi kawasan. Produksi kayu kini ditautkan secara dinamis dengan Luas Hutan berbasis produktivitas historis.")

    st.markdown("---")
    
    # 1. Hitung Produktivitas Kayu per Hektar (m3/ha) sebagai konstanta biologis
    produktivitas_ha = produksi / luas_hutan 
    
    # 2. Input Slider
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        luas_sim = st.slider("Luas Hutan Efektif (ha)", 10000, 35000, int(luas_hutan), step=500)
        
        # Produksi Kayu sekarang dihitung OTOMATIS berdasarkan luas, bukan slider manual lagi
        produksi_sim = luas_sim * produktivitas_ha
        st.info(f"🪵 Kapasitas Produksi Kayu (Otomatis): **{produksi_sim:,.0f} m³/tahun**")
        
    with col_s2:
        harga_sim = st.slider("Harga Jual Kayu Jati (Rp/m³)", 3000000, 6000000, harga_kayu, step=100000)
        karbon_sim = st.slider("Harga Kredit Karbon (USD/ton CO₂)", 5, 30, int(harga_karbon), step=1)

    # 3. Kalkulasi Berdasarkan Input Simulasi yang Sudah Saling Terkait
    sim_kayu_bruto = produksi_sim * harga_sim
    sim_kayu_netto = sim_kayu_bruto * margin_profit
    sim_karbon = luas_sim * stok_karbon * karbon_sim * kurs_usd
    sim_total = sim_kayu_netto + sim_karbon

    st.markdown("### Hasil Valuasi Simulasi")
    c1, c2, c3 = st.columns(3)
    c1.metric("Pendapatan Bersih Kayu",  f"Rp {sim_kayu_netto/1e9:,.2f} Milyar")
    c2.metric("Nilai Valuasi Karbon", f"Rp {sim_karbon/1e9:,.2f} Milyar")
    c3.metric("Total Valuasi Kawasan",  f"Rp {sim_total/1e9:,.2f} Milyar")

    st.markdown(f"""
        <div class="desc-box">
        <i>*Catatan Logika Model: Kapasitas produksi kayu ditautkan secara dinamis dengan Luas Hutan menggunakan asumsi riap/produktivitas tegakan sebesar <b>{produktivitas_ha:,.2f} m³/ha/tahun</b>. Jika luas hutan menyusut, kemampuan produksi kayu otomatis menurun. Pendapatan bersih dihitung dengan margin laba {margin_profit*100}%.</i>
        </div>
    """, unsafe_allow_html=True)

# =====================================================
# MENU 6: DASHBOARD SUMMARY (TRADE-OFF ANALYSIS)
# =====================================================
elif menu == "Dashboard Summary":
    st.title("📈 Dashboard Summary: Trade-Off Analysis")

    c1, c2, c3 = st.columns(3)
    c1.metric("🌳 Luas Pengelolaan",    f"{luas_hutan:,.2f} Ha")
    c2.metric("🪵 Target Produksi", f"{produksi:,.0f} m³/thn")
    c3.metric("💰 Total Valuasi Ekologis",   f"Rp {nilai_total/1e9:,.2f} Milyar")

    st.markdown("---")

    # =============================================
    # KALKULASI SKENARIO (BAU vs OPTIMAL)
    # =============================================
    # 1. Skenario BAU: Hutan hanya difungsikan untuk menebang dan menjual kayu (Konvensional)
    skenario_bau = nilai_kayu_netto 
    
    # 2. Skenario Optimal: KPH menjual kayu lestari + Mendaftarkan hutan untuk sertifikasi karbon (PES)
    skenario_optimal = nilai_kayu_netto + nilai_karbon 
    
    # 3. Selisih (Nilai Tambah / Added Value)
    nilai_tambah = skenario_optimal - skenario_bau

    st.subheader("Tabel Komparasi Pengelolaan (Konversi Jati)")
    summary_df = pd.DataFrame({
        "Indikator / Skenario Pengelolaan": [
            "Pendapatan Bersih Penjualan Kayu (Rente Ekonomi)",
            "Potensi Jasa Lingkungan (Payment for Environmental Services/PES)",
            "SKENARIO BAU (Hanya Jual Kayu)",
            "SKENARIO OPTIMAL (Jati Lestari + Kredit Karbon)",
            "NILAI TAMBAH (Added Value Skenario Optimal)",
        ],
        "Nilai Valuasi Ekonomi (Tahunan)": [
            f"Rp {nilai_kayu_netto/1e9:,.2f} Miliar",
            f"Rp {nilai_karbon/1e9:,.2f} Miliar",
            f"Rp {skenario_bau/1e9:,.2f} Miliar",
            f"Rp {skenario_optimal/1e9:,.2f} Miliar",
            f"Rp {nilai_tambah/1e9:,.2f} Miliar",
        ]
    })

    st.dataframe(summary_df, use_container_width=True, hide_index=True)
    st.markdown("---")

    # =============================================
    # GRAFIK TRADE-OFF BAU VS OPTIMAL
    # =============================================
    col_chart, col_text = st.columns([1.5, 1])

    with col_chart:
        st.subheader("Grafik Analisis Trade-Off")
        tradeoff_chart = pd.DataFrame({
            "Skenario": ["Skenario BAU (Hanya Jati)", "Skenario Optimal (Jati + Karbon)"],
            "Nilai Valuasi (Miliar Rp)": [skenario_bau / 1e9, skenario_optimal / 1e9]
        })

        fig = px.bar(
            tradeoff_chart, x="Skenario", y="Nilai Valuasi (Miliar Rp)",
            color="Skenario", text="Nilai Valuasi (Miliar Rp)",
            color_discrete_map={
                "Skenario BAU (Hanya Jati)": "#ff9999",
                "Skenario Optimal (Jati + Karbon)": "#66b3ff"
            }
        )
        fig.update_traces(texttemplate="%{text:,.2f} M", textposition="outside", width=0.5)
        fig.update_layout(height=450, template="plotly_white", showlegend=False, yaxis_title="Miliar Rupiah (Rp)")
        st.plotly_chart(fig, use_container_width=True)

    with col_text:
        st.subheader("Kesimpulan Analisis")
        st.markdown(f"""
            <div class="desc-box" style="margin-top: 0;">
            <b>Interpretasi Valuasi Ekonomi:</b><br><br>
            Berdasarkan analisis kelayakan dan *trade-off* di atas, mempertahankan gaya manajemen <i>Business as Usual</i> (Skenario BAU) yang hanya berfokus pada ektraksi penjualan kayu jati akan menghasilkan Pendapatan Bersih (Rente) sekitar <b>Rp {skenario_bau/1e9:,.2f} Miliar/tahun</b>.<br><br>
            Namun, dengan mengintegrasikan nilai pembayaran jasa lingkungan (karbon) dalam <b>Skenario Optimal</b>, total nilai manfaat ekonomi dari kawasan KPH Randublatung akan melonjak drastis hingga <b>Rp {skenario_optimal/1e9:,.2f} Miliar/tahun</b>.<br><br>
            Terdapat insentif Nilai Tambah sebesar <b>Rp {nilai_tambah/1e9:,.2f} Miliar/tahun</b> yang sangat jelas membuktikan bahwa <b>pengelolaan hutan secara berkelanjutan dan partisipasi aktif dalam perdagangan karbon jauh lebih menguntungkan</b> dibandingkan sekadar menebang dan menjual kayunya.
            </div>
        """, unsafe_allow_html=True)