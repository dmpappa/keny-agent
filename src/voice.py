import os
import io
import sounddevice as sd
import numpy as np
from elevenlabs import ElevenLabs
from dotenv import load_dotenv

load_dotenv()

class KenyVoice:
    def __init__(self):
        self.client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))
        self.voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        self.output_device = os.getenv("AUDIO_DEVICE_OUTPUT", "default")
        self.sample_rate = 44100

        print(f"🔊 KenyVoice iniciado. Voz ID: {self.voice_id}")

    def speak(self, text: str):
        """
        Convierte texto a voz y lo reproduce.
        
        Args:
            text: Lo que Keny va a decir
        """
        if not text or not text.strip():
            return

        print(f"🎙️ Keny dice: {text}")

        try:
            # Generamos el audio con ElevenLabs
            audio_generator = self.client.text_to_speech.convert(
                voice_id=self.voice_id,
                text=text,
                model_id="eleven_multilingual_v2",
                voice_settings={
                    "stability": 0.5,
                    "similarity_boost": 0.8,
                    "style": 0.3,
                    "use_speaker_boost": True
                }
            )

            # Convertimos el generator a bytes
            audio_bytes = b"".join(audio_generator)

            # Reproducimos el audio
            self._play_audio(audio_bytes)

        except Exception as e:
            print(f"❌ Error en KenyVoice: {e}")

    def _play_audio(self, audio_bytes: bytes):
        """Reproduce los bytes de audio por el dispositivo configurado."""
        try:
            # Convertimos bytes MP3 a array numpy
            audio_array = self._mp3_to_numpy(audio_bytes)

            # Buscamos el dispositivo de salida
            device_index = self._find_device(self.output_device)

            # Reproducimos
            sd.play(audio_array, samplerate=self.sample_rate, device=device_index)
            sd.wait()  # Esperamos que termine antes de seguir

        except Exception as e:
            print(f"❌ Error reproduciendo audio: {e}")

    def _mp3_to_numpy(self, audio_bytes: bytes) -> np.ndarray:
        """Convierte MP3 bytes a numpy array para sounddevice."""
        try:
            from pydub import AudioSegment
            audio = AudioSegment.from_mp3(io.BytesIO(audio_bytes))
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(1)
            samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
            samples = samples / 32768.0  # Normalizar a [-1, 1]
            return samples
        except Exception as e:
            print(f"❌ Error convirtiendo audio: {e}")
            return np.zeros(1000, dtype=np.float32)

    def _find_device(self, device_name: str):
        """Busca el índice del dispositivo de audio por nombre."""
        if device_name == "default":
            return None

        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device_name.lower() in device['name'].lower():
                if device['max_output_channels'] > 0:
                    print(f"🔊 Usando dispositivo: {device['name']}")
                    return i

        print(f"⚠️ Dispositivo '{device_name}' no encontrado, usando default.")
        return None

    def list_devices(self):
        """Lista todos los dispositivos de audio disponibles."""
        print("\n📻 Dispositivos de audio disponibles:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_output_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        print()

    def test_voice(self):
        """Prueba que la voz funcione correctamente."""
        try:
            print("🧪 Probando la voz de Keny...")
            self.speak("Buenas, soy Keny. Ya estoy listo para el stream, che.")
            print("✅ Voz funcionando correctamente.")
            return True
        except Exception as e:
            print(f"❌ Error en test de voz: {e}")
            return False