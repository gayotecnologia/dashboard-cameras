import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
from login import check_login
from io import BytesIO
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import base64

# Checa login antes de qualquer coisa
check_login()

# Configura a página para ser responsiva
st.set_page_config(layout="wide")

# Carrega imagens das logos
logo_esquerda = Image.open("logo.jpeg")
logo_direita = Image.open("atem.png")

# Converter imagens para base64
from io import BytesIO
def pil_image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

logo_esquerda_base64 = pil_image_to_base64(logo_esquerda)
logo_direita_base64 = pil_image_to_base64(logo_direita)

# Exibe as logos de forma responsiva
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px 0;'>
        <img src='data:image/png;base64,{logo_esquerda_base64}' style='height: 50px;'>
        <img src='data:image/png;base64,{logo_direita_base64}' style='height: 50px;'>
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

st.dataframe(df_filtrado, use_container_width=True)

# Botão para exportar PDF
if st.button("Exportar Relatório em PDF"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    # Inserir logos
    c.drawImage(ImageReader(logo_esquerda), 40, height - 60, width=100, preserveAspectRatio=True)
    c.drawImage(ImageReader(logo_direita), width - 140, height - 60, width=100, preserveAspectRatio=True)

    # Título
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 80, "Relatório de Câmeras - Atem Belém")

    # Data e hora
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 100, "Data/Hora: " + datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

    # Tabela de dados
    x_offset = 40
    y_offset = height - 130
    row_height = 12
    font_size = 6
    c.setFont("Helvetica", font_size)

    columns = list(df_filtrado.columns)
    col_widths = [max(100 if col == "Descrição" else 60 for col in columns)] * len(columns)

    for i, col in enumerate(columns):
        c.drawString(x_offset + sum(col_widths[:i]), y_offset, col[:18])

    y_offset -= row_height
    for index, row in df_filtrado.iterrows():
        if y_offset < 40:
            c.showPage()
            y_offset = height - 60
            c.setFont("Helvetica", font_size)
            c.drawImage(ImageReader(logo_esquerda), 40, height - 60, width=100, preserveAspectRatio=True)
            c.drawImage(ImageReader(logo_direita), width - 140, height - 60, width=100, preserveAspectRatio=True)
        for i, col in enumerate(columns):
            texto = str(row[col])[:60] if col == "Descrição" else str(row[col])[:20]
            c.drawString(x_offset + sum(col_widths[:i]), y_offset, texto)
        y_offset -= row_height

    c.save()
    st.download_button(
        label="🔍 Baixar Relatório PDF",
        data=buffer.getvalue(),
        file_name="relatorio_cameras.pdf",
        mime="application/pdf"
    )

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
