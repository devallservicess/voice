"""
Service TTS pour SeniorVoice
Text-to-Speech - retourne le texte de la réponse vocale
(pas de génération mp3, juste du texte pour affichage et lecture côté frontend)
"""


class TTSService:
    """Service de synthèse vocale (texte uniquement, pas de génération de fichiers audio)"""

    def __init__(self):
        print("✅ Service TTS initialisé (mode texte)")

    def generate_response(self, text: str) -> dict:
        """
        Préparer la réponse vocale

        Args:
            text: Texte à convertir en parole

        Returns:
            {"text": str, "speech_rate": str}
        """
        return {
            "text": text,
            "speech_rate": "slow",  # Débit lent pour seniors
        }
