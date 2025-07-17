import streamlit as st
import pandas as pd
from login import check_login

# Verifica login
if not check_login():
    st.stop()

# ===== TOPO COM LOGO E TÍTULO =====
col_logo = st.columns([1, 2, 1])
with col_logo[1]:
    st.image("logo.jpg", width=80)  # ajuste o nome conforme sua imagem
st.markdown("<h3 style='text-align: center;'>Dashboard de Status das Câmeras</h3>", unsafe_allow_html=True)

# ===== LEITURA DO CSV =====
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

# Padronização de texto
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.strip().str.lower()
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.strip().str.lower()

# ===== FILTROS =====
st.sidebar.header("🔍 Filtros")
modelos = st.sidebar.multiselect("Modelo da Câmera", options=df["Modelo"].unique(), default=df["Modelo"].unique())
status = st.sidebar.multiselect("Em Funcionamento", options=["sim", "não"], default=["sim", "não"])
gravando = st.sidebar.multiselect("Gravando em Disco", options=["sim", "não"], default=["sim", "não"])

df_filtrado = df[
    df["Modelo"].isin(modelos) &
    df["Em Funcionamento"].isin(status) &
    df["Gravando em Disco"].isin(gravando)
]

# ===== MÉTRICAS =====
total = len(df_filtrado)
on = df_filtrado["Em Funcionamento"].eq("sim").sum()
off = df_filtrado["Em Funcionamento"].eq("não").sum()
gravando = df_filtrado["Gravando em Disco"].eq("sim").sum()
percent_on = (on / total * 100) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Câmeras", total)
col2.metric("Câmeras ON", on, f"{percent_on:.1f}%")
col3.metric("Câmeras OFF", off)
col4.metric("Câmeras Gravando", gravando)

# ===== TABELA =====
st.subheader("📋 Tabela de Câmeras")
st.dataframe(df_filtrado, use_container_width=True)

# ===== GRÁFICOS =====
st.subheader("📊 Distribuição por Modelo")
st.bar_chart(df_filtrado["Modelo"].value_counts())

st.subheader("📈 FPS por Câmera")
st.line_chart(df_filtrado[["Nome", "FPS"]].set_index("Nome"))

st.subheader("💾 Dias de Gravação por Câmera")
st.bar_chart(df_filtrado[["Nome", "Dias de gravação"]].set_index("Nome"))
