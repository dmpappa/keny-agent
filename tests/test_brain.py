import sys
sys.path.append('.')
from src.brain import KenyBrain

print("🧠 Probando el cerebro de Keny...")
keny = KenyBrain()
keny.test_connection()

print("\n--- Prueba de conversación ---")
respuesta = keny.think("Mario dice: Che Keny, ¿qué pensás del fútbol argentino?")
print(f"Keny: {respuesta}")