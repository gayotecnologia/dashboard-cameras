import pandas as pd
import streamlit as st
import plotly.express as px

# Carregar CSV
arquivo_csv = "cameras.csv"
df = pd.read_csv(arquivo_csv)

# Renomear colunas
df.rename(columns={
    "Em Funcionamento": "Status",
    "Dias de gravação": "DiasGravacao",
    "Gravando em Disco": "Gravando",
    "Disco Utilizado": "Disco"
}, inplace=True)

# Título
st.title("📡 Dashboard de Câmeras - Gayo Tecnologia")

# Métricas principais
qtd_cameras_total = len(df)
qtd_cameras_online = len(df[df["Status"] == "Sim"])
qtd_cameras_offline = qtd_cameras_total - qtd_cameras_online

dias_gravacao_medio = df["DiasGravacao"].mean()
fps_medio = df["FPS"].mean()
uso_total_disco = df["Disco"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total de Câmeras", qtd_cameras_total)
col2.metric("Online", qtd_cameras_online)
col3.metric("Offline", qtd_cameras_offline)

col4, col5, col6 = st.columns(3)
col4.metric("Dias Médios de Gravação", f"{dias_gravacao_medio:.1f}")
col5.metric("FPS Médio", f"{fps_medio:.1f}")
col6.metric("Uso Total de Disco (GB)", f"{uso_total_disco:.1f}")

# Gráfico de pizza: status
st.subheader("📊 Status das Câmeras")
status_counts = df["Status"].value_counts()
fig_status = px.pie(names=status_counts.index, values=status_counts.values, title="Câmeras Online x Offline")
st.plotly_chart(fig_status)

# Gráfico de barras: câmeras por modelo
st.subheader("📊 Câmeras por Modelo")
model_counts = df["Modelo"].value_counts().reset_index()
model_counts.columns = ["Modelo", "Quantidade"]
fig_modelos = px.bar(model_counts, x="Modelo", y="Quantidade", title="Quantidade por Modelo", text_auto=True)
st.plotly_chart(fig_modelos)

# Filtro de status
st.subheader("📋 Tabela de Câmeras")
status_filtro = st.selectbox("Filtrar por status", ["Todos", "Online", "Offline"])
if status_filtro == "Online":
    df_filtrado = df[df["Status"] == "Sim"]
elif status_filtro == "Offline":
    df_filtrado = df[df["Status"] != "Sim"]
else:
    df_filtrado = df

# Ordenar por uso de disco
df_filtrado = df_filtrado.sort_values(by="Disco", ascending=False)

# Mostrar tabela
st.dataframe(df_filtrado)

# Exportar
st.download_button("📥 Baixar dados filtrados", df_filtrado.to_csv(index=False), file_name="cameras_filtrado.csv")
