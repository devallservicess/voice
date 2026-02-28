import React, { useState, useRef } from 'react';

const Microphone = ({ onAudioCaptured, isApiAvailable, micStatusText }) => {
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef  = useRef([]);

  const handleMicClick = async () => {
    if (!isApiAvailable) return;
    isRecording ? stopRecording() : await startRecording();
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          sampleRate: 16000,
          echoCancellation: true,
          noiseSuppression: true,
        },
      });

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      const mediaRecorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current   = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        onAudioCaptured(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('❌ Erreur micro:', err);
      alert('Microphone non disponible. Vérifiez les permissions.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  return (
    <section className="mic-section" id="micSection">
      <div className="mic-wrapper">
        <p className="mic-instruction" id="micInstruction">
          {isRecording
            ? '🔴 Parlez maintenant… Appuyez pour arrêter'
            : 'Appuyez sur le micro pour parler'}
        </p>

        <div className="mic-btn-container">
          {!isRecording && <div className="mic-ring mic-ring-1" />}
          {!isRecording && <div className="mic-ring mic-ring-2" />}

          <button
            className={`mic-btn ${isRecording ? 'recording' : ''}`}
            id="micBtn"
            aria-label={isRecording ? 'Arrêter l\'enregistrement' : 'Démarrer l\'enregistrement'}
            onClick={handleMicClick}
            disabled={!isApiAvailable}
          >
            {isRecording ? (
              /* Stop icon with liquid wave background */
              <>
                <div className="mic-wave-container">
                  <div className="mic-wave" style={{ animationDelay: '0s' }}></div>
                  <div className="mic-wave" style={{ animationDelay: '1s', opacity: 0.5 }}></div>
                </div>
                <svg viewBox="0 0 24 24" fill="currentColor" className="mic-svg" style={{ color: 'white', zIndex: 3, width: 36, height: 36 }}>
                  <rect x="6" y="6" width="12" height="12" rx="2" />
                </svg>
              </>
            ) : (
              /* Mic icon */
              <svg className="mic-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                <line x1="12" y1="19" x2="12" y2="23" />
                <line x1="8"  y1="23" x2="16" y2="23" />
              </svg>
            )}
            {isRecording && <div className="mic-pulse" />}
          </button>
        </div>

        <p className="mic-status" id="micStatus">{micStatusText}</p>
      </div>
    </section>
  );
};

export default Microphone;