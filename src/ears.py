import os
import numpy as np
import sounddevice as sd
import whisper
import tempfile
import wave
from dotenv import load_dotenv

load_dotenv()

class KenyEars:
    def __init__(self, model_size="small"):
        print("👂 Cargando modelo Whisper LOCAL...")
        print(f"   Modelo: {model_size}")
        print("   (la primera vez descarga ~244MB, esperá...)")
        
        self.model = whisper.load_model(model_size)
        # ✅ Whisper corre en tu PC — sin API, sin costo, sin internet
        
        self.sample_rate = 44100
        self.channels = 1
        self.chunk_duration = 0.5
        self.silence_threshold = 0.01
        self.silence_duration = 1.5
        self.whisper_rate = 16000
        
        print("✅ KenyEars listo — 100% offline y gratuito")
        print(f"   Dispositivo: {sd.query_devices(kind='input')['name']}")

    def _is_silence(self, audio_chunk: np.ndarray) -> bool:
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        return rms < self.silence_threshold

    def _record_until_silence(self) -> np.ndarray:
        chunk_samples = int(self.sample_rate * self.chunk_duration)
        recorded_chunks = []
        silence_chunks = 0
        silence_limit = int(self.silence_duration / self.chunk_duration)
        started_speaking = False

        print("🎤 Escuchando a Mario...")

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            ) as stream:
                while True:
                    chunk, _ = stream.read(chunk_samples)
                    chunk_flat = chunk.flatten()

                    if not self._is_silence(chunk_flat):
                        if not started_speaking:
                            print("🗣️ Detectando voz...")
                        started_speaking = True
                        silence_chunks = 0
                        recorded_chunks.append(chunk_flat)
                    else:
                        if started_speaking:
                            silence_chunks += 1
                            recorded_chunks.append(chunk_flat)
                            if silence_chunks >= silence_limit:
                                print("⏹️ Silencio detectado, procesando...")
                                break

        except Exception as e:
            print(f"❌ Error grabando: {e}")
            return np.array([])

        if not recorded_chunks:
            return np.array([])

        return np.concatenate(recorded_chunks)

    def _resample(self, audio: np.ndarray) -> np.ndarray:
        """Convierte 44100 Hz → 16000 Hz para Whisper."""
        ratio = self.whisper_rate / self.sample_rate
        new_length = int(len(audio) * ratio)
        old_indices = np.linspace(0, len(audio) - 1, len(audio))
        new_indices = np.linspace(0, len(audio) - 1, new_length)
        return np.interp(new_indices, old_indices, audio)

    def _transcribe(self, audio: np.ndarray) -> str:
        """Transcribe con Whisper LOCAL — sin API ni internet."""
        if len(audio) == 0:
            return ""

        print("🧠 Transcribiendo con Whisper local...")

        # Convertimos a 16000 Hz
        audio_16k = self._resample(audio)

        # Normalizamos el volumen
        max_val = np.max(np.abs(audio_16k))
        if max_val > 0:
            audio_16k = audio_16k / max_val

        try:
            result = self.model.transcribe(
                audio_16k.astype(np.float32),
                language="es",
                fp16=False
                # fp16=False porque no tenemos GPU Nvidia
                # En CPU siempre va False
            )
            return result["text"].strip()

        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return ""

    def listen_once(self) -> str:
        """Escucha una vez y devuelve el texto transcripto."""
        audio = self._record_until_silence()
        if len(audio) == 0:
            return ""
        texto = self._transcribe(audio)
        if texto:
            print(f"📝 Mario dijo: '{texto}'")
        return texto

    def list_input_devices(self):
        print("\n🎤 Dispositivos de entrada disponibles:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']}")
        print()

    def test_ears(self):
        print("🧪 Probando los oídos de Keny...")
        print("📢 Hablá algo en el micrófono cuando veas el 🎤\n")
        texto = self.listen_once()
        if texto:
            print(f"✅ Transcripción OK: '{texto}'")
            return True
        else:
            print("❌ No se detectó voz o falló la transcripción.")
            return False