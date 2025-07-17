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
st.markdown("<h3 style='text-align: center;'> Dashboard de câmeras - Atem Belém.</h3>", unsafe_allow_html=True)

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
        <div style="background-color: {color}; padding: 13px; border-radius: 12px; text-align: center; color: white; font-weight: bold;">
            <h6 style="margin: 0;">{title}</h6>
            <h4 style="margin: 0;">{value}</h4>
        </div>
        """,
        unsafe_allow_html=True
    )

# Layout com colunas
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    card("Total de Câmeras", total_cameras, "#343a40")  # cinza escuro

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
st.sidebar.header("🔍 Filtros avançados")

# Status
status_selecionado = st.sidebar.multiselect(
    "Status da Câmera",
    options=df["Em Funcionamento"].unique(),
    default=df["Em Funcionamento"].unique()
)

# Modelo da câmera
modelos_selecionados = st.sidebar.multiselect(
    "Modelo da Câmera",
    options=sorted(df["Modelo"].dropna().unique()),
    default=sorted(df["Modelo"].dropna().unique())
)

# Gravando em disco
gravando_selecionado = st.sidebar.multiselect(
    "Gravando em Disco",
    options=df["Gravando em Disco"].dropna().unique(),
    default=df["Gravando em Disco"].dropna().unique()
)

# Dias de gravação
dias_min, dias_max = int(df["Dias de gravação"].min()), int(df["Dias de gravação"].max())
dias_gravacao = st.sidebar.slider("Dias de Gravação", min_value=dias_min, max_value=dias_max, value=(dias_min, dias_max))

# Endereço
endereco_texto = st.sidebar.text_input("Buscar por Endereço")

# FPS mínimo (opcional)
fps_min = st.sidebar.slider("FPS mínimo", min_value=0, max_value=int(df["FPS"].max()), value=0)

# Aplicando os filtros
df_filtrado = df[
    (df["Em Funcionamento"].isin(status_selecionado)) &
    (df["Modelo"].isin(modelos_selecionados)) &
    (df["Gravando em Disco"].isin(gravando_selecionado)) &
    (df["Dias de gravação"].between(*dias_gravacao)) &
    (df["FPS"] >= fps_min)
]

if endereco_texto:
    df_filtrado = df_filtrado[df_filtrado["Endereço"].str.contains(endereco_texto, case=False, na=False)]
