import pyautogui
import time

print("⏳ O clique vai acontecer em 5 segundos...")
time.sleep(5)

pyautogui.click(1495, 975)  # coloque as coordenadas capturadas
print("✅ Clique executado")
