import React, { useEffect, useState } from 'react';
import { getReminders, getMedications, getContacts, getMessages } from '../services/api';

const Panel = ({ title, headerClass, children, loading }) => (
  <div className="dash-panel">
    <div className={`panel-header ${headerClass}`}>{title}</div>
    <div className="panel-body">
      {loading
        ? <div className="panel-loading"><div className="spinner" /> Chargement…</div>
        : children}
    </div>
  </div>
);

const Dashboard = ({ refreshTrigger }) => {
  const [reminders,    setReminders]    = useState([]);
  const [medications,  setMedications]  = useState([]);
  const [contacts,     setContacts]     = useState([]);
  const [messages,     setMessages]     = useState([]);
  const [loading,      setLoading]      = useState(true);

  useEffect(() => {
    setLoading(true);
    Promise.allSettled([
      getReminders().then(d  => d.success  && setReminders(d.reminders)),
      getMedications().then(d => d.success  && setMedications(d.medications)),
      getContacts().then(d    => d.success  && setContacts(d.contacts)),
      getMessages().then(d    => d.success  && setMessages(d.messages)),
    ]).finally(() => setLoading(false));
  }, [refreshTrigger]);

  return (
    <section className="dashboard-section" id="dashboard">
      <h2 className="section-title">📊 Tableau de bord</h2>
      <div className="dashboard-grid">

        <Panel title="⏰ Mes Rappels" headerClass="ph-amber" loading={loading}>
          {reminders.length > 0
            ? reminders.map((r, i) => (
                <div key={i} className="dash-item">
                  <span className="dash-item-title">{r.title}</span>
                  <span className="dash-item-detail">🕐 {r.reminder_time}</span>
                </div>
              ))
            : <p className="dash-empty">Aucun rappel</p>}
        </Panel>

        <Panel title="💊 Mes Médicaments" headerClass="ph-red" loading={loading}>
          {medications.length > 0
            ? medications.map((m, i) => (
                <div key={i} className="dash-item">
                  <span className="dash-item-title">💊 {m.name}{m.dosage ? ` (${m.dosage})` : ''}</span>
                  <span className="dash-item-detail">🕐 {m.schedule_time}</span>
                </div>
              ))
            : <p className="dash-empty">Aucun médicament</p>}
        </Panel>

        <Panel title="👥 Mes Contacts" headerClass="ph-blue" loading={loading}>
          {contacts.length > 0
            ? contacts.map((c, i) => (
                <div key={i} className={`dash-item ${c.is_emergency ? 'dash-item-emergency' : ''}`}>
                  <span className="dash-item-title">{c.is_emergency ? '🚨 ' : '👤 '}{c.name}</span>
                  <span className="dash-item-detail">{c.relation || c.phone}</span>
                </div>
              ))
            : <p className="dash-empty">Aucun contact</p>}
        </Panel>

        <Panel title="💬 Messages récents" headerClass="ph-green" loading={loading}>
          {messages.length > 0
            ? messages.map((m, i) => (
                <div key={i} className="dash-item">
                  <span className="dash-item-title">
                    {m.direction === 'received' ? '📩' : '📤'} {m.contact_name || 'Inconnu'}
                  </span>
                  <span className="dash-item-detail">
                    {m.content.length > 45 ? m.content.slice(0, 45) + '…' : m.content}
                  </span>
                </div>
              ))
            : <p className="dash-empty">Aucun message</p>}
        </Panel>

      </div>
    </section>
  );
};

export default Dashboard;