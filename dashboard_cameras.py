import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from reportlab.lib.units import cm

# ----------------------------
# Função para converter tempo em dias
# ----------------------------
def converter_para_dias(tempo_str):
    try:
        partes = tempo_str.replace("Hora(s)", "").replace("Minuto(s)", "").replace("Segundo(s)", "").split(",")
        horas = int(partes[0]) if len(partes) > 0 else 0
        minutos = int(partes[1]) if len(partes) > 1 else 0
        segundos = int(partes[2]) if len(partes) > 2 else 0
        total_dias = horas / 24 + minutos / (24*60) + segundos / (24*3600)
        return round(total_dias, 2)
    except:
        return 0

# ----------------------------
# Função para desenhar cabeçalho
# ----------------------------
def desenhar_cabecalho_pdf(c, width, height):
    titulo = "Relatório de Câmeras - Atem Belém"
    c.setFont("Helvetica-Bold", 14)
    titulo_largura = c.stringWidth(titulo, "Helvetica-Bold", 14)
    c.drawString((width - titulo_largura) / 2, height - 60, titulo)

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    c.setFont("Helvetica", 10)
    data_largura = c.stringWidth(data_atual, "Helvetica", 10)
    c.drawString((width - data_largura) / 2, height - 75, data_atual)

# ----------------------------
# Função para exportar PDF
# ----------------------------
def exportar_pdf(df):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    desenhar_cabecalho_pdf(c, width, height)

    dados = [["Nome", "Descrição", "Dias de Gravação", "Tempo Inativo"]]

    for _, row in df.iterrows():
        nome = str(row["Nome"])
        descricao = str(row["Descrição"])[:26]  # abreviação
        dias = str(row["Dias de gravação"])     # alinhado à esquerda
        tempo = str(row["Tempo Inativo"]).rjust(20)  # alinhado à direita
        dados.append([nome, descricao, dias, tempo])

    tabela = Table(dados, colWidths=[5*cm, 6*cm, 3*cm, 4*cm])
    tabela.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (2, 1), (2, -1), "LEFT"),
        ("ALIGN", (3, 1), (3, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONT", (0, 1), (-1, -1), "Helvetica"),
    ]))

    largura, altura = tabela.wrapOn(c, width, height)
    tabela.drawOn(c, 30, height - 150 - altura)

    c.showPage()
    c.save()

    buffer.seek(0)
    return buffer

# ----------------------------
# Streamlit App
# ----------------------------
st.title("Dashboard de Câmeras - Atem Belém")

# Upload CSV
arquivo = st.file_uploader("Carregar CSV", type="csv")
if arquivo:
    df = pd.read_csv(arquivo, sep=";")
    df["Tempo Inativo (dias)"] = df["Tempo Inativo"].apply(converter_para_dias)

    st.subheader("📋 Tabela de Câmeras")
    st.dataframe(df)

    # Botão de exportação PDF
    if st.button("📄 Exportar Relatório PDF"):
        pdf_buffer = exportar_pdf(df)
        st.download_button(
            label="📥 Baixar Relatório PDF",
            data=pdf_buffer,
            file_name="relatorio_cameras.pdf",
            mime="application/pdf",
        )

    # Gráfico: Top 20 câmeras com maior tempo inativo
    st.subheader("📊 Top 20 Câmeras com Maior Tempo Inativo (dias)")
    df_top = df.sort_values("Tempo Inativo (dias)", ascending=False).head(20)
    fig, ax = plt.subplots(figsize=(10, 6))
    df_top.plot(x="Nome", y="Tempo Inativo (dias)", kind="bar", ax=ax, legend=False, color="red")
    ax.set_ylabel("Dias")
    ax.set_xlabel("Câmeras")
    ax.set_title("Top 20 Câmeras com Maior Tempo Inativo (em dias)")
    st.pyplot(fig)
