import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# 1. SAYFA AYARLARI
st.set_page_config(page_title="Gaziantep İklim Terminali", layout="wide", initial_sidebar_state="collapsed")

# CSS: KARANLIK TEMA
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"] { background-color: #0e1117; }
    [data-testid="stHeader"] { background: rgba(0,0,0,0); }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px; }
    h1 { color: #e6edf3; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: -1px; }
    
    .warning-box {
        background-color: #1a0000;
        border: 2px solid #f85149;
        color: #ff7b72;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        font-weight: bold;
        margin-top: 30px;
        box-shadow: 0px 0px 20px rgba(248, 81, 73, 0.4);
    }
    .prof-note {
        color: #58a6ff;
        font-size: 20px;
        display: block;
        margin-top: 15px;
        font-style: italic;
        font-weight: normal;
        border-top: 1px solid #30363d;
        padding-top: 10px;
    }
    /* İndirme Butonu Stili */
    .stDownloadButton button {
        background-color: #238636;
        color: white;
        border: 1px solid #2ea043;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 GAZİANTEP YAĞIŞ TERMİNALİ (1975 - 2055)")

# 2. VERİ OLUŞTURMA
np.random.seed(42)
tum_yillar = np.arange(1975, 2056)
yagis_degerleri = 550 - (tum_yillar - 1975) * 5.5 + np.random.normal(0, 32, len(tum_yillar))
df = pd.DataFrame({'Yıl': tum_yillar, 'Yağış (mm)': yagis_degerleri.round(2)})

# 3. ANALİZ VE MODEL
X_gecmis = tum_yillar[:51].reshape(-1, 1)
y_gecmis = yagis_degerleri[:51]
model = LinearRegression().fit(X_gecmis, y_gecmis)
r2_score = model.score(X_gecmis, y_gecmis)
trend_butun_grafik = model.predict(tum_yillar.reshape(-1, 1))

# İstatistiksel Kıyaslama (YENİ ÖZELLİK)
ilk_5_yil_ort = df['Yağış (mm)'].head(5).mean()
son_5_yil_ort = df['Yağış (mm)'].tail(5).mean()
degisim = son_5_yil_ort - ilk_5_yil_ort

# 4. GRAFİK
fig = go.Figure()

# Mavi (Geçmiş)
fig.add_trace(go.Scatter(
    x=df['Yıl'][:51], y=df['Yağış (mm)'][:51], name='GERÇEKLEŞEN',
    line=dict(color='#58a6ff', width=2), fill='tozeroy', fillcolor='rgba(88, 166, 255, 0.1)'
))

# Turuncu (Tahmin)
fig.add_trace(go.Scatter(
    x=df['Yıl'][51:], y=df['Yağış (mm)'][51:], name='AI ÖNGÖRÜSÜ',
    line=dict(color='#ffa657', width=3)
))

# Kırmızı Trend (Boydan Boya)
fig.add_trace(go.Scatter(
    x=tum_yillar, y=trend_butun_grafik, name='GENEL TREND',
    line=dict(color='#f85149', width=2, dash='dash'), hoverinfo='skip'
))

# LAYOUT: Yılları tek tek gösterme (Dik yazarak)
fig.update_layout(
    template="plotly_dark", hovermode="x unified", paper_bgcolor='#0e1117', plot_bgcolor='#0e1117',
    margin=dict(l=0, r=0, t=30, b=0), height=600,
    xaxis=dict(
        showgrid=True, gridcolor='#30363d',
        rangeslider=dict(visible=True, thickness=0.04),
        tickmode='linear', tick0=1975, dtick=1, tickangle=-90 # Her yılı dik yaz
    ),
    yaxis=dict(showgrid=True, gridcolor='#30363d', side="right"),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)

st.plotly_chart(fig, use_container_width=True)

# 5. METRİKLER (GÜNCELLENDİ)
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("GÜVEN SKORU (R²)", f"{r2_score:.4f}")
with c2: st.metric("1975-1980 ORT.", f"{ilk_5_yil_ort:.0f} mm")
with c3: st.metric("2050-2055 ORT.", f"{son_5_yil_ort:.0f} mm")
with c4: st.metric("TOPLAM SU KAYBI", f"{degisim:.0f} mm", delta=f"{degisim:.0f} mm", delta_color="inverse")

# 6. TABLO VE İNDİRME BUTONU (YENİ)
st.markdown("### 📋 YILLIK VERİ TAKİP LİSTESİ")

# CSV İndirme İşlemi
csv = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 BU VERİ SETİNİ EXCEL/CSV OLARAK İNDİR",
    data=csv,
    file_name='gaziantep_iklim_projeksiyonu.csv',
    mime='text/csv',
)

def renklendir(val):
    return f'color: {"#f85149" if val < 300 else "#3fb950"}; font-weight: bold'

st.dataframe(df.sort_values(by='Yıl', ascending=False).style.applymap(renklendir, subset=['Yağış (mm)']), use_container_width=True, height=400)

# 7. HOCA NOTU
st.markdown("""
    <div class="warning-box">
        ⚠️ YASAL UYARI: BU TERMİNALDEKİ VERİLER SİMÜLASYONDUR. 
        GERÇEK METEOROLOJİK KAYITLARI YANSITMAZ.<br>
        <span class="prof-note">
            📝 Bu çalışma sadece bir prototiptir; siz değerli hocalarımızın yönlendirmesi ile son halini alacaktır.
        </span>
    </div>
    """, unsafe_allow_html=True)