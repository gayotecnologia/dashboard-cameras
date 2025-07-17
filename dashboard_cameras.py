import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login

# Checa login antes de qualquer coisa
check_login()

# Configura a página para ser responsiva
st.set_page_config(layout="wide")

# Carrega imagens das logos
logo_esquerda = Image.open("logo.jpeg")
logo_direita = Image.open("atem.png")

# Exibe as logos de forma responsiva
st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px 0;'>
        <img src='data:image/png;base64,""" + logo_esquerda.tobytes().hex() + """' style='height: 50px;'>
        <img src='data:image/png;base64,""" + logo_direita.tobytes().hex() + """' style='height: 50px;'>
    </div>
""", unsafe_allow_html=True)

# Título
st.markdown("<h3 style='text-align: center;'>Disponibilidade de câmeras - Atem Belém</h3>", unsafe_allow_html=True)

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

# Cálculos
total_cameras = len(df)
on_cameras = df["Em Funcionamento"].eq("sim").sum()
off_cameras = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].eq("sim").sum()
percent_on = round((on_cameras / total_cameras) * 100, 2)

# Função para criar cartões com cor
def card(title, value, color):
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 10px; border-radius: 10px; text-align: center;
                    color: white; font-weight: bold; font-size: 18px;">
            <div style='font-size: 14px'>{title}</div>
            <div style='font-size: 22px'>{value}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# Cartões com layout responsivo
st.markdown("## 📊 Visão Geral")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
with col1:
    card("Total Câmeras", total_cameras, "#343a40")  # cinza escuro
with col2:
    card("Câmeras ON", on_cameras, "#198754")  # verde
with col3:
    card("Câmeras OFF", off_cameras, "#dc3545")  # vermelho
with col4:
    card("Gravando", gravando, "#0d6efd")  # azul
with col5:
    cor_percent = "#198754" if percent_on >= 95 else "#dc3545"
    card("Online (%)", f"{percent_on}%", cor_percent)

# Filtro avançado
st.markdown("---")
st.subheader("📋 Tabela de Câmeras")
st.markdown("Use os filtros abaixo para refinar os resultados.")

col_f1, col_f2 = st.columns(2)
with col_f1:
    opcao_filtro = st.selectbox("Filtrar por funcionamento:", ["Todos", "Somente ON", "Somente OFF"])
with col_f2:
    modelo_filtro = st.selectbox("Filtrar por modelo:", ["Todos"] + sorted(df["Modelo"].dropna().unique().tolist()))

# Aplicar filtros
df_filtrado = df.copy()
if opcao_filtro == "Somente ON":
    df_filtrado = df_filtrado[df_filtrado["Em Funcionamento"] == "sim"]
elif opcao_filtro == "Somente OFF":
    df_filtrado = df_filtrado[df_filtrado["Em Funcionamento"] == "não"]

if modelo_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Modelo"] == modelo_filtro]

st.dataframe(df_filtrado, use_container_width=True)

# Gráfico: Distribuição por Modelo
st.markdown("---")
st.subheader("📦 Distribuição por Modelo")
st.bar_chart(df["Modelo"].value_counts())

# Gráfico: FPS por Câmera
st.subheader("📈 FPS por Câmera")
st.line_chart(df[["Nome", "FPS"]].set_index("Nome"))

# Gráfico: Dias de Gravação por Câmera
st.subheader("📊 Dias de Gravação por Câmera")
st.bar_chart(df[["Nome", "Dias de gravação"]].set_index("Nome"))
