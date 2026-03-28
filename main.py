import os
import sys
import time
import threading
from dotenv import load_dotenv
from src.brain import KenyBrain
from src.ears import KenyEars
from src.voice import KenyVoice

load_dotenv()

# ─────────────────────────────────────────
# Comandos de voz para controlar a Keny
# ─────────────────────────────────────────
STOP_COMMANDS = ["para keny", "stop keny", "salir", "cerrar", "chau keny"]
RESET_COMMANDS = ["nueva conversación", "empezar de nuevo", "olvidá todo"]

class KenyAssistant:
    def __init__(self):
        print("\n" + "="*50)
        print("🤖 KENY — Asistente Personal de Voz")
        print("="*50)
        print("Iniciando módulos...\n")

        # Inicializamos los tres módulos principales
        self.brain = KenyBrain()
        self.ears  = KenyEars(model_size="small")
        self.voice = KenyVoice()

        self.running = False
        # Flag para controlar el loop principal
        # Cuando es False, el agente se detiene limpiamente

        print("\n✅ Keny listo para escucharte.")
        print("💡 Decí 'para Keny' o 'salir' para detenerlo.\n")

    def _is_stop_command(self, text: str) -> bool:
        """Detecta si el usuario quiere parar el agente."""
        text_lower = text.lower().strip()
        return any(cmd in text_lower for cmd in STOP_COMMANDS)

    def _is_reset_command(self, text: str) -> bool:
        """Detecta si el usuario quiere resetear la conversación."""
        text_lower = text.lower().strip()
        return any(cmd in text_lower for cmd in RESET_COMMANDS)

    def _process_turn(self, text: str) -> bool:
        """
        Procesa un turno de conversación.
        
        Returns:
            False si hay que detener el agente, True si continúa
        """
        # ¿Quiere parar?
        if self._is_stop_command(text):
            self.voice.speak("Dale, me apago. Hasta la próxima.")
            return False

        # ¿Quiere resetear la conversación?
        if self._is_reset_command(text):
            self.brain.reset_conversation()
            self.voice.speak("Listo, empezamos de cero.")
            return True

        # Procesamiento normal — Keny piensa y responde
        print("🧠 Procesando...")
        response = self.brain.think(text)
        self.voice.speak(response)
        return True

    def run(self):
        """Loop principal del asistente."""
        self.running = True

        # Saludo inicial
        self.voice.speak(
            "Buenas, soy Keny. ¿En qué te puedo ayudar?"
        )

        # Loop infinito de conversación
        while self.running:
            try:
                # 1. Escuchamos al usuario
                text = self.ears.listen_once()

                # 2. Si no detectó nada, seguimos escuchando
                if not text or not text.strip():
                    continue

                # 3. Procesamos el turno
                should_continue = self._process_turn(text)

                if not should_continue:
                    self.running = False
                    break

                # Pequeña pausa entre turnos para que no se solapen
                time.sleep(0.3)

            except KeyboardInterrupt:
                # Ctrl+C en la terminal
                print("\n⚠️ Interrumpido por el usuario.")
                self.voice.speak("Me interrumpiste, che. Hasta luego.")
                break

            except Exception as e:
                # Cualquier error no crítico — lo logueamos y seguimos
                print(f"⚠️ Error en el turno: {e}")
                time.sleep(1)
                continue

        print("\n👋 Keny detenido.")


def main():
    """Punto de entrada principal."""
    try:
        keny = KenyAssistant()
        keny.run()
    except Exception as e:
        print(f"\n❌ Error crítico al iniciar Keny: {e}")
        print("Verificá que el micrófono esté conectado y el .env configurado.")
        sys.exit(1)


if __name__ == "__main__":
    main()