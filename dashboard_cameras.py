import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login

# Verifica login
if not check_login():
    st.stop()

# ========== LOGO CENTRALIZADA ==========
try:
    logo = Image.open("logo.jpeg")
    st.markdown("<div style='text-align: center;'><img src='data:image/jpeg;base64," +
                st.image(logo, use_column_width=False, width=80, output_format="JPEG").data +
                "' style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)
except Exception:
    st.warning("⚠️ Não foi possível carregar a logo. Verifique o nome e caminho.")

# ========== TÍTULO ==========
st.markdown("<h2 style='text-align: center;'>📊 Dashboard de Status das Câmeras</h2>", unsafe_allow_html=True)

# ========== LEITURA DO CSV ==========
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

# ========== LIMPEZA ==========
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.strip().str.lower()
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.strip().str.lower()

# ========== MÉTRICAS ==========
total = len(df)
online = df["Em Funcionamento"].eq("sim").sum()
offline = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].eq("sim").sum()
percent_online = (online / total * 100) if total else 0

# ========== CARTÕES COM ÍCONES ==========
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("🎯 Total", total)
col2.metric("✅ Online", online)
col3.metric("❌ Offline", offline)
col4.metric("💾 Gravando", gravando)
col5.metric("📶 % Online", f"{percent_online:.1f}%")

# ========== FILTROS ==========
with st.expander("🔍 Filtros"):
    modelos = st.multiselect("Modelo", options=df["Modelo"].unique(), default=df["Modelo"].unique())
    status_funcionamento = st.multiselect("Status de Funcionamento", ["sim", "não"], default=["sim", "não"])
    df_filtrado = df[
        (df["Modelo"].isin(modelos)) &
        (df["Em Funcionamento"].isin(status_funcionamento))
    ]

# ========== TABELA ==========
st.subheader("📋 Tabela de Câmeras")
st.dataframe(df_filtrado, use_container_width=True)

# ========== GRÁFICOS ==========
st.subheader("📊 Distribuição por Modelo")
st.bar_chart(df_filtrado["Modelo"].value_counts())

st.subheader("📈 FPS por Câmera")
st.line_chart(df_filtrado[["Nome", "FPS"]].set_index("Nome"))

st.subheader("🗓️ Dias de Gravação por Câmera")
st.bar_chart(df_filtrado[["Nome", "Dias de gravação"]].set_index("Nome"))
