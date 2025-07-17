import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import os

# Checa login antes de qualquer coisa
check_login()

# Configura a página para ser responsiva
st.set_page_config(layout="wide")

# Carrega imagens das logos
logo_esquerda = Image.open("logo.jpeg")
logo_direita = Image.open("atem.png")

# Codifica as imagens em base64
import io
buffer_esq = io.BytesIO()
logo_esquerda.save(buffer_esq, format="JPEG")
img_str_esq = base64.b64encode(buffer_esq.getvalue()).decode()

buffer_dir = io.BytesIO()
logo_direita.save(buffer_dir, format="PNG")
img_str_dir = base64.b64encode(buffer_dir.getvalue()).decode()

# Layout com duas logos no topo responsivo
st.markdown(f"""
    <style>
        @media only screen and (max-width: 600px) {{
            .logo-container {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .logo-container img {{
                height: 30px !important;
                width: auto;
            }}
        }}
        .logo-container {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .logo-container img {{
            height: 60px;
            width: auto;
        }}
    </style>
    <div class="logo-container">
        <img src="data:image/jpeg;base64,{img_str_esq}" alt="Logo Esquerda">
        <img src="data:image/png;base64,{img_str_dir}" alt="Logo Direita">
    </div>
""", unsafe_allow_html=True)

# Título
st.markdown("<h3 style='text-align: center;'>Disponibilidade de câmeras - Atem Belém</h3>", unsafe_allow_html=True)

# Leitura do CSV
df = pd.read_csv("status_cameras.csv", sep="\t", encoding="utf-8")
colunas_esperadas = [
    "Nome", "Em Funcionamento", "Endereço", "Descrição",
    "Ativado", "Modelo", "Dias de gravação", "Gravando em Disco", "FPS", "Disco Utilizado"
]
if not all(col in df.columns for col in colunas_esperadas):
    st.error("❌ O CSV não possui todas as colunas esperadas.")
    st.write("Colunas encontradas:", df.columns.tolist())
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

# Gráfico: Dias de Gravação por Câmera
st.markdown("---")
st.subheader("📊 Dias de Gravação por Câmera")

# Converter coluna para numérico e limpar dados inválidos
df_dias = df.copy()
df_dias["Dias de gravação"] = pd.to_numeric(df_dias["Dias de gravação"], errors="coerce")
df_dias = df_dias.dropna(subset=["Dias de gravação"])

fig3, ax3 = plt.subplots(figsize=(12, 4))
df_dias.plot(x="Nome", y="Dias de gravação", kind="bar", ax=ax3, legend=False)
ax3.set_title("Dias de Gravação por Câmera")
ax3.set_ylabel("Dias")
ax3.set_xlabel("Câmeras")
plt.xticks(rotation=90)
plt.tight_layout()
st.pyplot(fig3)

# Botão de exportação PDF (somente filtrado)
def gerar_pdf(dados, nome="relatorio.pdf"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()

    # Adiciona logos
    pdf.image("logo.jpeg", x=10, y=8, w=30)
    pdf.image("atem.png", x=250, y=8, w=30)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 15, f"Relatório de Câmeras - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
    pdf.ln(5)

    # Tabela
    pdf.set_font("Arial", size=6)
    colunas = dados.columns.tolist()
    largura_coluna = 270 / len(colunas)

    for col in colunas:
        pdf.cell(largura_coluna, 6, col[:30], border=1)
    pdf.ln()

    for _, row in dados.iterrows():
        for item in row:
            texto = str(item)
            pdf.cell(largura_coluna, 6, texto[:60], border=1)
        pdf.ln()

    pdf_output = pdf.output(dest='S').encode('latin1')
    buffer = BytesIO(pdf_output)
    return buffer

st.markdown("### 📤 Exportar Relatório Filtrado")
pdf_filtrado = gerar_pdf(df_filtrado)
st.download_button("📄 Baixar PDF Filtrado", data=pdf_filtrado, file_name="relatorio_filtrado.pdf")
