from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============ Voice Processing ============

class VoiceProcessingResponse(BaseModel):
    """Réponse principale du pipeline vocal"""
    success: bool
    transcription: str = ""
    intent: str = ""
    confidence: float = 0.0
    entities: Dict[str, Any] = {}
    action_result: str = ""
    action_data: Dict[str, Any] = {}
    tts_text: str = ""


# ============ Contacts ============

class ContactBase(BaseModel):
    name: str
    phone: str
    relation: str = ""
    is_emergency: bool = False

class ContactResponse(ContactBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ContactListResponse(BaseModel):
    success: bool
    contacts: List[ContactResponse]


# ============ Reminders ============

class ReminderBase(BaseModel):
    title: str
    reminder_time: str = ""
    reminder_type: str = "general"

class ReminderResponse(ReminderBase):
    id: int
    is_done: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ReminderListResponse(BaseModel):
    success: bool
    reminders: List[ReminderResponse]


# ============ Medications ============

class MedicationBase(BaseModel):
    name: str
    dosage: str = ""
    schedule_time: str = ""
    notes: str = ""

class MedicationResponse(MedicationBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MedicationListResponse(BaseModel):
    success: bool
    medications: List[MedicationResponse]


# ============ Messages ============

class MessageBase(BaseModel):
    content: str
    contact_id: Optional[int] = None
    direction: str = "received"

class MessageResponse(MessageBase):
    id: int
    contact_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    success: bool
    messages: List[MessageResponse]


# ============ Agenda ============

class AgendaItem(BaseModel):
    type: str  # "reminder", "medication", "alarm"
    title: str
    time: str
    is_done: bool = False

class AgendaResponse(BaseModel):
    success: bool
    items: List[AgendaItem]


# ============ Action History ============

class ActionHistoryItem(BaseModel):
    id: int
    transcription: str
    detected_intent: str
    action_result: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ActionHistoryResponse(BaseModel):
    success: bool
    history: List[ActionHistoryItem]