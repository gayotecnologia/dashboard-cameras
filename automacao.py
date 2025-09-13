import time
import pyautogui as pg
import subprocess
import os

# Caminhos
csv_origem = r"C:\Users\gayo\Documents\status_cameras\none_csv01.csv"
csv_destino = r"C:\Users\gayo\Documents\status_cameras\status_atualizado.csv"
repo_path = r"C:\Users\gayo\Documents\status_cameras"

# Função para registrar no log
def registrar_log(mensagem):
    with open(os.path.join(repo_path, "log.txt"), "a", encoding="utf-8") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {mensagem}\n")

try:
    # -------------------------
    # Passo 1: clicar em "Gerar Relatório"
    # -------------------------
    time.sleep(2)
    pg.click(200, 200)  # <-- ajustar coordenadas do botão "Gerar Relatório"

    time.sleep(2)

    # -------------------------
    # Passo 2: digitar caminho e salvar
    # -------------------------
    pg.typewrite(csv_origem)
    pg.press("enter")

    # -------------------------
    # Passo 3: lidar com os popups
    # -------------------------

    # Popup 1: arquivo já existe (substituir?)
    time.sleep(2)
    pg.press("left")   # seta para "Sim"
    pg.press("enter")  # confirma

    # Popup 2: incluir cabeçalho?
    time.sleep(2)
    pg.press("left")   # seta para "Sim"
    pg.press("enter")  # confirma

    # -------------------------
    # Passo 4: copiar/renomear CSV
    # -------------------------
    if os.path.exists(csv_origem):
        os.replace(csv_origem, csv_destino)
        registrar_log("✅ CSV atualizado com sucesso")
    else:
        registrar_log("❌ Erro: arquivo de exportação não encontrado")

    # -------------------------
    # Passo 5: Git add/commit/push
    # -------------------------
    os.chdir(repo_path)
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Atualização automática do CSV"], check=True)
    subprocess.run(["git", "push"], check=True)

    registrar_log("📤 Atualização enviada para o GitHub com sucesso")

except Exception as e:
    registrar_log(f"❌ Erro durante automação: {e}")
