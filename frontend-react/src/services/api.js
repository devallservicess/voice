const API_URL = 'http://localhost:8000/api';

export const processVoice = async (audioBlob) => {
    const formData = new FormData();
    formData.append('audio_file', audioBlob, 'recording.webm');

    const response = await fetch(`${API_URL}/process-voice`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Erreur serveur: ${response.status}`);
    }

    return await response.json();
};

export const checkHealth = async () => {
    try {
        const response = await fetch(`${API_URL}/health`);
        return await response.json();
    } catch (error) {
        console.error('API Health Check Failed', error);
        throw error;
    }
};

export const getReminders = async () => {
    const response = await fetch(`${API_URL}/reminders`);
    return await response.json();
};

export const getMedications = async () => {
    const response = await fetch(`${API_URL}/medications`);
    return await response.json();
};

export const getContacts = async () => {
    const response = await fetch(`${API_URL}/contacts`);
    return await response.json();
};

export const getMessages = async () => {
    const response = await fetch(`${API_URL}/messages`);
    return await response.json();
};

/**
 * submitQuickAction — envoie une commande textuelle directement au pipeline NLP+Action
 * sans passer par Whisper (pas besoin d'audio pour les actions rapides).
 */
export const submitQuickAction = async (commandText) => {
    const response = await fetch(`${API_URL}/process-text`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: commandText }),
    });

    if (!response.ok) {
        throw new Error(`Erreur action rapide: ${response.status}`);
    }

    return await response.json();
};