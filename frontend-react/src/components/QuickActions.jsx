import React from 'react';

const actions = [
  { id: 'get_time',       icon: '🕐', label: 'Quelle heure ?', color: 'ac-blue'   },
  { id: 'get_weather',    icon: '🌤️', label: 'Météo',          color: 'ac-orange' },
  { id: 'read_messages',  icon: '💬', label: 'Messages',        color: 'ac-green'  },
  { id: 'check_agenda',   icon: '📅', label: 'Agenda',          color: 'ac-purple' },
  { id: 'call_contact',   icon: '📞', label: 'Appeler',         color: 'ac-teal'   },
  { id: 'create_reminder',icon: '⏰', label: 'Rappel',          color: 'ac-pink'   },
];

const QuickActions = ({ onActionClick }) => (
  <section className="quick-section" id="quickActions">
    <h2 className="section-title">⚡ Actions rapides</h2>
    <div className="actions-grid">
      {actions.map(({ id, icon, label, color }) => (
        <button
          key={id}
          className="action-card"
          onClick={() => onActionClick(id)}
          aria-label={label}
        >
          <div className={`action-icon-wrap ${color}`}>{icon}</div>
          <span className="action-name">{label}</span>
        </button>
      ))}
    </div>
  </section>
);

export default QuickActions;