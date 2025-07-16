import streamlit as st
import pandas as pd
import plotly.express as px
import re
import os
import login  # importa usuário e senha

st.set_page_config(layout="wide")
st.title("📷 Dashboard de Câmeras - Digifort")

# --- LOGIN ---
with st.sidebar:
    st.header("🔐 Acesso Restrito")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if usuario == login.USUARIO_CORRETO and senha == login.SENHA_CORRETA:
        st.success("Acesso liberado")
        acesso_liberado = True
    else:
        st.warning("Insira credenciais válidas")
        acesso_liberado = False

if acesso_liberado:
    # --- CARREGA CSV LOCAL ---
    caminho_csv = "./status_cameras.csv"
    if not os.path.exists(caminho_csv):
        st.error("Arquivo CSV 'status_cameras.csv' não encontrado.")
    else:
        try:
            df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8')
            df.columns = df.columns.str.strip()

            df["Em Funcionamento"] = df["Em Funcionamento"].str.lower() == "sim"
            df["Gravando em Disco"] = df["Gravando em Disco"].str.lower() == "sim"
            df["Ativado"] = df["Ativado"].str.lower() == "sim"
            df["FPS"] = pd.to_numeric(df["FPS"], errors="coerce")

            def converter_disco(valor):
                if isinstance(valor, str):
                    valor = valor.strip().lower()
                    if "tb" in valor:
                        return float(re.search(r"[\d.,]+", valor).group().replace(",", ".")) * 1
                    elif "gb" in valor:
                        return float(re.search(r"[\d.,]+", valor).group().replace(",", ".")) / 1024
                return 0

            df["Disco (TB)"] = df["Disco Utilizado"].apply(converter_disco)
            df["Dias"] = df["Dias de gravação"].str.extract(r"(\d+)").astype(float)

            # Filtros
            st.sidebar.subheader("Filtros")
            modelos_selecionados = st.sidebar.multiselect("Filtrar por modelo", options=df["Modelo"].unique(), default=df["Modelo"].unique())
            df_filtrado = df[df["Modelo"].isin(modelos_selecionados)]

            # Métricas
            total_cameras = len(df_filtrado)
            cameras_online = df_filtrado["Em Funcionamento"].sum()
            cameras_offline = total_cameras - cameras_online
            fps_medio = df_filtrado["FPS"].mean()
            dias_gravacao_medio = df_filtrado["Dias"].mean()
            disco_total_tb = df_filtrado["Disco (TB)"].sum()

            col1, col2, col3, col4, col5, col6 = st.columns(6)
            col1.metric("📸 Total de Câmeras", total_cameras)
            col2.metric("🟢 Online", cameras_online)
            col3.metric("🔴 Offline", cameras_offline)
            col4.metric("🎞️ FPS Médio", f"{fps_medio:.1f}")
            col5.metric("🗓️ Dias Gravando (média)", f"{dias_gravacao_medio:.1f}")
            col6.metric("💾 Disco Total (TB)", f"{disco_total_tb:.2f}")

            st.markdown("---")

            st.subheader("Distribuição por Modelo de Câmera")
            grafico_modelo = df_filtrado["Modelo"].value_counts().reset_index()
            grafico_modelo.columns = ["Modelo", "Quantidade"]
            fig1 = px.bar(grafico_modelo, x="Modelo", y="Quantidade", title="Quantidade por Modelo", text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)

            st.subheader("Status das Câmeras")
            status = {"Online": cameras_online, "Offline": cameras_offline}
            fig2 = px.pie(names=list(status.keys()), values=list(status.values()), title="Status das Câmeras")
            st.plotly_chart(fig2, use_container_width=True)

            st.subheader("📋 Tabela de Câmeras")
            st.dataframe(df_filtrado.drop(columns=["Disco Utilizado"]), use_container_width=True)

        except Exception as e:
            st.error(f"Erro ao processar os dados: {e}")
else:
    st.info("Insira seu usuário e senha na barra lateral.")
