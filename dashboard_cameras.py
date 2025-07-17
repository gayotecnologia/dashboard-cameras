import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login

# Verificação de login
if not check_login():
    st.stop()

# === LOGO CENTRALIZADA ===
try:
    logo = Image.open("logo.jpeg")
    col_logo = st.columns([1, 2, 1])
    with col_logo[1]:
        st.image(logo, width=80)
except Exception as e:
    st.warning("⚠️ Logo não carregada. Verifique o nome e o caminho do arquivo.")

# === TÍTULO CENTRALIZADO ===
st.markdown("<h3 style='text-align: center;'>📊 Dashboard de Status das Câmeras</h3>", unsafe_allow_html=True)

# === LEITURA DO CSV ===
try:
    df = pd.read_csv("status_cameras.csv", sep="\t", encoding="utf-8")

    colunas_esperadas = [
        "Nome", "Em Funcionamento", "Endereço", "Descrição",
        "Ativado", "Modelo", "Dias de gravação", "Gravando em Disco", "FPS", "Disco Utilizado"
    ]
    if not all(col in df.columns for col in colunas_esperadas):
        st.error("❌ O CSV não possui todas as colunas esperadas.")
        st.write("Colunas encontradas:", df.columns.tolist())
        st.stop()

except Exception as e:
    st.error(f"Erro ao carregar o CSV: {e}")
    st.stop()

# === PADRONIZAÇÃO ===
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.lower().str.strip()
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.lower().str.strip()

# === MÉTRICAS ===
total = len(df)
online = df["Em Funcionamento"].eq("sim").sum()
offline = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].eq("sim").sum()
percent_online = (online / total) * 100 if total else 0

# === CARTÕES ===
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("### 🎯 Total")
    st.metric(label="", value=total)

with col2:
    st.markdown("### ✅ Online")
    st.metric(label="", value=online)

with col3:
    st.markdown("### ❌ Offline")
    st.metric(label="", value=offline)

with col4:
    st.markdown("### 💾 Gravando")
    st.metric(label="", value=gravando)

with col5:
    st.markdown("### 📶 % Online")
    st.metric(label="", value=f"{percent_online:.1f}%")

# === FILTROS ===
with st.expander("🔎 Filtros"):
    modelos = st.multiselect("Modelo", options=df["Modelo"].unique(), default=df["Modelo"].unique())
    status_funcionamento = st.multiselect("Status de Funcionamento", ["sim", "não"], default=["sim", "não"])
    df_filtrado = df[
        (df["Modelo"].isin(modelos)) &
        (df["Em Funcionamento"].isin(status_funcionamento))
    ]

# === TABELA ===
st.subheader("📋 Tabela Completa")
st.dataframe(df_filtrado, use_container_width=True)

# === GRÁFICOS ===
st.subheader("📊 Distribuição por Modelo")
st.bar_chart(df_filtrado["Modelo"].value_counts())

st.subheader("📈 FPS por Câmera")
st.line_chart(df_filtrado[["Nome", "FPS"]].set_index("Nome"))

st.subheader("🗓️ Dias de Gravação")
st.bar_chart(df_filtrado[["Nome", "Dias de gravação"]].set_index("Nome"))
