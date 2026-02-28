"""
Service de transcription audio avec GROQ (Whisper Large v3)
Remplace le Whisper local (base) par l'API Groq — gratuit, plus rapide, plus précis.

Setup:
    pip install groq
    Créer un compte sur https://console.groq.com → API Keys → créer une clé
    Ajouter dans .env :  GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxx
"""

import os
import subprocess
from groq import Groq

class VoiceAnalyzer:
    """Service de transcription audio via Groq API (Whisper Large v3)"""

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "❌ GROQ_API_KEY manquant !\n"
                "1. Inscrivez-vous gratuitement sur https://console.groq.com\n"
                "2. Allez dans API Keys → créez une clé\n"
                "3. Ajoutez dans votre .env :  GROQ_API_KEY=gsk_xxxxxxxx"
            )
        self.client = Groq(api_key=api_key)

        # Modèle recommandé — whisper-large-v3 = meilleure précision (FR + AR)
        # Alternative plus rapide : whisper-large-v3-turbo
        self.model = os.getenv("GROQ_WHISPER_MODEL", "whisper-large-v3")

        self.ffmpeg_path = self._find_ffmpeg()

        print(f"✅ Groq Whisper initialisé — modèle: {self.model}")
        if self.ffmpeg_path:
            print(f"✅ FFmpeg trouvé: {self.ffmpeg_path}")
        else:
            print("⚠️  FFmpeg non trouvé — conversion audio limitée")

    # ------------------------------------------------------------------
    def transcribe(self, audio_path: str) -> str:
        """
        Transcrire un fichier audio via l'API Groq.
        Supporte WAV, MP3, WebM, OGG, M4A, FLAC, MP4.
        """
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Fichier introuvable : {audio_path}")

        file_size = os.path.getsize(audio_path)
        ext = os.path.splitext(audio_path)[1].lower()
        print(f"📂 Transcription : {os.path.basename(audio_path)} ({ext}, {file_size} bytes)")

        if file_size < 100:
            raise ValueError("Fichier audio trop petit ou vide")

        # Groq accepte nativement : flac, mp3, mp4, mpeg, mpga, m4a, ogg, wav, webm
        # Pour les autres formats, convertir en wav
        wav_path = None
        try:
            needs_conversion = ext not in {".flac", ".mp3", ".mp4", ".m4a", ".ogg", ".wav", ".webm", ".mpeg", ".mpga"}
            if needs_conversion:
                wav_path = self._convert_to_wav(audio_path)
                transcribe_path = wav_path
            else:
                transcribe_path = audio_path

            # Groq limite les fichiers à 25 Mo (free) — vérifier
            if os.path.getsize(transcribe_path) > 25 * 1024 * 1024:
                print("⚠️  Fichier > 25 Mo, conversion en wav 16kHz pour réduire la taille...")
                wav_path = self._convert_to_wav(transcribe_path)
                transcribe_path = wav_path

            with open(transcribe_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    file=(os.path.basename(transcribe_path), audio_file),
                    model=self.model,
                    # Ne PAS forcer la langue — Groq détecte automatiquement FR et AR
                    # Si vous voulez forcer : language="fr" ou language="ar"
                    prompt=(
                        "Transcription spécialisée pour seniors tunisiens (Hackathon SeniorVoice). "
                        "Le locuteur peut avoir une voix tremblante ou faible, bafouiller, hésiter (euh, bah, ben, mmm), "
                        "ou faire des pauses. Il mélange souvent le français et l'arabe dialectal tunisien (darija). "
                        "Mots courants : rappel, médicament, Doliprane, météo, agenda, urgence, "
                        "نحب نعيط، ذكرني، شنوة الطقس، قداش الساعة، عاوني، نجدة. "
                        "Transcrivez exactement ce qui est dit en tolérant les hésitations."
                    ),
                    response_format="text",
                    temperature=0.0,  # 0 = plus déterministe, meilleur pour commandes vocales
                )

            # response est une str quand response_format="text"
            transcription = str(response).strip()
            print(f"✅ Transcription : {transcription[:120]}...")
            return transcription

        except Exception as e:
            print(f"❌ Erreur Groq : {e}")
            raise
        finally:
            if wav_path and os.path.exists(wav_path) and wav_path != audio_path:
                try:
                    os.remove(wav_path)
                except OSError:
                    pass

    # ------------------------------------------------------------------
    def _find_ffmpeg(self) -> str:
        """Trouver FFmpeg (système ou imageio-ffmpeg)"""
        # Système
        try:
            result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
            if result.returncode == 0:
                return "ffmpeg"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # imageio-ffmpeg
        try:
            import imageio_ffmpeg
            path = imageio_ffmpeg.get_ffmpeg_exe()
            if os.path.exists(path):
                ffmpeg_dir = os.path.dirname(path)
                if ffmpeg_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
                return path
        except ImportError:
            pass

        return None