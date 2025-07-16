import streamlit as st
import pandas as pd
from login import check_login

st.set_page_config(page_title="📹 Status das Câmeras", layout="wide")

# Login
if not check_login():
    st.stop()

# Tenta carregar o CSV corretamente
@st.cache_data
def carregar_csv():
    try:
        df = pd.read_csv("status_cameras.csv", sep=";", encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv("status_cameras.csv", sep=";", encoding="latin1")
    df.columns = df.columns.str.strip()  # Remove espaços extras nos nomes das colunas
    return df

df = carregar_csv()

# Validação básica
colunas_esperadas = [
    "Nome", "Em Funcionamento", "Endereço", "Descrição",
    "Ativado", "Modelo", "Dias de gravação",
    "Gravando em Disco", "FPS", "Disco Utilizado"
]

# Checa se todas as colunas estão no DataFrame
if not all(col in df.columns for col in colunas_esperadas):
    st.error("⚠️ O CSV não possui todas as colunas esperadas. Verifique o arquivo.")
    st.write("Colunas encontradas:", df.columns.tolist())
    st.stop()

# Título
st.title("📊 Dashboard de Câmeras - Digifort")

# Métricas principais
col1, col2, col3, col4 = st.columns(4)

col1.metric("🎥 Total de Câmeras", len(df))
col2.metric("✅ Câmeras ON", df["Em Funcionamento"].str.lower().eq("sim").sum())
col3.metric("❌ Câmeras OFF", df["Em Funcionamento"].str.lower().eq("não").sum())
col4.metric("📼 Dias médios de gravação", f"{df['Dias de gravação'].mean():.1f}")

# Filtro por modelo e status
with st.expander("🔍 Filtros"):
    modelos = df["Modelo"].dropna().unique().tolist()
    modelo_filtro = st.multiselect("Modelo da câmera", modelos, default=modelos)

    status_filtro = st.selectbox("Status da câmera", ["Todas", "ON", "OFF"])

# Aplica filtros
df_filtrado = df[df["Modelo"].isin(modelo_filtro)]

if status_filtro == "ON":
    df_filtrado = df_filtrado[df_filtrado["Em Funcionamento"].str.lower() == "sim"]
elif status_filtro == "OFF":
    df_filtrado = df_filtrado[df_filtrado["Em Funcionamento"].str.lower() == "não"]

# Exibe a tabela
st.subheader("📋 Tabela de Câmeras")
st.dataframe(df_filtrado, use_container_width=True)

# Rodapé opcional
st.caption("Desenvolvido por Romilson 💡 | Powered by Streamlit")
