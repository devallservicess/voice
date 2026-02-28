from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Créer le dossier database s'il n'existe pas
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
os.makedirs(DATABASE_DIR, exist_ok=True)

DATABASE_URL = f"sqlite:///{os.path.join(DATABASE_DIR, 'seniorvoice.db')}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============ Modèles de données SeniorVoice ============

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    relation = Column(String, default="")  # famille, ami, médecin, etc.
    is_emergency = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    messages = relationship("Message", back_populates="contact")


class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    reminder_time = Column(String, nullable=False)  # ex: "08:00", "14:30"
    reminder_type = Column(String, default="general")  # medical, general
    is_done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dosage = Column(String, default="")
    schedule_time = Column(String, default="")  # ex: "08:00, 20:00"
    notes = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    content = Column(Text, nullable=False)
    direction = Column(String, default="received")  # sent / received
    created_at = Column(DateTime, default=datetime.utcnow)

    contact = relationship("Contact", back_populates="messages")


class ActionHistory(Base):
    __tablename__ = "action_history"

    id = Column(Integer, primary_key=True, index=True)
    audio_filename = Column(String, default="")
    transcription = Column(Text, default="")
    detected_intent = Column(String, default="")
    entities_json = Column(Text, default="{}")
    action_result = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


# ============ Fonctions utilitaires ============

def init_db():
    """Créer toutes les tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Obtenir une session de base de données"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_db():
    """Pré-remplir la base avec des données d'exemple pour la démo"""
    db = SessionLocal()
    try:
        # Ne seeder que si la base est vide
        if db.query(Contact).count() > 0:
            return

        # Contacts d'exemple
        contacts = [
            Contact(name="Mohamed", phone="+216 20 123 456", relation="fils", is_emergency=True),
            Contact(name="Fatma", phone="+216 25 789 012", relation="fille", is_emergency=True),
            Contact(name="Dr. Ben Said", phone="+216 71 234 567", relation="médecin", is_emergency=False),
            Contact(name="Amina", phone="+216 22 345 678", relation="voisine", is_emergency=False),
            Contact(name="SAMU", phone="190", relation="urgence", is_emergency=True),
        ]
        for c in contacts:
            db.add(c)

        # Médicaments d'exemple
        medications = [
            Medication(name="Doliprane", dosage="500mg", schedule_time="08:00, 20:00", notes="Après le repas"),
            Medication(name="Amlodipine", dosage="5mg", schedule_time="08:00", notes="Pour la tension"),
            Medication(name="Metformine", dosage="850mg", schedule_time="08:00, 13:00, 20:00", notes="Pour le diabète"),
        ]
        for m in medications:
            db.add(m)

        # Rappels d'exemple
        reminders = [
            Reminder(title="Prendre Doliprane", reminder_time="08:00", reminder_type="medical"),
            Reminder(title="Rendez-vous Dr. Ben Said", reminder_time="10:00", reminder_type="medical"),
            Reminder(title="Appeler Mohamed", reminder_time="18:00", reminder_type="general"),
        ]
        for r in reminders:
            db.add(r)

        # Messages d'exemple
        messages = [
            Message(contact_id=1, content="Bonjour papa, comment tu vas aujourd'hui?", direction="received"),
            Message(contact_id=2, content="Maman, n'oublie pas ton médicament ce soir", direction="received"),
            Message(contact_id=1, content="Je vais bien, merci mon fils", direction="sent"),
        ]
        for msg in messages:
            db.add(msg)

        db.commit()
        print("✅ Base de données pré-remplie avec des données d'exemple")
    except Exception as e:
        print(f"⚠️ Erreur lors du seed: {e}")
        db.rollback()
    finally:
        db.close()