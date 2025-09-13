import shutil
import os

# Caminho do arquivo CSV de origem
csv_origem = r"C:\Users\gayo\Documents\status_cameras\none_csv01.csv"

# Caminho da pasta onde o arquivo atualizado será salvo (mesma pasta do projeto)
pasta_destino = r"C:\Users\gayo\Documents\status_cameras"

def atualizar_csv():
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(csv_origem):
            print(f"❌ Arquivo não encontrado: {csv_origem}")
            return

        # Nome do arquivo atualizado (sobrescreve sempre com o mesmo nome)
        csv_destino = os.path.join(pasta_destino, "status_atualizado.csv")

        # Faz uma cópia do arquivo de origem
        shutil.copy2(csv_origem, csv_destino)

        print(f"✅ CSV atualizado com sucesso em {csv_destino}")

    except Exception as e:
        print(f"❌ Erro ao atualizar CSV: {e}")

if __name__ == "__main__":
    atualizar_csv()
