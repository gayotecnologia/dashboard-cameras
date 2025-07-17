import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login

# Checa login antes de qualquer coisa
check_login()

# Centraliza a logo com tamanho reduzido
col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
with col_logo2:
    image = Image.open("logo.jpeg")
    import streamlit as st
from PIL import Image

# Carregar imagens
logo_esquerda = Image.open("logo.jpeg")        # Sua logo
logo_direita = Image.open("atem.png")          # Logo do cliente (ATEM)

# Layout com duas logos no topo
col1, col2, col3 = st.columns([1, 6, 1])

with col1:
    st.image(logo_esquerda, width=100)

with col3:
    st.image(logo_direita, width=100)

# Título
st.markdown("<h3 style='text-align: center;'> Disponibilidade de câmeras - Atem Belém.</h3>", unsafe_allow_html=True)

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
# Cálculos
total_cameras = len(df)
on_cameras = df["Em Funcionamento"].eq("sim").sum()
off_cameras = df["Em Funcionamento"].eq("não").sum()
gravando = df["Gravando em Disco"].str.lower().eq("sim").sum()
percent_on = round((on_cameras / total_cameras) * 100, 2)

# Função para criar cartões com cor
def card(title, value, color):
    st.markdown(
        f"""
        <div style="background-color: {color}; padding: 12px; border-radius: 7px; text-align: center; color: white; font-weight: bold;">
            <h11 style="margin: 0;">{title}</11>
            <h5 style="margin: 0;">{value}</h5>
        </div>
        """,
        unsafe_allow_html=True
    )

# Layout com colunas
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    card("Total Câmeras", total_cameras, "#343a40")  # cinza escuro

with col2:
    card("Câmeras ON", on_cameras, "#198754")  # verde fixo

with col3:
    card("Câmeras OFF", off_cameras, "#dc3545")  # vermelho

with col4:
    cor_percent = "#198754" if percent_on >= 95 else "#dc3545"
    card("Online (%)", f"{percent_on}%", cor_percent)

with col5:
    card("Gravando", gravando, "#0d6efd")  # azul


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
