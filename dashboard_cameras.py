import streamlit as st
import pandas as pd
from login import check_login

st.set_page_config(page_title="Status das Câmeras", layout="wide")

if check_login():
    try:
        # Tenta carregar o CSV
        df = pd.read_csv("status_cameras.csv", sep=";", encoding="utf-8")
    except:
        df = pd.read_csv("status_cameras.csv", sep=";", encoding="latin1")

    df.columns = df.columns.str.strip()  # Remove espaços nos nomes das colunas

    # Para debug: mostrar os nomes das colunas encontrados
    st.write("Colunas encontradas:", df.columns.tolist())

    st.title("Dashboard de Câmeras")

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total de Câmeras", len(df))

    if "Em Funcionamento" in df.columns:
        col2.metric("Câmeras ON", df["Em Funcionamento"].str.lower().eq("sim").sum())
        col3.metric("Câmeras OFF", df["Em Funcionamento"].str.lower().eq("não").sum())
    else:
        col2.warning("Coluna 'Em Funcionamento' não encontrada.")
        col3.warning("Coluna 'Em Funcionamento' não encontrada.")

    if "Dias de gravação" in df.columns:
        col4.metric("Dias Médios de Gravação", f"{df['Dias de gravação'].mean():.1f}")
    else:
        col4.warning("Coluna 'Dias de gravação' não encontrada.")

    st.subheader("Tabela Completa")
    st.dataframe(df, use_container_width=True)

else:
    st.stop()
