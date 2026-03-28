import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class KenyBrain:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.max_tokens = int(os.getenv("KENY_MAX_TOKENS", 150))
        self.conversation_history = []
        
        # Personalidad de Keny
        self.system_prompt = """
        Sos Keny, el co-conductor virtual del programa de streaming 
        "No Preguntes por Rusia" de Mario Pergolini en YouTube.

        TU PERSONALIDAD:
        - Hablás con acento rioplatense auténtico (usás "vos", "che", "dale", "re", "posta")
        - Sos irónico, inteligente y con humor ácido pero nunca agresivo
        - Conocés a fondo a todos los columnistas del programa
        - Hacés comentarios cortos, directos y con timing perfecto
        - Nunca hablás de más, sabés cuándo callar
        - Tratás a Mario de igual a igual, con respeto pero sin reverencia

        TUS REGLAS DE ORO:
        - Respondés en MÁXIMO 2 oraciones
        - Nunca repetís lo que Mario acaba de decir
        - Si te presentan a un columnista, lo hacés con humor y un dato curioso
        - Si no tenés nada bueno para decir, decís algo corto y dejás pasar
        - Usás jerga rioplatense natural, no forzada

        EJEMPLOS DE CÓMO HABLÁS:
        - "Dale Mario, ya era hora que lo llames a este."
        - "Che, menos mal que llegó, yo ya me estaba quedando dormido."
        - "Posta que este tipo sabe de lo que habla, a diferencia de otros."
        """

    def think(self, user_message: str, context: str = "") -> str:
        """
        Procesa un mensaje y genera la respuesta de Keny.
        
        Args:
            user_message: Lo que dijo Mario
            context: Contexto adicional (ej: nombre del columnista a presentar)
        
        Returns:
            La respuesta de Keny como string
        """
        # Armamos el mensaje con contexto si hay
        full_message = user_message
        if context:
            full_message = f"{user_message}\n[CONTEXTO: {context}]"

        # Agregamos al historial
        self.conversation_history.append({
            "role": "user",
            "content": full_message
        })

        # Llamamos a Claude
        response = self.client.messages.create(
            model="claude-opus-4-5",
            max_tokens=self.max_tokens,
            system=self.system_prompt,
            messages=self.conversation_history
        )

        # Extraemos la respuesta
        keny_response = response.content[0].text

        # Guardamos en el historial
        self.conversation_history.append({
            "role": "assistant",
            "content": keny_response
        })

        # Limitamos el historial a las últimas 10 interacciones
        # para no gastar tokens innecesarios
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

        return keny_response

    def reset_conversation(self):
        """Resetea el historial — útil entre bloques del programa."""
        self.conversation_history = []
        print("🧠 Keny: memoria reseteada.")

    def test_connection(self) -> bool:
        """Verifica que la conexión con Claude funciona."""
        try:
            response = self.think("Decí hola en una sola oración corta.")
            print(f"✅ Conexión OK. Keny dice: {response}")
            return True
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False