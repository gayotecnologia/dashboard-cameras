import pyautogui
import time

print("➡️ Passe o mouse no botão 'Gerar Relatório' em 5 segundos...")
time.sleep(5)
time.sleep(5)


pos = pyautogui.position()
print(f"📌 Posição capturada: {pos}")
