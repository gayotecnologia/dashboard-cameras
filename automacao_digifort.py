import pyautogui
import time
import schedule
import subprocess
from datetime import datetime

# Desativa o fail-safe do PyAutoGUI (cuidado: sem ESC de emergência)
pyautogui.FAILSAFE = False

def exportar_csv():
    try:
        print("▶️ Iniciando automação no Digifort...")

        # Clicar em "Exportar relatório"
        pyautogui.click(1502, 977)
        time.sleep(2)

        # Selecionar o arquivo CSV já existente
        pyautogui.click(334, 26089)
        time.sleep(1)

        # Clicar em "Salvar"
        pyautogui.click(748, 588)
        time.sleep(2)

        # Popup: substituir arquivo
        pyautogui.click(1019, 524)
        time.sleep(1)

        # Popup: incluir cabeçalho
        pyautogui.click(1019, 617)
        time.sleep(2)

        print("✅ Arquivo CSV exportado com sucesso!")

        # Enviar para o GitHub
        atualizar_github()

    except Exception as e:
        print(f"⚠️ Erro durante automação: {e}")

def atualizar_github():
    try:
        # Adiciona todas as mudanças
        subprocess.run(["git", "add", "."], check=True)

        # Faz commit apenas se houver mudanças
        subprocess.run(
            ["git", "commit", "-am", f"Atualização automática - {datetime.now()}"],
            check=False
        )

        # Faz o push
        subprocess.run(["git", "push", "origin", "main"], check=True)

        print("✅ Arquivo enviado para o GitHub com sucesso!")

    except subprocess.CalledProcessError as e:
        print(f"⚠️ Erro ao atualizar o GitHub: {e}")

# Agendar a automação a cada 10 minutos
schedule.every(2).minutes.do(exportar_csv)

print("===============================================")
print("🚀 Iniciando Automação Digifort + GitHub")
print("===============================================")
print("⏳ Automação iniciada. Executando a cada 10 minutos...")

# Loop infinito da automação
while True:
    schedule.run_pending()
    time.sleep(1)
