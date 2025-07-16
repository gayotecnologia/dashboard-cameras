import streamlit as st
import pandas as pd
import os
from login import check_login
import plotly.express as px

# Configuração da página
st.set_page_config(page_title="Dashboard de Câmeras", layout="wide")

# Autenticação
if not check_login():
    st.stop()

# Carregar dados do CSV
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
    online_percent = (online_count / total_cameras * 100) if total_cameras > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Câmeras Online", online_count)
    col2.metric("Câmeras Offline", offline_count)
    col3.metric("Porcentagem Online", f"{online_percent:.2f}%")

    st.dataframe(dados_filtrados, use_container_width=True)

elif menu == "Relatório":
    st.title("📄 Exportar Relatório")
    st.write("Clique abaixo para exportar o status das câmeras:")
    st.download_button(
        label="📥 Exportar CSV",
        data=dados.to_csv(index=False).encode("utf-8"),
        file_name="relatorio_cameras.csv",
        mime="text/csv"
    )

elif menu == "Gráficos":
    st.title("📊 Análises Visuais das Câmeras")

    # Gráfico de status
    status_count = dados["Status"].value_counts().reset_index()
    status_count.columns = ["Status", "Quantidade"]
    fig_status = px.bar(
        status_count,
        x="Status",
        y="Quantidade",
        color="Status",
        color_discrete_map={"Online": "green", "Offline": "red"},
        title="Quantidade de Câmeras por Status",
        text="Quantidade"
    )
    st.plotly_chart(fig_status, use_container_width=True)

    # Gráfico de FPS por modelo
    st.subheader("📈 Média de FPS por Modelo de Câmera")
    fps_media = dados.groupby("Modelo")["FPS"].mean().reset_index().sort_values(by="FPS")
    fig_fps = px.bar(
        fps_media,
        x="Modelo",
        y="FPS",
        color="FPS",
        color_continuous_scale="Blues",
        title="Média de FPS por Modelo"
    )
    st.plotly_chart(fig_fps, use_container_width=True)
