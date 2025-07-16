import streamlit as st
import pandas as pd
from login import check_login

# Verifica login
if not check_login():
    st.stop()

# Título do dashboard
st.title("📹 Dashboard de Câmeras - Digifort")

# Carrega os dados diretamente do arquivo no repositório
CSV_PATH = "status_cameras.csv"

try:
    df = pd.read_csv(CSV_PATH, sep=";", encoding="utf-8")
    st.write("🧾 Colunas encontradas no CSV:")
    st.write(df.columns.tolist())
except Exception as e:
    st.error(f"Erro ao carregar o CSV: {e}")
    st.stop()


# Corrige nomes de colunas com espaços extras
df.columns = df.columns.str.strip()

# Converte colunas específicas para tratamento
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.strip().str.lower()
df["Modelo"] = df["Modelo"].astype(str).str.strip()
df["FPS"] = pd.to_numeric(df["FPS"], errors="coerce")
df["Dias de gravação"] = pd.to_numeric(df["Dias de gravação"], errors="coerce")
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.strip().str.lower()

# Filtros
with st.sidebar:
    st.header("🎛️ Filtros")
    status = st.multiselect("Status de Funcionamento", ["sim", "não"], default=["sim", "não"])
    modelos = st.multiselect("Modelo da Câmera", sorted(df["Modelo"].unique()))
    min_fps, max_fps = int(df["FPS"].min()), int(df["FPS"].max())
    fps_range = st.slider("FPS", min_value=min_fps, max_value=max_fps, value=(min_fps, max_fps))

# Aplica filtros
filtro = (
    df["Em Funcionamento"].isin(status) &
    df["FPS"].between(fps_range[0], fps_range[1])
)
if modelos:
    filtro &= df["Modelo"].isin(modelos)

df_filtrado = df[filtro]

# Métricas no topo
col1, col2, col3 = st.columns(3)
col1.metric("Total de Câmeras", len(df_filtrado))
col2.metric("Câmeras ON", (df_filtrado["Em Funcionamento"] == "sim").sum())
col3.metric("Câmeras Gravando", (df_filtrado["Gravando em Disco"] == "sim").sum())

# Exibe a tabela
st.markdown("### 📋 Tabela de Câmeras")
st.dataframe(df_filtrado, use_container_width=True)
