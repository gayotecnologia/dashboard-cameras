import streamlit as st
import pandas as pd
from login import check_login

# Autenticação
if not check_login():
    st.stop()

# Título
st.title("📹 Dashboard de Status das Câmeras")

# Leitura segura do CSV com diagnóstico
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

# Limpar e padronizar
df["Em Funcionamento"] = df["Em Funcionamento"].str.lower().fillna("")

# Métricas
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total de Câmeras", len(df))
col2.metric("Câmeras ON", df["Em Funcionamento"].eq("sim").sum())
col3.metric("Câmeras OFF", df["Em Funcionamento"].eq("não").sum())
col4.metric("Câmeras Gravando", df["Gravando em Disco"].str.lower().eq("sim").sum())

# Exibir tabela
st.subheader("📋 Tabela Completa")
st.dataframe(df)

# Gráficos
st.subheader("📊 Distribuição por Modelo")
modelo_counts = df["Modelo"].value_counts()
st.bar_chart(modelo_counts)

st.subheader("📈 FPS por câmera")
st.line_chart(df[["Nome", "FPS"]].set_index("Nome"))

st.subheader("💾 Dias de Gravação")
st.bar_chart(df[["Nome", "Dias de gravação"]].set_index("Nome"))
