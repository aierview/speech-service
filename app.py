from stt_service.app import main as stt_main
from tts_service.app import main as tts_main
import threading

if __name__ == "__main__":
    threading.Thread(target=stt_main, daemon=True).start()
    threading.Thread(target=tts_main, daemon=True).start()
    print("🚀 Speech Service rodando com STT e TTS ativos...")
    while True:
        pass
