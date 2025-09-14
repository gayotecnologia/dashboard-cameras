import subprocess
import datetime
import os

try:
    # Garante que vamos commitar tudo que mudou
    subprocess.run(["git", "add", "-A"], check=True)

    # Faz commit com timestamp
    commit_msg = f"Push automático - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    subprocess.run(["git", "commit", "-m", commit_msg], check=True)

    # Envia para o GitHub
    subprocess.run(["git", "push"], check=True)

    print("✅ Push realizado com sucesso!")

except subprocess.CalledProcessError as e:
    print(f"❌ Erro ao executar comando git: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
