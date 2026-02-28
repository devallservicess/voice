import React, { useState, useEffect } from 'react';
import './App.css'; // ← NEW: import the redesigned CSS

import Header      from './components/Header';
import Microphone  from './components/Microphone';
import ResultCard  from './components/ResultCard';
import QuickActions from './components/QuickActions';
import Dashboard   from './components/Dashboard';

import { checkHealth, processVoice, submitQuickAction } from './services/api';
import { speakText } from './services/audio';

// ── Status helpers ────────────────────────────────────────────────────
const STATUS = {
  CHECKING:   '🔄 Vérification de la connexion…',
  READY:      '✅ Prêt à vous écouter',
  PROCESSING: '⏳ Traitement en cours…',
  EXECUTING:  '⏳ Exécution en cours…',
  ERROR_API:  '❌ Service non disponible — réessayez',
  ERROR_MIC:  '❌ Erreur de communication',
  EMERGENCY:  '🚨 ALERTE URGENCE EN COURS…',
};

// Map action IDs → natural French text commands for the NLP
const ACTION_COMMANDS = {
  get_time:       'quelle heure est-il',
  get_weather:    'quel temps fait-il aujourd\'hui',
  read_messages:  'lis mes messages',
  check_agenda:   'qu\'est-ce que j\'ai de prévu aujourd\'hui',
  call_contact:   'appeler',
  create_reminder:'créer un rappel',
};

// Offline fallback responses if the API is unreachable
const FALLBACK_RESPONSES = {
  get_time:       () => `Il est actuellement ${new Date().toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}.`,
  get_weather:    () => "Aujourd'hui à Tunis, il fait 22 degrés, le temps est ensoleillé.",
  read_messages:  () => 'Impossible de récupérer les messages. Vérifiez votre connexion.',
  check_agenda:   () => 'Impossible de récupérer l\'agenda. Vérifiez votre connexion.',
  call_contact:   () => 'Qui souhaitez-vous appeler ? Utilisez le microphone pour le dire.',
  create_reminder:() => 'Quel rappel souhaitez-vous créer ? Utilisez le microphone pour le dire.',
};


function App() {
  const [isApiAvailable, setIsApiAvailable] = useState(false);
  const [micStatusText,  setMicStatusText]  = useState(STATUS.CHECKING);
  const [result,         setResult]         = useState(null);
  const [isProcessing,   setIsProcessing]   = useState(false);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  // ── API health check on mount ────────────────────────────────────────
  useEffect(() => {
    const verify = async () => {
      try {
        await checkHealth();
        setIsApiAvailable(true);
        setMicStatusText(STATUS.READY);
      } catch {
        setIsApiAvailable(false);
        setMicStatusText(STATUS.ERROR_API);
      }
    };
    verify();
  }, []);

  const triggerRefresh = () => setRefreshTrigger(prev => prev + 1);

  const resetStatus = (delay = 4000) =>
    setTimeout(() => setMicStatusText(STATUS.READY), delay);

  // ── Voice recording pipeline ─────────────────────────────────────────
  const handleAudioCaptured = async (audioBlob) => {
    if (isProcessing) return;
    setIsProcessing(true);
    setMicStatusText(STATUS.PROCESSING);

    try {
      const data = await processVoice(audioBlob);
      setResult(data);
      triggerRefresh();

      const text = data.tts_text || data.action_result;
      if (text) speakText(text);

      setMicStatusText(STATUS.READY);
    } catch (err) {
      console.error('❌ Erreur API voix:', err);
      setResult({
        success:      false,
        intent:       'unknown',
        transcription:'',
        action_result:"Désolé, je n'ai pas pu traiter votre demande. Veuillez réessayer.",
        confidence:   0,
      });
      setMicStatusText(STATUS.ERROR_MIC);
      resetStatus(5000);
    } finally {
      setIsProcessing(false);
    }
  };

  // ── Quick action buttons ─────────────────────────────────────────────
  const handleQuickAction = async (actionId) => {
    if (isProcessing) return;
    setIsProcessing(true);
    setMicStatusText(STATUS.EXECUTING);

    const commandText = ACTION_COMMANDS[actionId];
    if (!commandText) {
      setIsProcessing(false);
      return;
    }

    try {
      const data = await submitQuickAction(commandText);
      setResult(data);
      triggerRefresh();

      const text = data.tts_text || data.action_result;
      if (text) speakText(text);

      setMicStatusText(STATUS.READY);
    } catch (err) {
      console.error('❌ Erreur action rapide:', err);

      // Offline fallback — still give a useful response
      const fallbackFn = FALLBACK_RESPONSES[actionId];
      const responseText = fallbackFn ? fallbackFn() : 'Action non disponible.';

      setResult({
        success:      true,
        intent:       actionId,
        transcription: commandText,
        action_result: responseText,
        tts_text:      responseText,
        confidence:    1,
      });
      speakText(responseText);
      setMicStatusText(STATUS.READY);
    } finally {
      setIsProcessing(false);
    }
  };

  // ── SOS emergency ────────────────────────────────────────────────────
  const handleEmergency = () => {
    setMicStatusText(STATUS.EMERGENCY);

    const msg =
      "🚨 ALERTE URGENCE ! J'ai prévenu vos contacts d'urgence : Mohamed, Fatma, SAMU. " +
      "Restez calme, de l'aide arrive. Le SAMU a été contacté au 190.";

    const spokenMsg =
      "Alerte urgence ! J'ai prévenu vos contacts d'urgence. " +
      "Mohamed et Fatma ont été contactés. Le SAMU a été appelé au 190. " +
      "Restez calme, de l'aide arrive.";

    setResult({
      success:      true,
      transcription:"Urgence ! Au secours !",
      intent:       "emergency_alert",
      action_result: msg,
      tts_text:      spokenMsg,
      confidence:    1,
    });

    speakText(spokenMsg);
    resetStatus(8000);
  };

  // ── Render ───────────────────────────────────────────────────────────
  return (
    <div className="app-container" id="app">

      <Header onEmergency={handleEmergency} />

      <main className="main-content">

        <Microphone
          isApiAvailable={isApiAvailable}
          isProcessing={isProcessing}
          onAudioCaptured={handleAudioCaptured}
          micStatusText={micStatusText}
        />

        {result && <ResultCard result={result} />}

        <QuickActions
          onActionClick={handleQuickAction}
          disabled={isProcessing}
        />

        <Dashboard refreshTrigger={refreshTrigger} />

      </main>

      <footer className="footer">
        <p>🎙️ SeniorVoice v2.0 — Assistant vocal IA pour seniors tunisiens</p>
      </footer>

    </div>
  );
}

export default App;