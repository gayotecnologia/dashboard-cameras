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

# Converter Tempo Inativo para dias
def converter_tempo_para_dias_v2(tempo_str):
    try:
        horas = minutos = segundos = 0
        partes = tempo_str.split(',')
        for parte in partes:
            parte = parte.strip()
            if "Hora" in parte:
                horas = int(parte.split()[0])
            elif "Minuto" in parte:
                minutos = int(parte.split()[0])
            elif "Segundo" in parte:
                segundos = int(parte.split()[0])
        total_segundos = horas * 3600 + minutos * 60 + segundos
        dias = round(total_segundos / 86400, 2)
        return dias
    except:
        return None

df["Tempo Inativo (dias)"] = df["Tempo Inativo"].apply(converter_tempo_para_dias_v2)

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
    card("Disponibilidade (%)", f"{percent_on}%", cor_percent)

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

# Exibe a tabela com 'dias' sufixado
df_filtrado_exibe = df_filtrado.copy()
df_filtrado_exibe["Tempo Inativo (dias)"] = df_filtrado_exibe["Tempo Inativo (dias)"].apply(lambda x: f"{x} dias" if pd.notna(x) else "")

st.dataframe(df_filtrado_exibe[[
    "Nome", "Em Funcionamento", "Endereço", "Descrição", "Ativado", "Modelo",
    "Dias de gravação", "Gravando em Disco", "FPS", "Disco Utilizado", "Tempo Inativo (dias)"
]], use_container_width=True)

# Exportar para PDF (mover para logo após a tabela)
if st.button("📄 Exportar Relatório em PDF"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    # Adiciona logos
    c.drawImage(ImageReader(logo_esquerda), 30, 530, width=100, height=40)
    c.drawImage(ImageReader(logo_direita), 740, 530, width=100, height=40)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(420, 520, "Relatório de Disponibilidade de Câmeras - Atem Belém")

    # Cabeçalho da Tabela
    y = 480
    c.setFont("Helvetica-Bold", 8)
    col_titles = ["Nome", "Funcionamento", "Descrição", "Modelo", "Gravando", "Dias Gravação", "Tempo Inativo (dias)"]
    col_widths = [120, 80, 150, 100, 60, 70, 90]
    for i, title in enumerate(col_titles):
        c.drawString(sum(col_widths[:i]) + 30, y, title)

    # Conteúdo da tabela
    y -= 15
    c.setFont("Helvetica", 7)
    for _, row in df_filtrado.iterrows():
        values = [
            str(row["Nome"][:30]),
            row["Em Funcionamento"],
            str(row["Descrição"][:40]),
            str(row["Modelo"][:20]),
            row["Gravando em Disco"],
            str(row["Dias de gravação"]),
            f"{row['Tempo Inativo (dias)']} dias" if pd.notna(row['Tempo Inativo (dias)']) else ""
        ]
        for i, val in enumerate(values):
            c.drawString(sum(col_widths[:i]) + 30, y, val)
        y -= 12
        if y < 40:
            c.showPage()
            y = 530

    c.save()
    buffer.seek(0)
    b64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
    href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="relatorio_cameras.pdf">📥 Baixar PDF</a>'
    st.markdown(href, unsafe_allow_html=True)

# Gráficos
st.markdown("---")
st.subheader("🛆 Distribuição por Modelo")
st.bar_chart(df["Modelo"].value_counts())

st.subheader("📈 FPS por Câmera")
st.line_chart(df[["Nome", "FPS"]].set_index("Nome"))

st.subheader("📊 Dias de Gravação por Câmera")
st.bar_chart(df[["Nome", "Dias de gravação"]].set_index("Nome"))

st.subheader("📝 Top 20 Câmeras com Maior Tempo Inativo (em dias)")
top_inativas = df[["Nome", "Tempo Inativo (dias)"]].dropna().copy()
top_inativas = top_inativas.sort_values(by="Tempo Inativo (dias)", ascending=False).head(20)
if not top_inativas.empty:
    st.bar_chart(top_inativas.set_index("Nome"))
else:
    st.info("Nenhuma câmera com tempo inativo registrado.")
