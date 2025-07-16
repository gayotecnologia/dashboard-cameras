import streamlit as st
import pandas as pd
from login import check_login  # <-- agora estamos importando a função corretamente

st.set_page_config(page_title="Status das Câmeras", layout="wide")

# Verifica login
if check_login():
    # Lê o CSV diretamente do repositório
    df = pd.read_csv("status_cameras.csv", sep=";")

    st.title("Dashboard de Câmeras")

    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Câmeras", len(df))
    col2.metric("Câmeras ON", df["Em Funcionamento"].str.lower().eq("sim").sum())
    col3.metric("Câmeras OFF", df["Em Funcionamento"].str.lower().eq("não").sum())
    col4.metric("Dias Médios de Gravação", f"{df['Dias de gravação'].mean():.1f}")

    st.subheader("Tabela Completa")
    st.dataframe(df, use_container_width=True)

else:
    st.stop()  # Encerra a execução se o login falhar
