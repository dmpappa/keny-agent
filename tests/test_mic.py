import sys
sys.path.append('.')
import sounddevice as sd
import numpy as np

print("=" * 60)
print("DIAGNÓSTICO COMPLETO DE AUDIO")
print("=" * 60)

# 1. Listar TODOS los dispositivos (entrada Y salida)
print("\n📋 TODOS los dispositivos de audio:")
print(sd.query_devices())

# 2. Dispositivo por defecto del sistema
print("\n🎯 Dispositivo de ENTRADA por defecto:")
print(sd.query_devices(kind='input'))

# 3. Probar captura de audio 3 segundos
print("\n🎤 Grabando 3 segundos... HABLÁ AHORA")
try:
    duracion = 3
    sample_rate = 16000
    grabacion = sd.rec(
        int(duracion * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype='float32'
    )
    sd.wait()
    
    volumen_max = np.max(np.abs(grabacion))
    volumen_rms = np.sqrt(np.mean(grabacion**2))
    
    print(f"✅ Grabación completada")
    print(f"   Volumen máximo detectado: {volumen_max:.4f}")
    print(f"   Volumen RMS:              {volumen_rms:.4f}")
    
    if volumen_max < 0.001:
        print("   ⚠️  Sin señal — el micrófono no está capturando nada")
    elif volumen_max < 0.01:
        print("   ⚠️  Señal muy baja — ajustar silence_threshold")
    else:
        print("   ✅ Señal OK — el micrófono funciona correctamente")
        
except Exception as e:
    print(f"❌ Error: {e}")