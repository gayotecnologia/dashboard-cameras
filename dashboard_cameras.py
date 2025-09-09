import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from PIL import Image
from datetime import datetime, timedelta
from login import check_login
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Spacer, Image
from datetime import datetime
import base64
import pytz

# ------------------------------
# Carregar CSV
# ------------------------------
df = pd.read_csv("cameras.csv")
# Checa login antes de qualquer coisa
check_login()

# Abreviar descrição para 26 caracteres
df["Descrição"] = df["Descrição"].astype(str).str.slice(0, 26)
# Configura a página para ser responsiva
st.set_page_config(layout="wide")

# Converter Tempo Inativo (dias) para horas
if "Tempo Inativo" in df.columns:
    df["Tempo Inativo (horas)"] = df["Tempo Inativo"].astype(float) * 24
    df["Tempo Inativo (horas)"] = df["Tempo Inativo (horas)"].apply(lambda x: f"{int(x):>5} h")
else:
    df["Tempo Inativo (horas)"] = "0 h"
# Carrega imagens das logos (e redimensiona para tamanho adequado no PDF)
logo_esquerda = Image.open("logo.jpeg")
logo_direita = Image.open("atem.png")

# Converter imagens para base64
def pil_image_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

# ------------------------------
# Criar PDF
# ------------------------------
arquivo_pdf = "Relatorio_Cameras.pdf"
pdf = SimpleDocTemplate(arquivo_pdf, pagesize=A4)
elementos = []
logo_esquerda_base64 = pil_image_to_base64(logo_esquerda)
logo_direita_base64 = pil_image_to_base64(logo_direita)

largura, altura = A4
# Exibe as logos de forma responsiva
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px 0;'>
        <img src='data:image/png;base64,{logo_esquerda_base64}' style='height: 40px;'>
        <img src='data:image/png;base64,{logo_direita_base64}' style='height: 40px;'>
    </div>
""", unsafe_allow_html=True)

# Inserir logos
logo_esquerda = "logo_empresa.png"
logo_direita = "logo_cliente.png"
# Título
st.markdown("<h3 style='text-align: center;'>Disponibilidade de câmeras - Atem Belém</h3>", unsafe_allow_html=True)

# Leitura do CSV
try:
    elementos.append(Image(logo_esquerda, width=80, height=40))
    elementos[-1].hAlign = "LEFT"
    elementos.append(Image(logo_direita, width=80, height=40))
    elementos[-1].hAlign = "RIGHT"
except:
    pass

elementos.append(Spacer(1, 20))

# Título centralizado
titulo = "Relatório de Câmeras - Atem Belém"
subtitulo = datetime.now().strftime("Gerado em: %d/%m/%Y %H:%M")

c = canvas.Canvas(arquivo_pdf, pagesize=A4)
c.setFont("Helvetica-Bold", 14)
titulo_largura = c.stringWidth(titulo, "Helvetica-Bold", 14)
c.drawString((largura - titulo_largura) / 2, altura - 60, titulo)

c.setFont("Helvetica", 10)
subtitulo_largura = c.stringWidth(subtitulo, "Helvetica", 10)
c.drawString((largura - subtitulo_largura) / 2, altura - 80, subtitulo)

c.save()

# ------------------------------
# Montar tabela
# ------------------------------
colunas = ["Nome", "Descrição", "Dias de gravação", "Tempo Inativo (horas)"]
dados = [colunas] + df[colunas].values.tolist()

tabela = Table(dados, repeatRows=1)

tabela.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.gray),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
    ("ALIGN", (0, 0), (1, -1), "LEFT"),   # Nome e Descrição à esquerda
    ("ALIGN", (2, 0), (2, -1), "LEFT"),   # Dias de gravação à esquerda
    ("ALIGN", (3, 0), (3, -1), "RIGHT"),  # Tempo Inativo alinhado à direita
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
]))

elementos.append(tabela)

# ------------------------------
# Gerar PDF final
# ------------------------------
doc = SimpleDocTemplate(arquivo_pdf, pagesize=A4)
doc.build(elementos)

print(f"✅ Relatório gerado: {arquivo_pdf}")
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

# Exportar para PDF (logo após a tabela)
if st.button("📄 Exportar Relatório em PDF"):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(A4))

    def desenhar_cabecalho_pdf(c):
        # Logos
        c.drawImage(ImageReader(logo_esquerda), 30, 530, width=80, height=30, preserveAspectRatio=True)
        c.drawImage(ImageReader(logo_direita), 740, 530, width=80, height=30, preserveAspectRatio=True)

        # Título centralizado
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(420, 520, "Relatório de Disponibilidade de Câmeras - Atem Belém")

        # >>>>>> ADIÇÃO: Data/Hora da exportação (centralizado) <<<<<<
        fuso = pytz.timezone("America/Belem")
        data_local = datetime.now(fuso).strftime("%d/%m/%Y %H:%M:%S")
        c.setFont("Helvetica", 10)
        c.drawCentredString(420, 505, f"Exportado em: {data_local}")
        # -------------------------------------------------------------

        # Cabeçalho da tabela
        y_header = 480
        c.setFont("Helvetica-Bold", 8)
        col_titles = ["Nome", "Funcionamento", "Descrição", "Modelo", "Gravando", "Dias Gravação", "Tempo Inativo (dias)"]
        col_widths = [120, 80, 130, 100, 60, 70, 90]
        for i, title in enumerate(col_titles):
            c.drawString(sum(col_widths[:i]) + 30, y_header, title)
        return y_header - 15, col_widths

    y, col_widths = desenhar_cabecalho_pdf(c)
    c.setFont("Helvetica", 7)

    for _, row in df_filtrado.iterrows():
        values = [
            str(row["Nome"][:30]),
            row["Em Funcionamento"],
            str(row["Descrição"][:26]),
            str(row["Modelo"][:20]),
            row["Gravando em Disco"],
            str(row["Dias de gravação"]),
            f"{row['Tempo Inativo (dias)']} dias" if pd.notna(row['Tempo Inativo (dias)']) else ""
        ]
        for i, val in enumerate(values):
            x_pos = sum(col_widths[:i]) + 30
            align_right = i == len(values) - 1
            if align_right:
                c.drawRightString(x_pos + col_widths[i] - 5, y, val)
            else:
                c.drawString(x_pos, y, val)
        y -= 12
        if y < 40:
            c.showPage()
            y, col_widths = desenhar_cabecalho_pdf(c)
            c.setFont("Helvetica", 7)

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
