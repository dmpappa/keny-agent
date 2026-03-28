import sys
sys.path.append('.')
from src.voice import KenyVoice

keny_voice = KenyVoice()

# Ver qué dispositivos tenés disponibles
keny_voice.list_devices()

# Probar la voz
keny_voice.test_voice()


"""import sys
sys.path.append('.')
from src.voice import KenyVoice

keny_voice = KenyVoice()

# Ver qué dispositivos tenés disponibles
keny_voice.list_devices()

# Probar la voz
keny_voice.test_voice()
"""