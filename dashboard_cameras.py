import streamlit as st
import pandas as pd
from PIL import Image
from login import check_login
import base64
from io import BytesIO
from datetime import datetime
from fpdf import FPDF

# Checa login antes de qualquer coisa
check_login()

# Configura a página para ser responsiva
st.set_page_config(layout="wide")

# Carrega imagens das logos
logo_esquerda = Image.open("logo.jpeg")
logo_direita = Image.open("atem.png")

# Codifica imagens em base64 para exibição
def image_to_base64(img):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

logo_esquerda_b64 = image_to_base64(logo_esquerda)
logo_direita_b64 = image_to_base64(logo_direita)

# Exibe as logos no topo
st.markdown(f"""
    <div style='display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 10px 0;'>
        <img src='data:image/png;base64,{logo_esquerda_b64}' style='height: 50px;'>
        <img src='data:image/png;base64,{logo_direita_b64}' style='height: 50px;'>
    </div>
""", unsafe_allow_html=True)

# Título
st.markdown("<h3 style='text-align: center;'>Disponibilidade de câmeras - Atem Belém</h3>", unsafe_allow_html=True)

# Leitura do CSV
df = pd.read_csv("status_cameras.csv", sep="\t", encoding="utf-8")
df["Em Funcionamento"] = df["Em Funcionamento"].str.lower().fillna("").str.strip()
df["Gravando em Disco"] = df["Gravando em Disco"].str.lower().fillna("").str.strip()

# Filtros
col_f1, col_f2 = st.columns(2)
with col_f1:
    opcao_filtro = st.selectbox("Filtrar por funcionamento:", ["Todos", "Somente ON", "Somente OFF"])
with col_f2:
    modelo_filtro = st.selectbox("Filtrar por modelo:", ["Todos"] + sorted(df["Modelo"].dropna().unique().tolist()))

# Aplica os filtros
df_filtrado = df.copy()
if opcao_filtro == "Somente ON":
    df_filtrado = df_filtrado[df_filtrado["Em Funcionamento"] == "sim"]
elif opcao_filtro == "Somente OFF":
    df_filtrado = df_filtrado[df_filtrado["Em Funcionamento"] == "não"]

if modelo_filtro != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Modelo"] == modelo_filtro]

# Exibe tabela
st.dataframe(df_filtrado, use_container_width=True)

# Botão para exportar relatório PDF
if st.button("📄 Exportar Relatório Filtrado em PDF"):
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 10)
            self.cell(0, 10, "Relatório de Câmeras - Atem Belém", 0, 1, "C")
            self.image("logo.jpeg", 10, 8, 30)
            self.image("atem.png", 170, 8, 30)
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 0, "C")

        def chapter_title(self):
            self.set_font("Arial", "B", 12)
            self.ln(5)

        def chapter_body(self, data):
            self.set_font("Arial", size=7)
            col_width = 190 / len(data.columns)
            row_height = 6
            for i, col in enumerate(data.columns):
                self.cell(col_width, row_height, str(col), border=1)
            self.ln(row_height)
            for row in data.itertuples(index=False):
                for item in row:
                    self.cell(col_width, row_height, str(item), border=1)
                self.ln(row_height)

    pdf = PDF()
    pdf.add_page()
    pdf.chapter_title()
    pdf.chapter_body(df_filtrado)

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)

    st.download_button(
        label="📥 Baixar Relatório PDF",
        data=buffer,
        file_name=f"relatorio_cameras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )
