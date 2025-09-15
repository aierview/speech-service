import py_eureka_client.eureka_client as eureka_client
from stt_service.app import main as stt_main
from tts_service.app import main as tts_main
from dotenv import load_dotenv
import threading
import time
import os

load_dotenv()

EUREKA_SERVER = os.getenv("EUREKA_SERVER_URL")
APP_NAME = "SPEECH-SERVICE"
SERVICE_PORT = 4000

def start_services():
    threading.Thread(target=stt_main, daemon=True).start()
    threading.Thread(target=tts_main, daemon=True).start()
    print("🚀 STT e TTS rodando...")

if __name__ == "__main__":
    eureka_client.init(eureka_server=EUREKA_SERVER,
                       app_name=APP_NAME,
                       instance_port=SERVICE_PORT)

    print(f"✅ {APP_NAME} registrado no Eureka Server em {EUREKA_SERVER}")

    start_services()
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("⏹ Serviço finalizado.")