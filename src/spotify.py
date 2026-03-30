import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

load_dotenv()

class KenySpotify:
    def __init__(self):
        print("🎵 Iniciando KenySpotify...")

        # Scopes — permisos que le pedimos a Spotify
        # user-modify-playback-state → play, pause, next, volume
        # user-read-playback-state   → leer estado actual
        # user-read-currently-playing → qué está sonando
        scope = (
            "user-modify-playback-state "
            "user-read-playback-state "
            "user-read-currently-playing"
        )

        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope=scope,
                # Guarda el token en un archivo local
                # La primera vez abre el navegador para autorizar
                cache_path=".spotify_cache"
            )
        )

        print("✅ KenySpotify listo.")

    def _get_active_device(self):
        """Busca el dispositivo activo de Spotify."""
        devices = self.sp.devices()
        if not devices["devices"]:
            print("⚠️ No hay dispositivos Spotify activos. Abrí Spotify.")
            return None

        # Buscamos el dispositivo activo
        for device in devices["devices"]:
            if device["is_active"]:
                return device["id"]

        # Si ninguno está activo, usamos el primero disponible
        return devices["devices"][0]["id"]

    def play(self, query: str) -> str:
        """
        Busca y reproduce música por texto.
        query puede ser: artista, canción, género, playlist, etc.
        """
        try:
            device_id = self._get_active_device()
            if not device_id:
                return "No encontré ningún dispositivo Spotify activo, che."

            # Primero intentamos buscar como track
            results = self.sp.search(q=query, type="track", limit=1)
            tracks = results["tracks"]["items"]

            if tracks:
                track = tracks[0]
                track_name = track["name"]
                artist_name = track["artists"][0]["name"]
                track_uri = track["uri"]

                self.sp.start_playback(
                    device_id=device_id,
                    uris=[track_uri]
                )
                return f"Dale, poniéndote '{track_name}' de {artist_name}."

            # Si no encontramos track, buscamos playlist
            results = self.sp.search(q=query, type="playlist", limit=1)
            playlists = results["playlists"]["items"]

            if playlists:
                playlist = playlists[0]
                playlist_name = playlist["name"]
                playlist_uri = playlist["uri"]

                self.sp.start_playback(
                    device_id=device_id,
                    context_uri=playlist_uri
                )
                return f"Poniendo la playlist '{playlist_name}', dale."

            return f"No encontré nada para '{query}' en Spotify, che."

        except Exception as e:
            print(f"❌ Error en Spotify: {e}")
            return "Hubo un error con Spotify, revisá que esté abierto."

    def pause(self) -> str:
        """Pausa la reproducción."""
        try:
            self.sp.pause_playback()
            return "Pausado."
        except Exception as e:
            print(f"❌ Error pausando: {e}")
            return "No pude pausar, revisá que haya algo sonando."

    def resume(self) -> str:
        """Reanuda la reproducción."""
        try:
            self.sp.start_playback()
            return "Dale, seguimos."
        except Exception as e:
            print(f"❌ Error reanudando: {e}")
            return "No pude reanudar la reproducción."

    def next_track(self) -> str:
        """Salta a la siguiente canción."""
        try:
            self.sp.next_track()
            return "Siguiente, dale."
        except Exception as e:
            print(f"❌ Error: {e}")
            return "No pude pasar a la siguiente."

    def previous_track(self) -> str:
        """Vuelve a la canción anterior."""
        try:
            self.sp.previous_track()
            return "Volvemos a la anterior."
        except Exception as e:
            print(f"❌ Error: {e}")
            return "No pude volver a la anterior."

    def set_volume(self, volume: int) -> str:
        """
        Ajusta el volumen entre 0 y 100.
        """
        volume = max(0, min(100, volume))
        try:
            device_id = self._get_active_device()
            self.sp.volume(volume, device_id=device_id)
            return f"Volumen al {volume}%."
        except Exception as e:
            print(f"❌ Error: {e}")
            return "No pude cambiar el volumen."

    def what_is_playing(self) -> str:
        """Dice qué está sonando actualmente."""
        try:
            current = self.sp.current_playback()
            if not current or not current.get("is_playing"):
                return "No hay nada sonando en este momento."

            track = current["item"]
            name = track["name"]
            artist = track["artists"][0]["name"]
            return f"Está sonando '{name}' de {artist}."
        except Exception as e:
            print(f"❌ Error: {e}")
            return "No pude obtener la canción actual."

    def detect_command(self, text: str) -> str:
        """
        Detecta comandos de Spotify en el texto y los ejecuta.
        Retorna la respuesta de Keny o None si no hay comando de Spotify.
        """
        text_lower = text.lower()

        # Pausar
        if any(w in text_lower for w in ["pausá", "pausa", "pará la música", "stop música"]):
            return self.pause()

        # Reanudar
        if any(w in text_lower for w in ["seguí", "continuá", "play", "reanudá"]):
            return self.resume()

        # Siguiente
        if any(w in text_lower for w in ["siguiente", "próxima", "skip", "pasá"]):
            return self.next_track()

        # Anterior
        if any(w in text_lower for w in ["anterior", "volvé", "atrás"]):
            return self.previous_track()

        # Qué suena
        if any(w in text_lower for w in ["qué suena", "qué está sonando", "qué canción", "qué tema"]):
            return self.what_is_playing()

        # Volumen
        if "volumen" in text_lower or "subí" in text_lower or "bajá" in text_lower:
            if "subí" in text_lower or "más volumen" in text_lower:
                return self.set_volume(80)
            if "bajá" in text_lower or "menos volumen" in text_lower:
                return self.set_volume(30)
            if "silencio" in text_lower or "muteá" in text_lower:
                return self.set_volume(0)

        # Reproducir música — el más importante
        triggers = ["poneme", "poné", "tocá", "reproducí", "buscá en spotify", "ponme"]
        for trigger in triggers:
            if trigger in text_lower:
                # Extraemos qué quiere escuchar
                # "poneme jazz tranquilo" → "jazz tranquilo"
                idx = text_lower.find(trigger)
                query = text[idx + len(trigger):].strip()
                if query:
                    return self.play(query)

        return None
        # Retorna None si el texto no tiene comando de Spotify
        # Así main.py sabe que debe pasarlo a brain.py normalmente