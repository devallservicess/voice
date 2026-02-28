import React from 'react';
import { speakText } from '../services/audio';

const intentLabels = {
  create_reminder: '⏰ Rappel créé',
  call_contact: '📞 Appel contact',
  get_weather: '🌤️ Météo',
  get_time: '🕐 Heure',
  add_medication: '💊 Médicament',
  read_messages: '💬 Messages',
  send_message: '✉️ Message envoyé',
  set_alarm: '⏰ Alarme',
  check_agenda: '📅 Agenda',
  emergency_alert: '🚨 URGENCE',
  unknown: '❓ Non compris',
  error: '⚠️ Erreur',
};

const ResultCard = ({ result }) => {
  if (!result) return null;

  const intentLabel = intentLabels[result.intent] || result.intent || 'Résultat';
  const isEmergency = result.intent === 'emergency_alert';

  // Try every possible field name the backend might use
  const responseText =
    result.tts_text ||
    result.action_result ||
    result.response_text ||
    result.message ||
    (result.success === false
      ? "Je n'ai pas pu exécuter cette action. Veuillez réessayer."
      : "Je n'ai pas de réponse pour le moment.");

  const transcriptionText =
    result.transcription ||
    result.raw_text ||
    result.text ||
    '—';

  const confidence = typeof result.confidence === 'number'
    ? Math.round(result.confidence * 100)
    : null;

  // Message list if backend sent structured messages
  const messages =
    result.action_data?.messages ||
    result.data?.messages ||
    [];

  return (
    <section className="result-section" id="resultSection">
      <div className={`result-card glass ${isEmergency ? 'emergency-glow' : ''}`}>

        {/* Top bar */}
        <div className="result-top"
          style={isEmergency ? { background: 'var(--red)' } : {}}>
          <span className="result-badge">
            <span>{result.success ? '✅' : '⚠️'}</span>
            {intentLabel}
          </span>
          {confidence !== null && confidence > 0 && (
            <span style={{ fontSize: '.78rem', color: 'rgba(255,255,255,.55)', fontWeight: 600 }}>
              {confidence}% confiance
            </span>
          )}
        </div>

        {/* Body */}
        <div className="result-body">
          <div className="result-block transcription-block">
            <div className="result-label">🎤 Ce que j'ai compris</div>
            <p>{transcriptionText}</p>
          </div>
          <div className="result-block response-block">
            <div className="result-label">🤖 Ma réponse</div>
            <p style={{ whiteSpace: 'pre-line' }}>{responseText}</p>
          </div>
        </div>

        {/* Inline message list when reading messages */}
        {messages.length > 0 && (
          <div style={{ padding: '0 24px 20px' }}>
            <div style={{ borderRadius: 16, overflow: 'hidden', border: '1.5px solid var(--cream-dark)' }}>
              {messages.map((msg, i) => (
                <div key={i} style={{
                  display: 'flex', alignItems: 'flex-start', gap: 12,
                  padding: '12px 16px',
                  background: i % 2 === 0 ? 'var(--cream)' : 'var(--white)',
                  borderBottom: i < messages.length - 1 ? '1px solid var(--cream-dark)' : 'none',
                }}>
                  <span style={{ fontSize: '1.2rem', flexShrink: 0 }}>
                    {msg.direction === 'received' ? '📩' : '📤'}
                  </span>
                  <div>
                    <div style={{ fontWeight: 700, fontSize: '.9rem', color: 'var(--text-dark)' }}>
                      {msg.from || 'Inconnu'}
                    </div>
                    <div style={{ fontSize: '.88rem', color: 'var(--text-mid)', marginTop: 2 }}>
                      {msg.content}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="result-actions">
          <button className="btn-listen" onClick={() => speakText(responseText)}>
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"
              width="20" height="20">
              <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" />
              <path d="M19.07 4.93a10 10 0 0 1 0 14.14" />
              <path d="M15.54 8.46a5 5 0 0 1 0 7.07" />
            </svg>
            Écouter la réponse
          </button>
        </div>

      </div>
    </section>
  );
};

export default ResultCard;