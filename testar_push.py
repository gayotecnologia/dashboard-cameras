import subprocess
import datetime
import os

# Caminho do CSV
csv_path = r"C:\Users\gayo\Documents\status_cameras\status_atualizado.csv"

try:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Arquivo não encontrado: {csv_path}")

    # Adiciona o arquivo ao git
    subprocess.run(["git", "add", csv_path], check=True)

    # Faz commit com timestamp
    commit_msg = f"Teste push automático - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    # Envia para o GitHub
    subprocess.run(["git", "push"], check=True)

    print("✅ Push realizado com sucesso!")

except subprocess.CalledProcessError as e:
    print(f"❌ Erro ao executar comando git: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
