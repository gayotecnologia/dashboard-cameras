import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime, timedelta
from login import check_login
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import base64
import pytz
import matplotlib.pyplot as plt

# Checa login antes de qualquer coisa
check_login()

# Configura a página para ser responsiva
st.set_page_config(layout="wide")

# Aplica fonte customizada via CSS
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Carrega imagens das logos (e redimensiona para tamanho adequado no PDF)
logo_esquerda = Image.open("logo.jpeg")
logo_direita = Image.open("atem.png")

# Converter imagens para base64
def pil_image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

logo_esquerda_base64 = pil_image_to_base64(logo_esquerda)
logo_direita_base64 = pil_image_to_base64(logo_direita)

# Exibe as logos de forma responsiva
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px 0;'>
        <img src='data:image/png;base64,{logo_esquerda_base64}' style='height: 40px;'>
        <img src='data:image/png;base64,{logo_direita_base64}' style='height: 40px;'>
    </div>
""", unsafe_allow_html=True)

# Título
st.markdown("<h3 style='text-align: center;'>Disponibilidade de câmeras - Atem Belém</h3>", unsafe_allow_html=True)

# Leitura do CSV
try:
    df = pd.read_csv("status_cameras.csv", sep="\t", encoding="utf-8")
    colunas_esperadas = [
        "Nome", "Em Funcionamento", "Endereço", "Descrição",
        "Ativado", "Modelo", "Dias de gravação", "Gravando em Disco", "FPS", "Disco Utilizado", "Tempo Inativo"
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
df["Modelo"] = df["Modelo"].astype(str).str.slice(0, 15)  # Abreviar para 15 caracteres

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
                    color: white; font-weight: bold; font-size: 18px; font-family: 'Segoe UI', sans-serif;">
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
    card("Total Câmeras", total_cameras, "#343a40")
with col2:
    card("Câmeras ON", on_cameras, "#198754")
with col3:
    card("Câmeras OFF", off_cameras, "#dc3545")
with col4:
    card("Gravando", gravando, "#0d6efd")
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

st.dataframe(df_filtrado.style.set_properties(**{
    "text-align": "center"
}).format({"Dias de gravação": "{:>}"}), use_container_width=True)

# Botão de exportação
st.markdown("\n### 📤 Exportar Relatório para PDF")

if st.button("Exportar Relatório"):
    from export_pdf import exportar_relatorio_pdf
    pdf_data = exportar_relatorio_pdf(df_filtrado)
    st.download_button(
        label="📄 Baixar Relatório PDF",
        data=pdf_data,
        file_name=f"relatorio_cameras_{datetime.now().strftime('%Y-%m-%d')}.pdf",
        mime="application/pdf"
    )

# Gráficos
st.markdown("---")
st.subheader("📈 Gráficos")

# Gráfico 1: Dias de gravação por câmera
fig1, ax1 = plt.subplots(figsize=(12, 4))
df_dias = df_filtrado.dropna(subset=["Dias de gravação"])
if not df_dias.empty:
    df_dias.plot(x="Nome", y="Dias de gravação", kind="bar", ax=ax1, legend=False, color="#0d6efd")
    plt.xticks(rotation=90)
    plt.title("Dias de Gravação por Câmera")
    st.pyplot(fig1)

# Gráfico 2: Câmeras ON vs OFF
fig2, ax2 = plt.subplots()
df_estado = pd.Series({"ON": on_cameras, "OFF": off_cameras})
df_estado.plot(kind="bar", color=["#198754", "#dc3545"], ax=ax2)
plt.title("Câmeras ON x OFF")
st.pyplot(fig2)

# Gráfico 3: Gravando vs Não gravando
fig3, ax3 = plt.subplots()
df_gravando = pd.Series({"Gravando": gravando, "Não Gravando": total_cameras - gravando})
df_gravando.plot(kind="bar", color=["#0d6efd", "#6c757d"], ax=ax3)
plt.title("Gravando em Disco")
st.pyplot(fig3)

