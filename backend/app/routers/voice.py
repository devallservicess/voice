from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import os
import shutil
from datetime import datetime


class TextCommandRequest(BaseModel):
    text: str

from ..database import get_db, Contact, Reminder, Medication, Message, ActionHistory
from ..models.schemas import (
    VoiceProcessingResponse,
    ContactListResponse, ContactResponse, ContactBase,
    ReminderListResponse, ReminderResponse,
    MedicationListResponse, MedicationResponse,
    MessageListResponse, MessageResponse,
    AgendaResponse, AgendaItem,
    ActionHistoryResponse, ActionHistoryItem,
)
from ..services.audio_analyzer import VoiceAnalyzer
from ..services.nlp_processor import NLPProcessor
from ..services.action_engine import ActionEngine
from ..services.tts_service import TTSService

router = APIRouter(prefix="/api", tags=["seniorvoice"])

# Initialiser les services
analyzer = VoiceAnalyzer()
nlp = NLPProcessor()
action_engine = ActionEngine()
tts = TTSService()

# Dossier pour les fichiers uploadés
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ==================== Pipeline Vocal Principal ====================

@router.post("/process-voice", response_model=VoiceProcessingResponse)
async def process_voice(
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Pipeline complet : Audio → Whisper → NLP → Action → TTS
    """
    try:
        # Vérifier le format
        allowed_extensions = [".wav", ".mp3", ".m4a", ".ogg", ".webm", ".mp4"]
        file_ext = os.path.splitext(audio_file.filename or "audio.webm")[1].lower()
        if not file_ext:
            file_ext = ".webm"

        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Format non supporté. Utilisez: {', '.join(allowed_extensions)}"
            )

        # Sauvegarder le fichier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"senior_{timestamp}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)

        print(f"📤 Audio reçu: {filename} ({os.path.getsize(file_path)} bytes)")

        # 1. Transcription Whisper
        print("🎤 Étape 1: Transcription...")
        transcription = analyzer.transcribe(file_path)

        # 2. Détection d'intention + entités (NLP)
        print("🧠 Étape 2: Analyse NLP...")
        nlp_result = nlp.process(transcription)

        # 3. Exécution de l'action
        print(f"⚡ Étape 3: Action '{nlp_result['intent']}'...")
        entities = nlp_result["entities"]
        entities["_raw_text"] = transcription
        action_result = action_engine.execute(nlp_result["intent"], entities, db)

        # 4. Réponse TTS (texte)
        print("🔊 Étape 4: Préparer la réponse...")
        tts_response = tts.generate_response(action_result["response_text"])

        print(f"✅ Pipeline terminé: intent={nlp_result['intent']}, success={action_result['success']}")

        return VoiceProcessingResponse(
            success=action_result["success"],
            transcription=transcription,
            intent=nlp_result["intent"],
            confidence=nlp_result["confidence"],
            entities=nlp_result["entities"],
            action_result=action_result["response_text"],
            action_data=action_result.get("data", {}),
            tts_text=tts_response["text"]
        )

    except Exception as e:
        print(f"❌ Erreur pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ==================== Pipeline Texte (Actions Rapides) ====================

@router.post("/process-text", response_model=VoiceProcessingResponse)
async def process_text(
    request: TextCommandRequest,
    db: Session = Depends(get_db)
):
    """
    Pipeline NLP+Action sans audio (pour les boutons d'actions rapides)
    Text → NLP → Action → TTS
    """
    try:
        text = request.text.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Texte vide")

        print(f"📝 Commande texte: {text}")

        # 1. NLP
        nlp_result = nlp.process(text)

        # 2. Action
        entities = nlp_result["entities"]
        entities["_raw_text"] = text
        action_result = action_engine.execute(nlp_result["intent"], entities, db)

        # 3. TTS text
        tts_response = tts.generate_response(action_result["response_text"])

        return VoiceProcessingResponse(
            success=action_result["success"],
            transcription=text,
            intent=nlp_result["intent"],
            confidence=nlp_result["confidence"],
            entities=nlp_result["entities"],
            action_result=action_result["response_text"],
            action_data=action_result.get("data", {}),
            tts_text=tts_response["text"]
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur process-text: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")


# ==================== Contacts ====================

@router.get("/contacts", response_model=ContactListResponse)
async def get_contacts(db: Session = Depends(get_db)):
    """Récupérer tous les contacts"""
    contacts = db.query(Contact).all()
    return ContactListResponse(
        success=True,
        contacts=[ContactResponse.model_validate(c) for c in contacts]
    )

@router.post("/contacts", response_model=ContactResponse)
async def create_contact(contact: ContactBase, db: Session = Depends(get_db)):
    """Ajouter un nouveau contact"""
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return ContactResponse.model_validate(db_contact)


# ==================== Rappels ====================

@router.get("/reminders", response_model=ReminderListResponse)
async def get_reminders(db: Session = Depends(get_db)):
    """Récupérer tous les rappels"""
    reminders = db.query(Reminder).order_by(Reminder.reminder_time).all()
    return ReminderListResponse(
        success=True,
        reminders=[ReminderResponse.model_validate(r) for r in reminders]
    )


# ==================== Médicaments ====================

@router.get("/medications", response_model=MedicationListResponse)
async def get_medications(db: Session = Depends(get_db)):
    """Récupérer tous les médicaments"""
    medications = db.query(Medication).all()
    return MedicationListResponse(
        success=True,
        medications=[MedicationResponse.model_validate(m) for m in medications]
    )


# ==================== Messages ====================

@router.get("/messages", response_model=MessageListResponse)
async def get_messages(db: Session = Depends(get_db)):
    """Récupérer les messages"""
    messages = db.query(Message).order_by(Message.created_at.desc()).limit(20).all()
    result = []
    for msg in messages:
        contact = db.query(Contact).filter(Contact.id == msg.contact_id).first() if msg.contact_id else None
        result.append(MessageResponse(
            id=msg.id,
            content=msg.content,
            contact_id=msg.contact_id,
            direction=msg.direction,
            contact_name=contact.name if contact else None,
            created_at=msg.created_at
        ))
    return MessageListResponse(success=True, messages=result)


# ==================== Agenda ====================

@router.get("/agenda", response_model=AgendaResponse)
async def get_agenda(db: Session = Depends(get_db)):
    """Récupérer l'agenda complet (rappels + médicaments)"""
    items = []

    reminders = db.query(Reminder).filter(Reminder.is_done == False).all()
    for r in reminders:
        items.append(AgendaItem(
            type=r.reminder_type or "reminder",
            title=r.title,
            time=r.reminder_time,
            is_done=r.is_done
        ))

    medications = db.query(Medication).all()
    for m in medications:
        items.append(AgendaItem(
            type="medication",
            title=f"{m.name} ({m.dosage})" if m.dosage else m.name,
            time=m.schedule_time,
            is_done=False
        ))

    return AgendaResponse(success=True, items=items)


# ==================== Historique ====================

@router.get("/history", response_model=ActionHistoryResponse)
async def get_history(db: Session = Depends(get_db)):
    """Récupérer l'historique des actions"""
    history = db.query(ActionHistory).order_by(ActionHistory.created_at.desc()).limit(20).all()
    return ActionHistoryResponse(
        success=True,
        history=[ActionHistoryItem.model_validate(h) for h in history]
    )


# ==================== Santé ====================

@router.get("/health")
async def health_check():
    """Vérifier que l'API fonctionne"""
    return {
        "status": "ok",
        "application": "SeniorVoice API",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "whisper": "loaded",
            "nlp": "ready",
            "action_engine": "ready",
            "tts": "ready"
        }
    }