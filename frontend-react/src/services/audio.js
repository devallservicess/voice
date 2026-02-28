// TTS (Synthèse vocale navigateur)
export const speakText = (text) => {
    if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel(); // Annuler toute lecture en cours

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'fr-FR';
        utterance.rate = 0.85;  // Débit lent pour seniors
        utterance.pitch = 1.0;
        utterance.volume = 1.0;

        // Chercher une voix française
        const voices = window.speechSynthesis.getVoices();
        const frenchVoice = voices.find(v => v.lang.startsWith('fr'));
        if (frenchVoice) {
            utterance.voice = frenchVoice;
        }

        window.speechSynthesis.speak(utterance);
    }
};

// Ensure voices are loaded on some browsers
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}
