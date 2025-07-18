import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime, timedelta
from login import check_login
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
import base64
import pytz

# Checa login antes de qualquer coisa
check_login()

# Configura a página para ser responsiva
st.set_page_config(layout="wide")

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
st.markdown("\n")
if st.button("Exportar Relatório em PDF"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))
    width, height = landscape(A4)

    logo_width = 50
    logo_height = 25
    c.drawImage(ImageReader(logo_esquerda), 40, height - logo_height - 20, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
    c.drawImage(ImageReader(logo_direita), width - logo_width - 40, height - logo_height - 20, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')

    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 60, "Relatório de Câmeras - Atem Belém")

    fuso = pytz.timezone("America/Belem")
    data_local = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
    c.setFont("Helvetica", 10)
    c.drawString(40, height - 80, "Data/Hora: " + data_local)

    # Linha única com dados da visão geral com cores e centralizada
    c.setFont("Helvetica-Bold", 8)
    dados_gerais = [
        ("Total Câmeras", total_cameras, colors.darkgray),
        ("ON", on_cameras, colors.green),
        ("OFF", off_cameras, colors.red),
        ("Gravando", gravando, colors.blue),
        ("Online (%)", f"{percent_on}%", colors.green if percent_on >= 95 else colors.red)
    ]
    textos_coloridos = []
    total_largura = 0
    for titulo, valor, cor in dados_gerais:
        texto = f"{titulo}: {valor}   "
        largura = c.stringWidth(texto, "Helvetica-Bold", 8)
        textos_coloridos.append((texto, cor, largura))
        total_largura += largura + 10

    x_inicio = (width - total_largura) / 2
    x = x_inicio
    y_offset = height - 100  # Espaço extra aqui
    for texto, cor, largura in textos_coloridos:
        c.setFillColor(cor)
        c.drawString(x, y_offset, texto)
        x += largura + 10
    c.setFillColor(colors.black)

    # Cabeçalho e dados da tabela
    x_offset = 40
    y_offset -= 20  # Aumentar o espaço antes da tabela
    row_height = 12
    font_size = 6
    c.setFont("Helvetica", font_size)

    columns = list(df_filtrado.columns)
    col_widths = [90 if col == "Descrição" else 60 for col in columns]

    for i, col in enumerate(columns):
        x = x_offset + sum(col_widths[:i])
        c.drawCentredString(x + col_widths[i]/2, y_offset, col[:29])

    y_offset -= row_height
    for index, row in df_filtrado.iterrows():
        if y_offset < 40:
            c.showPage()
            c.drawImage(ImageReader(logo_esquerda), 40, height - logo_height - 20, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            c.drawImage(ImageReader(logo_direita), width - logo_width - 40, height - logo_height - 20, width=logo_width, height=logo_height, preserveAspectRatio=True, mask='auto')
            y_offset = height - 80
            c.setFont("Helvetica", font_size)
            for i, col in enumerate(columns):
                x = x_offset + sum(col_widths[:i])
                c.drawCentredString(x + col_widths[i]/2, y_offset, col[:29])
            y_offset -= row_height

        for i, col in enumerate(columns):
            x = x_offset + sum(col_widths[:i])
            texto = str(row[col])
            if col == "Descrição":
                if len(texto) > 29:
                    texto = texto[:29] + "..."
                c.drawString(x + 2, y_offset, texto)
            elif col == "Modelo":
                if len(texto) > 15:
                    texto = texto[:15] + "..."
                c.drawString(x + 2, y_offset, texto)
            elif col == "Dias de gravação":
                c.drawRightString(x + col_widths[i] - 2, y_offset, texto)
            elif col in ["Gravando em Disco", "FPS", "Disco Utilizado"]:
                c.drawRightString(x + col_widths[i] - 2, y_offset, texto)
            else:
                c.drawCentredString(x + col_widths[i]/2, y_offset, texto)
        y_offset -= row_height

    c.save()
    st.download_button(
        label="🔍 Baixar Relatório PDF",
        data=buffer.getvalue(),
        file_name="relatorio_cameras.pdf",
        mime="application/pdf"
    )

# Gráficos
st.markdown("---")
st.subheader("📦 Distribuição por Modelo")
st.bar_chart(df["Modelo"].value_counts())

st.subheader("📈 FPS por Câmera")
st.line_chart(df[["Nome", "FPS"]].set_index("Nome"))

st.subheader("📊 Dias de Gravação por Câmera")
st.bar_chart(df[["Nome", "Dias de gravação"]].set_index("Nome"))
