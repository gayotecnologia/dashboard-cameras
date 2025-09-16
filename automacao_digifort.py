import pyautogui
import time
import schedule
import subprocess
import datetime

# Coordenadas capturadas
exportar = (1502, 977)
arquivo_csv = (343, 265)
salvar = (748, 588)
popup_substituir = (1019, 524)
popup_cabecalho = (1019, 617)

def exportar_csv():
    print("▶️ Iniciando automação no Digifort...")
    time.sleep(2)

    # Clicar nos botões para exportar
    pyautogui.click(exportar)
    time.sleep(2)
    pyautogui.click(arquivo_csv)
    time.sleep(2)
    pyautogui.click(salvar)
    time.sleep(2)
    pyautogui.click(popup_substituir)
    time.sleep(2)
    pyautogui.click(popup_cabecalho)
    time.sleep(3)

    print("✅ Arquivo CSV exportado com sucesso!")

    # Enviar para o GitHub (somente status_cameras.csv)
    try:
        subprocess.run(["git", "add", "status_cameras.csv"], check=True)
        commit_message = f"Atualização automática do CSV - {datetime.datetime.now()}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("✅ Arquivo 'status_cameras.csv' enviado para o GitHub com sucesso!")
    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro ao atualizar o GitHub: {e}")

# Executar a cada 10 minutos
schedule.every(10).minutes.do(exportar_csv)

print("==============================================")
print("🚀 Automação Digifort + GitHub iniciada")
print("📌 Executando a cada 2 minutos...")
print("==============================================")

while True:
    schedule.run_pending()
    time.sleep(1)
