import pyautogui
import time

print("🖱️ Movimente o mouse para ver as coordenadas (CTRL+C para sair)\n")

try:
    while True:
        x, y = pyautogui.position()
        print(f"Posição atual: X={x}, Y={y}", end="\r")
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\n✅ Programa encerrado.")
