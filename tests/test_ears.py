import sys
sys.path.append('.')
from src.ears import KenyEars

keny_ears = KenyEars()

# Ver micrófonos disponibles
keny_ears.list_input_devices()

# Probar — hablá algo cuando diga "Escuchando"
keny_ears.test_ears()