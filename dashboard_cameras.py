from PIL import Image
import streamlit as st
import pandas as pd
from login import check_login

if not check_login():
    st.stop()

# 📌 Centralizar a logo
st.markdown(
    """
    <div style="text-align: center;">
        <img src="logo.jpeg" alt="Logo" width="80">
    </div>
    """,
    unsafe_allow_html=True
)

# 📌 Título centralizado
st.markdown(
    "<h3 style='text-align: center; color: black;'>📹 Dashboard de Status câmeras - Atem Belém</h3>",
    unsafe_allow_html=True
)

# 🔁 Leitura do CSV
df = pd.read_csv("status_cameras.csv", sep="\t", encoding="utf-8")

# ✅ Padronizar colunas
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.strip().str.lower()
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.strip().str.lower()

# 📊 Métricas
total = len(df)
on = df["Em Funcionamento"].eq("sim").sum()
off = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].eq("sim").sum()
porcentagem_on = (on / total) * 100 if total > 0 else 0

# 🎨 Estilo das métricas como cartões lado a lado
st.markdown("""
<style>
.metric-card {
    background-color: #f1f3f6;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 1px 1px 10px rgba(0,0,0,0.1);
    margin: 10px;
}
.metric-title {
    font-size: 18px;
    font-weight: 600;
    color: #333;
}
.metric-value {
    font-size: 28px;
    font-weight: bold;
    color: #0078D4;
}
</style>
""", unsafe_allow_html=True)

# 🔲 Layout com 4 colunas
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Total de Câmeras</div>
        <div class='metric-value'>{total}</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Câmeras ON</div>
        <div class='metric-value'>{on} ({porcentagem_on:.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Câmeras OFF</div>
        <div class='metric-value'>{off}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class='metric-card'>
        <div class='metric-title'>Gravando em Disco</div>
        <div class='metric-value'>{gravando}</div>
    </div>
    """, unsafe_allow_html=True)



# Exibir tabela
st.subheader("📋 Tabela Completa")
st.dataframe(df_filtrado, use_container_width=True)

# Gráficos
st.subheader("📊 Distribuição por Modelo")
st.bar_chart(df_filtrado["Modelo"].value_counts())

st.subheader("📈 FPS por câmera")
fps_chart = df_filtrado[["Nome", "FPS"]].dropna().set_index("Nome")
st.line_chart(fps_chart)

st.subheader("💾 Dias de Gravação")
dias_chart = df_filtrado[["Nome", "Dias de gravação"]].dropna().set_index("Nome")
st.bar_chart(dias_chart)
