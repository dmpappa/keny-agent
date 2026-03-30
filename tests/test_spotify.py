import sys
sys.path.append('.')
from src.spotify import KenySpotify

print("🎵 Probando KenySpotify...")
spotify = KenySpotify()

# La primera vez abre el navegador para autorizar — es normal
print("\n1. ¿Qué está sonando?")
print(spotify.what_is_playing())

print("\n2. Buscando jazz tranquilo...")
print(spotify.play("jazz tranquilo"))