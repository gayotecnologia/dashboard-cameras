import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Dashboard de Câmeras", layout="wide")

st.title("📡 Dashboard de Câmeras IP")
st.write("Visualização em tempo real dos status das câmeras monitoradas")

csv_path = "status_cameras.csv"

# Verificar se o arquivo existe
if not os.path.exists(csv_path):
    st.error("Arquivo 'status_cameras.csv' não encontrado. Verifique o caminho.")
    st.stop()

# Carregar os dados
dados = pd.read_csv(csv_path)

# Filtro por status
status_selecionado = st.multiselect(
    "Filtrar por status",
    options=dados["Status"].unique(),
    default=dados["Status"].unique()
)

dados_filtrados = dados[dados["Status"].isin(status_selecionado)]

# Métricas
col1, col2 = st.columns(2)
col1.metric("Câmeras Online", dados_filtrados[dados_filtrados["Status"] == "Online"].shape[0])
col2.metric("Câmeras Offline", dados_filtrados[dados_filtrados["Status"] == "Offline"].shape[0])

# Tabela
st.dataframe(dados_filtrados, use_container_width=True)