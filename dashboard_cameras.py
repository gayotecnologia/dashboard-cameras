import streamlit as st
import pandas as pd
from login import check_login

# Verificação de login
if not check_login():
    st.stop()
from PIL import Image

logo = Image.open("logo.jpeg")
st.image(logo, width=70)  # Ajuste o tamanho como preferir

# Título
st.markdown(
    "<h3 style='text-align: left; color: black;'>📹 Dashboard de Status câmeras - Atem Belém</h3>",
 unsafe_allow_html=True
)


# Leitura segura do CSV diretamente do repositório local
try:
    df = pd.read_csv("status_cameras.csv", sep="\t", encoding="utf-8")
    df.columns = df.columns.str.strip()  # remove espaços nas colunas

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

# Limpar e padronizar
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.strip().str.lower()
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.strip().str.lower()

# Filtros
with st.sidebar:
    st.header("🔎 Filtros")
    modelos = st.multiselect("Modelo da Câmera", df["Modelo"].unique(), default=df["Modelo"].unique())
    status = st.multiselect("Status de Funcionamento", ["sim", "não"], default=["sim", "não"])

df_filtrado = df[
    df["Modelo"].isin(modelos) & df["Em Funcionamento"].isin(status)
]

# Métricas
total_cameras = len(df_filtrado)
cameras_on = df_filtrado["Em Funcionamento"].eq("sim").sum()
cameras_off = df_filtrado["Em Funcionamento"].eq("não").sum()
cameras_gravando = df_filtrado["Gravando em Disco"].eq("sim").sum()

# Porcentagem de câmeras ON
percent_on = (cameras_on / total_cameras) * 100 if total_cameras > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Câmeras", total_cameras)
col2.metric("Câmeras ON", cameras_on, f"{percent_on:.1f}%")
col3.metric("Câmeras OFF", cameras_off)
col4.metric("Câmeras Gravando", cameras_gravando)


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
