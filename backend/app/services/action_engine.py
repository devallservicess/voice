"""
Moteur d'actions SeniorVoice
Exécute les 10 commandes vocales et retourne des réponses textuelles
"""

from typing import Dict, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..database import Contact, Reminder, Medication, Message, ActionHistory


class ActionEngine:
    """Moteur d'exécution des commandes vocales"""

    def __init__(self):
        self.action_handlers = {
            "create_reminder": self._handle_create_reminder,
            "call_contact": self._handle_call_contact,
            "get_weather": self._handle_get_weather,
            "get_time": self._handle_get_time,
            "add_medication": self._handle_add_medication,
            "read_messages": self._handle_read_messages,
            "send_message": self._handle_send_message,
            "set_alarm": self._handle_set_alarm,
            "check_agenda": self._handle_check_agenda,
            "emergency_alert": self._handle_emergency_alert,
            "unknown": self._handle_unknown,
        }

    def execute(self, intent: str, entities: Dict, db: Session) -> Dict:
        """
        Exécuter l'action correspondant à l'intention détectée

        Args:
            intent: Intention détectée par le NLP
            entities: Entités extraites
            db: Session de base de données

        Returns:
            {"success": bool, "response_text": str, "action": str, "data": dict}
        """
        handler = self.action_handlers.get(intent, self._handle_unknown)

        try:
            result = handler(entities, db)

            # Sauvegarder dans l'historique
            history = ActionHistory(
                transcription=entities.get("_raw_text", ""),
                detected_intent=intent,
                entities_json=str(entities),
                action_result=result.get("response_text", "")
            )
            db.add(history)
            db.commit()

            return result

        except Exception as e:
            print(f"❌ Erreur action '{intent}': {e}")
            return {
                "success": False,
                "response_text": "Désolé, une erreur s'est produite. Veuillez réessayer.",
                "action": intent,
                "data": {}
            }

    # ==================== Handlers ====================

    def _handle_create_reminder(self, entities: Dict, db: Session) -> Dict:
        """Créer un rappel"""
        title = entities.get("reminder_title", "")
        time = entities.get("time", "")

        if not title:
            return {
                "success": False,
                "response_text": "Quel rappel souhaitez-vous créer ? Dites par exemple : rappelle-moi de prendre mon médicament à 8 heures.",
                "action": "create_reminder",
                "data": {"needs": "reminder_title"}
            }

        reminder = Reminder(
            title=title,
            reminder_time=time if time else "non défini",
            reminder_type="general"
        )
        db.add(reminder)
        db.commit()

        time_text = f" à {time}" if time else ""
        return {
            "success": True,
            "response_text": f"D'accord ! J'ai créé un rappel : {title}{time_text}. Je vous préviendrai au moment voulu.",
            "action": "create_reminder",
            "data": {"reminder_id": reminder.id, "title": title, "time": time}
        }

    def _handle_call_contact(self, entities: Dict, db: Session) -> Dict:
        """Appeler un contact"""
        contact_name = entities.get("contact", "")

        if not contact_name:
            # Lister les contacts disponibles
            contacts = db.query(Contact).limit(5).all()
            names = [c.name for c in contacts]
            return {
                "success": False,
                "response_text": f"Qui souhaitez-vous appeler ? Vos contacts sont : {', '.join(names)}.",
                "action": "call_contact",
                "data": {"needs": "contact", "available_contacts": names}
            }

        # Chercher le contact
        contact = db.query(Contact).filter(
            Contact.name.ilike(f"%{contact_name}%")
        ).first()

        if contact:
            return {
                "success": True,
                "response_text": f"J'appelle {contact.name} au {contact.phone}. L'appel est en cours.",
                "action": "call_contact",
                "data": {"contact_name": contact.name, "phone": contact.phone}
            }
        else:
            return {
                "success": False,
                "response_text": f"Je n'ai pas trouvé de contact nommé {contact_name}. Voulez-vous essayer un autre nom ?",
                "action": "call_contact",
                "data": {"searched": contact_name}
            }

    def _handle_get_weather(self, entities: Dict, db: Session) -> Dict:
        """Donner la météo (simulée pour la démo)"""
        now = datetime.now()
        # Météo simulée pour la démo
        weather_data = {
            "temperature": 22,
            "condition": "ensoleillé",
            "humidity": 55,
            "city": "Tunis"
        }

        return {
            "success": True,
            "response_text": f"Aujourd'hui à {weather_data['city']}, il fait {weather_data['temperature']} degrés, "
                           f"le temps est {weather_data['condition']} avec une humidité de {weather_data['humidity']} pourcent. "
                           f"C'est une belle journée !",
            "action": "get_weather",
            "data": weather_data
        }

    def _handle_get_time(self, entities: Dict, db: Session) -> Dict:
        """Donner l'heure actuelle"""
        now = datetime.now()
        hour = now.strftime("%H")
        minute = now.strftime("%M")

        # Format naturel
        if int(minute) == 0:
            time_text = f"{hour} heures pile"
        else:
            time_text = f"{hour} heures et {minute} minutes"

        # Ajouter contexte de la journée
        h = int(hour)
        if h < 12:
            period = "Bon matin !"
        elif h < 18:
            period = "Bon après-midi !"
        else:
            period = "Bonne soirée !"

        return {
            "success": True,
            "response_text": f"Il est actuellement {time_text}. {period}",
            "action": "get_time",
            "data": {"time": now.strftime("%H:%M"), "period": period}
        }

    def _handle_add_medication(self, entities: Dict, db: Session) -> Dict:
        """Ajouter un médicament"""
        med_name = entities.get("medication", "")
        time = entities.get("time", "")

        if not med_name:
            return {
                "success": False,
                "response_text": "Quel médicament souhaitez-vous ajouter ? Dites par exemple : ajouter Doliprane à 8 heures.",
                "action": "add_medication",
                "data": {"needs": "medication"}
            }

        medication = Medication(
            name=med_name,
            schedule_time=time if time else "à définir",
            dosage="",
            notes=""
        )
        db.add(medication)
        db.commit()

        time_text = f" à prendre à {time}" if time else ""
        return {
            "success": True,
            "response_text": f"J'ai ajouté le médicament {med_name}{time_text} à votre liste. N'oubliez pas de le prendre !",
            "action": "add_medication",
            "data": {"medication_id": medication.id, "name": med_name}
        }

    def _handle_read_messages(self, entities: Dict, db: Session) -> Dict:
        """Lire les messages — supporte le filtrage par nom de contact"""
        contact_filter = entities.get("contact", "").strip()

        # Construire la requête de base
        query = db.query(Message).order_by(Message.created_at.desc())

        # Si un nom de contact est mentionné, filtrer par ce contact
        filtered_contact = None
        if contact_filter:
            filtered_contact = db.query(Contact).filter(
                Contact.name.ilike(f"%{contact_filter}%")
            ).first()
            if filtered_contact:
                query = query.filter(Message.contact_id == filtered_contact.id)
            # Si le contact n'existe pas, on montre tous les messages quand même

        messages = query.limit(5).all()

        # Construire le préfixe selon le filtre appliqué
        if contact_filter and filtered_contact:
            prefix = f"Messages de {filtered_contact.name} : "
        elif contact_filter and not filtered_contact:
            prefix = f"Je n'ai pas trouvé de contact nommé {contact_filter}. Voici tous vos messages : "
        else:
            prefix = ""

        if not messages:
            if contact_filter and filtered_contact:
                response_text = f"Aucun message de {filtered_contact.name} pour le moment."
            else:
                response_text = "Vous n'avez aucun message pour le moment."
            return {
                "success": True,
                "response_text": response_text,
                "action": "read_messages",
                "data": {"messages": []}
            }

        msg_texts = []
        msg_data = []
        for msg in messages:
            contact = db.query(Contact).filter(Contact.id == msg.contact_id).first() if msg.contact_id else None
            sender = contact.name if contact else "Inconnu"
            direction = "de" if msg.direction == "received" else "envoyé à"
            msg_texts.append(f"Message {direction} {sender} : {msg.content}")
            msg_data.append({
                "from": sender,
                "content": msg.content,
                "direction": msg.direction,
                "date": msg.created_at.isoformat() if msg.created_at else ""
            })

        count = len(messages)
        response_text = (
            f"{prefix}Vous avez {count} message{'s' if count > 1 else ''}. "
            + " … ".join(msg_texts)
        )

        return {
            "success": True,
            "response_text": response_text,
            "action": "read_messages",
            "data": {"messages": msg_data}
        }

    def _handle_send_message(self, entities: Dict, db: Session) -> Dict:
        """Envoyer un message"""
        contact_name = entities.get("contact", "")
        content = entities.get("message_content", "")

        if not contact_name:
            return {
                "success": False,
                "response_text": "À qui souhaitez-vous envoyer un message ?",
                "action": "send_message",
                "data": {"needs": "contact"}
            }

        if not content:
            return {
                "success": False,
                "response_text": f"Que souhaitez-vous dire à {contact_name} ?",
                "action": "send_message",
                "data": {"needs": "message_content", "contact": contact_name}
            }

        # Trouver le contact
        contact = db.query(Contact).filter(
            Contact.name.ilike(f"%{contact_name}%")
        ).first()

        contact_id = contact.id if contact else None
        display_name = contact.name if contact else contact_name

        message = Message(
            contact_id=contact_id,
            content=content,
            direction="sent"
        )
        db.add(message)
        db.commit()

        return {
            "success": True,
            "response_text": f"Message envoyé à {display_name} : \"{content}\"",
            "action": "send_message",
            "data": {"contact": display_name, "content": content}
        }

    def _handle_set_alarm(self, entities: Dict, db: Session) -> Dict:
        """Mettre une alarme"""
        time = entities.get("time", "")

        if not time:
            return {
                "success": False,
                "response_text": "À quelle heure souhaitez-vous l'alarme ? Dites par exemple : mets une alarme à 7 heures.",
                "action": "set_alarm",
                "data": {"needs": "time"}
            }

        # Sauvegarder comme rappel de type alarme
        reminder = Reminder(
            title=f"⏰ Alarme à {time}",
            reminder_time=time,
            reminder_type="alarm"
        )
        db.add(reminder)
        db.commit()

        return {
            "success": True,
            "response_text": f"L'alarme est réglée pour {time}. Je vous réveillerai à l'heure.",
            "action": "set_alarm",
            "data": {"time": time, "reminder_id": reminder.id}
        }

    def _handle_check_agenda(self, entities: Dict, db: Session) -> Dict:
        """Consulter l'agenda"""
        # Rappels non faits
        reminders = db.query(Reminder).filter(Reminder.is_done == False).all()
        # Médicaments
        medications = db.query(Medication).all()

        items = []
        if reminders:
            for r in reminders:
                items.append(f"Rappel : {r.title} à {r.reminder_time}")
        if medications:
            for m in medications:
                items.append(f"Médicament : {m.name} ({m.schedule_time})")

        if not items:
            return {
                "success": True,
                "response_text": "Votre agenda est vide pour le moment. Pas de rendez-vous ni de rappels prévus.",
                "action": "check_agenda",
                "data": {"items": []}
            }

        response_text = f"Voici votre programme : {'. '.join(items)}."

        return {
            "success": True,
            "response_text": response_text,
            "action": "check_agenda",
            "data": {"reminders": len(reminders), "medications": len(medications), "items": items}
        }

    def _handle_emergency_alert(self, entities: Dict, db: Session) -> Dict:
        """Alerte d'urgence"""
        # Récupérer les contacts d'urgence
        emergency_contacts = db.query(Contact).filter(Contact.is_emergency == True).all()

        contacts_info = []
        for c in emergency_contacts:
            contacts_info.append({"name": c.name, "phone": c.phone})

        names = [c.name for c in emergency_contacts]

        return {
            "success": True,
            "response_text": f"🚨 ALERTE URGENCE ! J'ai prévenu vos contacts d'urgence : {', '.join(names)}. "
                           f"Restez calme, de l'aide arrive. Le SAMU a été contacté au 190.",
            "action": "emergency_alert",
            "data": {"emergency_contacts": contacts_info, "samu_called": True}
        }

    def _handle_unknown(self, entities: Dict, db: Session) -> Dict:
        """Intention non reconnue"""
        return {
            "success": False,
            "response_text": "Je n'ai pas bien compris votre demande. Pouvez-vous répéter s'il vous plaît ? "
                           "Vous pouvez me demander par exemple : l'heure, la météo, appeler quelqu'un, "
                           "créer un rappel, ou lire vos messages.",
            "action": "unknown",
            "data": {}
        }