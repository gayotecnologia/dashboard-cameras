import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Spacer, Image
from datetime import datetime

# ------------------------------
# Carregar CSV
# ------------------------------
df = pd.read_csv("cameras.csv")

# Abreviar descrição para 26 caracteres
df["Descrição"] = df["Descrição"].astype(str).str.slice(0, 26)

# Converter Tempo Inativo (dias) para horas
if "Tempo Inativo" in df.columns:
    df["Tempo Inativo (horas)"] = df["Tempo Inativo"].astype(float) * 24
    df["Tempo Inativo (horas)"] = df["Tempo Inativo (horas)"].apply(lambda x: f"{int(x):>5} h")
else:
    df["Tempo Inativo (horas)"] = "0 h"

# ------------------------------
# Criar PDF
# ------------------------------
arquivo_pdf = "Relatorio_Cameras.pdf"
pdf = SimpleDocTemplate(arquivo_pdf, pagesize=A4)
elementos = []

largura, altura = A4

# Inserir logos
logo_esquerda = "logo_empresa.png"
logo_direita = "logo_cliente.png"
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
