import streamlit as st
import pandas as pd
from PIL import Image

# Centraliza a logo com tamanho reduzido
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    image = Image.open("logo.jpeg")
    st.image(image, width=100)

# Título
st.markdown("<h2 style='text-align: center;'>📹 Dashboard de Status das Câmeras</h2>", unsafe_allow_html=True)

# Leitura do CSV
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

# Normalizar campos
df["Em Funcionamento"] = df["Em Funcionamento"].str.lower().fillna("").str.strip()
df["Gravando em Disco"] = df["Gravando em Disco"].str.lower().fillna("").str.strip()

# Métricas principais
total = len(df)
on = df["Em Funcionamento"].eq("sim").sum()
off = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].eq("sim").sum()
percentual_on = (on / total * 100) if total > 0 else 0

# Cartões
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🎥 Total", total)
col2.metric("✅ ON", on)
col3.metric("❌ OFF", off)
col4.metric("💾 Gravando", gravando)
col5.metric("📊 % ON", f"{percentual_on:.1f}%")

# Tabela com filtro por status
st.subheader("📋 Tabela de Câmeras")
opcao_filtro = st.selectbox("Filtrar por funcionamento:", ["Todos", "Somente ON", "Somente OFF"])
if opcao_filtro == "Somente ON":
    df_filtrado = df[df["Em Funcionamento"] == "sim"]
elif opcao_filtro == "Somente OFF":
    df_filtrado = df[df["Em Funcionamento"] == "não"]
else:
    df_filtrado = df
st.dataframe(df_filtrado, use_container_width=True)

# Gráfico: Distribuição por Modelo
st.subheader("📦 Distribuição por Modelo")
st.bar_chart(df["Modelo"].value_counts())

# Gráfico: FPS por Câmera
st.subheader("📈 FPS por Câmera")
st.line_chart(df[["Nome", "FPS"]].set_index("Nome"))

# Gráfico: Dias de Gravação por Câmera
st.subheader("📊 Dias de Gravação por Câmera")
st.bar_chart(df[["Nome", "Dias de gravação"]].set_index("Nome"))
