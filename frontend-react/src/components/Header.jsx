import React from 'react';

const Header = ({ onEmergency }) => {
  return (
    <header className="header" id="header">
      <div className="header-left">
        <div className="header-logo">🎙️</div>
        <div className="header-text">
          <h1>SeniorVoice</h1>
          <p>Votre assistant vocal intelligent</p>
        </div>
      </div>
      <button
        className="sos-btn"
        id="sosBtn"
        title="Appeler les urgences"
        onClick={onEmergency}
        aria-label="Bouton SOS urgence"
      >
        <span className="sos-icon">🚨</span>
        <span className="sos-label">SOS</span>
      </button>
    </header>
  );
};

export default Header;