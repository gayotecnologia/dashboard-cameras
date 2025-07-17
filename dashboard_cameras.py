import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login

# Verificar login
if not check_login():
    st.stop()

# Exibir logo centralizada
try:
    logo = Image.open("logo.jpg")  # Altere para logo.png ou logo.jpeg se necessário
    col_logo = st.columns([1, 2, 1])
    with col_logo[1]:
        st.image(logo, use_column_width=False, width=200)
except Exception as e:
    st.warning("⚠️ Logo não foi carregada. Verifique o nome do arquivo e extensão.")

# Título centralizado
st.markdown("<h3 style='text-align: center;'>📊 Dashboard de Status das Câmeras</h3>", unsafe_allow_html=True)

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

# Padronizar dados
df["Em Funcionamento"] = df["Em Funcionamento"].astype(str).str.lower().str.strip()
df["Gravando em Disco"] = df["Gravando em Disco"].astype(str).str.lower().str.strip()

# Métricas com ícones
total = len(df)
on = df["Em Funcionamento"].eq("sim").sum()
off = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].eq("sim").sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Total", total)
col2.metric("✅ Online", on, f"{(on/total)*100:.1f}%", delta_color="normal")
col3.metric("❌ Offline", off)
col4.metric("💾 Gravando", gravando)

# Filtros interativos (opcional)
with st.expander("🔎 Filtros"):
    modelos = st.multiselect("Modelo", options=df["Modelo"].unique(), default=df["Modelo"].unique())
    funcionando = st.multiselect("Status", options=["sim", "não"], default=["sim", "não"])

    df_filtrado = df[
        (df["Modelo"].isin(modelos)) &
        (df["Em Funcionamento"].isin(funcionando))
    ]

# Tabela
st.subheader("📋 Tabela Completa")
st.dataframe(df_filtrado, use_container_width=True)

# Gráficos
st.subheader("📊 Distribuição por Modelo")
st.bar_chart(df_filtrado["Modelo"].value_counts())

st.subheader("📈 FPS por Câmera")
st.line_chart(df_filtrado[["Nome", "FPS"]].set_index("Nome"))

st.subheader("🗓️ Dias de Gravação")
st.bar_chart(df_filtrado[["Nome", "Dias de gravação"]].set_index("Nome"))
