import streamlit as st
import pandas as pd
import os
from login import check_login
import io

st.set_page_config(page_title="Dashboard de Câmeras", layout="wide")

if not check_login():
    st.stop()

# Carregar dados
csv_path = "status_cameras.csv"
if not os.path.exists(csv_path):
    st.error("Arquivo 'status_cameras.csv' não encontrado.")
    st.stop()

dados = pd.read_csv(csv_path)

# Menu lateral
menu = st.sidebar.selectbox("📋 Menu", ["Status das Câmeras", "Relatório", "Gráficos"])

if menu == "Status das Câmeras":
    st.title("📡 Status das Câmeras")
    status_selecionado = st.multiselect(
        "Filtrar por status",
        options=dados["Status"].unique(),
        default=dados["Status"].unique()
    )
    dados_filtrados = dados[dados["Status"].isin(status_selecionado)]

    total_cameras = dados_filtrados.shape[0]
    online_count = dados_filtrados[dados_filtrados["Status"] == "Online"].shape[0]
    offline_count = dados_filtrados[dados_filtrados["Status"] == "Offline"].shape[0]

