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
@@ -101,13 +102,13 @@
st.markdown("## 📊 Visão Geral")
col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
with col1:
    card("Total Câmeras", total_cameras, "#343a40")  # cinza escuro
    card("Total Câmeras", total_cameras, "#343a40")
with col2:
    card("Câmeras ON", on_cameras, "#198754")  # verde
    card("Câmeras ON", on_cameras, "#198754")
with col3:
    card("Câmeras OFF", off_cameras, "#dc3545")  # vermelho
    card("Câmeras OFF", off_cameras, "#dc3545")
with col4:
    card("Gravando", gravando, "#0d6efd")  # azul
    card("Gravando", gravando, "#0d6efd")
with col5:
    cor_percent = "#198754" if percent_on >= 95 else "#dc3545"
    card("Online (%)", f"{percent_on}%", cor_percent)
@@ -135,25 +136,64 @@

st.dataframe(df_filtrado, use_container_width=True)

# Gráficos
fig1, ax1 = plt.subplots(figsize=(10, 4))
df["Modelo"].value_counts().plot(kind='bar', ax=ax1)
ax1.set_title("Distribuição por Modelo")
buffer_fig1 = BytesIO()
plt.tight_layout()
fig1.savefig(buffer_fig1, format='png')
buffer_fig1.seek(0)

fig2, ax2 = plt.subplots(figsize=(10, 4))
df.plot(x="Nome", y="FPS", kind="line", ax=ax2, legend=False)
ax2.set_title("FPS por Câmera")
buffer_fig2 = BytesIO()
plt.tight_layout()
fig2.savefig(buffer_fig2, format='png')
buffer_fig2.seek(0)

fig3, ax3 = plt.subplots(figsize=(10, 4))
df.plot(x="Nome", y="Dias de gravação", kind="bar", ax=ax3, legend=False)
ax3.set_title("Dias de Gravação por Câmera")
buffer_fig3 = BytesIO()
plt.tight_layout()
fig3.savefig(buffer_fig3, format='png')
buffer_fig3.seek(0)

# Botão de exportação PDF (somente filtrado)
def gerar_pdf(dados, nome="relatorio.pdf"):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Relatório de Câmeras - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
    pdf.set_font("Arial", size=8)

    # Adiciona logos
    pdf.image("logo.jpeg", x=10, y=8, w=30)
    pdf.image("atem.png", x=250, y=8, w=30)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 15, f"Relatório de Câmeras - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", ln=True, align="C")
    pdf.ln(5)

    # Adiciona gráficos
    for buf in [buffer_fig1, buffer_fig2, buffer_fig3]:
        img_path = "temp_plot.png"
        with open(img_path, "wb") as f:
            f.write(buf.getvalue())
        pdf.image(img_path, x=10, w=270)
        pdf.ln(5)
        os.remove(img_path)

    pdf.set_font("Arial", size=6)
    colunas = dados.columns.tolist()
    largura_coluna = 270 / len(colunas)

    for col in colunas:
        pdf.cell(largura_coluna, 10, col[:20], border=1)
        pdf.cell(largura_coluna, 6, col[:30], border=1)
    pdf.ln()

    for _, row in dados.iterrows():
        for item in row:
            texto = str(item)
            pdf.cell(largura_coluna, 10, texto[:20], border=1)
            pdf.cell(largura_coluna, 6, texto[:60], border=1)
        pdf.ln()

    pdf_output = pdf.output(dest='S').encode('latin1')
@@ -167,12 +207,12 @@
# Gráfico: Distribuição por Modelo
st.markdown("---")
st.subheader("📦 Distribuição por Modelo")
st.bar_chart(df["Modelo"].value_counts())
st.pyplot(fig1)

# Gráfico: FPS por Câmera
st.subheader("📈 FPS por Câmera")
st.line_chart(df[["Nome", "FPS"]].set_index("Nome"))
st.pyplot(fig2)

# Gráfico: Dias de Gravação por Câmera
st.subheader("📊 Dias de Gravação por Câmera")
st.bar_chart(df[["Nome", "Dias de gravação"]].set_index("Nome"))
st.pyplot(fig3)
