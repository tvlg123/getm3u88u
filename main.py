from flask import Flask
from threading import Thread
from playwright.sync_api import sync_playwright
import re
import os
import subprocess

app = Flask(__name__)

def obtener_m3u8():
    with sync_playwright() as p:
        # Iniciar el navegador en modo headless
        print("Iniciando navegador...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Interceptar las solicitudes de red
        m3u8_urls = []

        def intercept_request(request):
            # Verifica si la URL contiene ".m3u8"
            if ".m3u8" in request.url:
                m3u8_urls.append(request.url)
                print(f"Encontrado: {request.url}")

        page.on("request", intercept_request)

        # Navegar a la URL objetivo
        url = "https://streamdz4.lat/player/embed.php?channel=espn"
        print(f"Navegando a: {url}")
        page.goto(url)
        
        # Esperar 10 segundos para cargar completamente la página
        print("Esperando a que cargue el contenido...")
        page.wait_for_timeout(10000)
        
        # Cerrar el navegador
        print("Cerrando navegador...")
        browser.close()

        # Procesar las URLs m3u8 encontradas
        if m3u8_urls:
            print("\nURLs m3u8 encontradas:")
            for url in m3u8_urls:
                print(url)
                # Extraer la parte completa desde "?md5=" hasta el final
                md5_part = re.search(r'\?md5=.*', url)
                if md5_part:
                    md5_value = md5_part.group(0)  # Captura toda la cadena
                    print(f"Extraído: {md5_value}")
                    
                    # Guardar solo el valor extraído en output.txt
                    with open("output.txt", "w") as file:
                        file.write(md5_value)
                    print("Guardado en output.txt")
        else:
            print("No se encontraron URLs m3u8.")

def subir_a_github():
    try:
        print("Subiendo output.txt a GitHub...")
        subprocess.run(["git", "config", "--global", "user.name", "Render Bot"])
        subprocess.run(["git", "config", "--global", "user.email", "bot@render.com"])
        subprocess.run(["git", "add", "output.txt"])
        subprocess.run(["git", "commit", "-m", "Actualización automática de output.txt"])
        subprocess.run(["git", "push"])
        print("Archivo subido exitosamente a GitHub.")
    except Exception as e:
        print(f"Error al subir a GitHub: {e}")

@app.route('/')
def ejecutar():
    print("Ejecutando el script...")
    obtener_m3u8()
    subir_a_github()
    print("Ejecución completada.")
    return "Script ejecutado con éxito"

if __name__ == "__main__":
    print("Iniciando servidor Flask...")
    port = int(os.environ.get("PORT", 5000))
    Thread(target=lambda: app.run(host='0.0.0.0', port=port)).start()
