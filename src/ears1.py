import os
import numpy as np
import sounddevice as sd
from openai import OpenAI
from dotenv import load_dotenv
import tempfile
import wave

load_dotenv()

class KenyEars:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        self.sample_rate = 44100
        # ✅ CORREGIDO: usamos 44100 Hz que es lo que soporta
        # el micrófono Realtek detectado en tu sistema
        # Antes era 16000 Hz y causaba conflicto
        
        self.channels = 1
        # Mono — suficiente para voz humana
        
        self.chunk_duration = 0.5
        # Chunks de medio segundo para ir procesando el audio
        
        self.silence_threshold = 0.01
        # Tu micrófono tiene buena señal (0.3045 max)
        # Este umbral es correcto para tu setup
        
        self.silence_duration = 1.5
        # 1.5 segundos de silencio = Mario terminó de hablar
        
        self.whisper_rate = 16000
        # Whisper prefiere 16000 Hz internamente
        # Convertimos al guardar el WAV
        
        print("👂 KenyEars iniciado.")
        print(f"   Dispositivo: {sd.query_devices(kind='input')['name']}")
        print(f"   Sample rate: {self.sample_rate} Hz")

    def _is_silence(self, audio_chunk: np.ndarray) -> bool:
        """Detecta si un chunk de audio es silencio por RMS."""
        rms = np.sqrt(np.mean(audio_chunk ** 2))
        return rms < self.silence_threshold

    def _record_until_silence(self) -> np.ndarray:
        """Graba hasta detectar silencio prolongado."""
        chunk_samples = int(self.sample_rate * self.chunk_duration)
        # 44100 × 0.5 = 22050 muestras por chunk
        
        recorded_chunks = []
        silence_chunks = 0
        silence_limit = int(self.silence_duration / self.chunk_duration)
        # 1.5 / 0.5 = 3 chunks de silencio = fin del habla
        
        started_speaking = False

        print("🎤 Escuchando a Mario...")

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='float32'
            ) as stream:
                while True:
                    chunk, overflowed = stream.read(chunk_samples)
                    
                    if overflowed:
                        print("⚠️ Buffer overflow — procesando igual")
                    
                    chunk_flat = chunk.flatten()

                    if not self._is_silence(chunk_flat):
                        # Hay sonido — Mario está hablando
                        if not started_speaking:
                            print("🗣️ Detectando voz...")
                        started_speaking = True
                        silence_chunks = 0
                        recorded_chunks.append(chunk_flat)
                    else:
                        # Silencio
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
        """
        Convierte de 44100 Hz a 16000 Hz para Whisper.
        Whisper funciona mejor con 16000 Hz.
        """
        # Ratio de conversión
        ratio = self.whisper_rate / self.sample_rate
        # Nuevo número de muestras
        new_length = int(len(audio) * ratio)
        # Índices originales y nuevos
        old_indices = np.linspace(0, len(audio) - 1, len(audio))
        new_indices = np.linspace(0, len(audio) - 1, new_length)
        # Interpolación lineal para resamplear
        return np.interp(new_indices, old_indices, audio)

    def _transcribe(self, audio: np.ndarray) -> str:
        """Transcribe el audio con Whisper via OpenAI API."""
        if len(audio) == 0:
            return ""

        # Resampleamos de 44100 a 16000 para Whisper
        audio_16k = self._resample(audio)

        # Guardamos como WAV temporal
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            with wave.open(tmp_path, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)           # 16 bits
                wav_file.setframerate(self.whisper_rate)  # 16000 Hz
                audio_int16 = (audio_16k * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())

            # Enviamos a Whisper
            with open(tmp_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="es"
                )
            return response.text.strip()

        except Exception as e:
            print(f"❌ Error en transcripción: {e}")
            return ""
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass

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
        """Lista dispositivos de entrada disponibles."""
        print("\n🎤 Dispositivos de entrada disponibles:")
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                print(f"  [{i}] {device['name']} "
                      f"(max rate: {device['default_samplerate']} Hz)")
        print()

    def test_ears(self):
        """Prueba micrófono + Whisper."""
        print("🧪 Probando los oídos de Keny...")
        print("📢 Hablá algo en el micrófono cuando veas el 🎤\n")
        texto = self.listen_once()
        if texto:
            print(f"✅ Transcripción OK: '{texto}'")
            return True
        else:
            print("❌ No se detectó voz o falló la transcripción.")
            return False