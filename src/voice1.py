import os
import asyncio
import tempfile
import edge_tts
import pygame
import sounddevice as sd
from dotenv import load_dotenv

load_dotenv()

class KenyVoice:
    def __init__(self):
        self.voice = "es-AR-TomasNeural"
        self.output_device = os.getenv("AUDIO_DEVICE_OUTPUT", "default")
        
        # Inicializamos pygame para audio
        pygame.mixer.init()
        print(f"🔊 KenyVoice iniciado con voz: {self.voice}")

    def speak(self, text: str):
        """Convierte texto a voz y lo reproduce."""
        if not text or not text.strip():
            return
        print(f"🎙️ Keny dice: {text}")
        try:
            asyncio.run(self._speak_async(text))
        except Exception as e:
            print(f"❌ Error en KenyVoice: {e}")

    async def _speak_async(self, text: str):
        """Genera y reproduce el audio."""
        communicate = edge_tts.Communicate(text, self.voice)

        # Guardamos como MP3 temporal
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        await communicate.save(tmp_path)
        self._play_mp3(tmp_path)

        # Limpiamos
        try:
            os.unlink(tmp_path)
        except:
            pass

    def _play_mp3(self, file_path: str):
        """Reproduce MP3 directo con pygame — sin ffmpeg."""
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            
            # Esperamos que termine
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
        except Exception as e:
            print(f"❌ Error reproduciendo: {e}")

    def list_devices(self):
        """Lista dispositivos de audio disponibles."""
        print("\n📻 Dispositivos de audio disponibles:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        print()

    def test_voice(self):
        """Prueba la voz."""
        try:
            print("🧪 Probando la voz de Keny...")
            self.speak("Buenas, soy Keny. Ya estoy listo para el stream, che.")
            print("✅ Voz funcionando correctamente.")
            return True
        except Exception as e:
            print(f"❌ Error en test de voz: {e}")
            return False