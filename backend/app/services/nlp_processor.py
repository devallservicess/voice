"""
Module NLP pour SeniorVoice - VERSION CORRIGÉE
Détection d'intention et extraction d'entités
Supporte le français et l'arabe dialectal tunisien
"""

import re
from typing import Dict, List, Optional, Tuple


class NLPProcessor:
    """Processeur NLP pour détecter les intentions et extraire les entités"""

    def __init__(self):
        # ──────────────────────────────────────────────────────────────
        # INTENTIONS — chaque intent a :
        #   "keywords"      : mots isolés (score +1.0 chacun)
        #   "strong_keywords": mots très discriminants (score +2.0)
        #   "patterns"      : regex (score +1.5 chacun)
        #   "blockers"      : si présent dans le texte → score = 0
        # ──────────────────────────────────────────────────────────────
        self.intent_patterns = {

            # ── 1. CRÉER UN RAPPEL ──────────────────────────────────
            "create_reminder": {
                "strong_keywords": [
                    "rappelle-moi", "rappelle moi", "rappel", "rappeler",
                    "ذكرني", "فكرني", "ما تنساش", "نذكرك", "نبي نذكر",
                ],
                "keywords": [
                    "rappelle", "souviens", "souvenir", "n'oublie pas", "oublie pas",
                    "تذكير",
                ],
                "patterns": [
                    r"rappelle[- ]?moi",
                    r"cr[ée]+r?\s+(?:un\s+)?rappel",
                    r"ajouter?\s+(?:un\s+)?rappel",
                    r"mettre?\s+(?:un\s+)?rappel",
                    r"(?:n.)?oublie\s+pas\s+(?:de\s+|d.)",
                    r"ذكرني",
                    r"فكرني",
                ],
                "blockers": [],
            },

            # ── 2. APPELER UN CONTACT ───────────────────────────────
            "call_contact": {
                "strong_keywords": [
                    "appelle", "appeler", "téléphone", "téléphoner",
                    "نعيط", "عيط", "عيطلي", "نبي نعيط",
                    "اتصل", "كلم", "نكلم",
                ],
                "keywords": [
                    "appel", "contacter", "contact", "joindre", "passer un appel",
                    "نحب نعيط", "عيط لي",
                ],
                "patterns": [
                    r"appelle[rz]?\s+\w+",
                    r"passe[rz]?\s+(?:un\s+)?appel",
                    r"(?:je\s+)?(?:veux|voudrais)\s+appeler",
                    r"téléphone[rz]?\s+(?:à|au|a)\s+",
                    r"(?:نحب|بغيت|نبي)\s+(?:ن)?(?:عيط|كلم)",
                    r"عيط(?:لي)?\s+(?:ل|لـ)?",
                    r"اتصل\s+(?:ب|بـ)?",
                ],
                "blockers": [],
            },

            # ── 3. MÉTÉO ────────────────────────────────────────────
            "get_weather": {
                "strong_keywords": [
                    "météo", "meteo", "température", "pluie",
                    "طقس", "الطقس", "شنوة الطقس", "حالة الجو",
                ],
                "keywords": [
                    "nuageux", "pleuvoir", "ensoleillé", "vent",
                    "الجو", "مطر", "شمس", "برد", "سخونة",
                ],
                "patterns": [
                    r"quel\s+temps",
                    r"(?:la\s+)?météo",
                    r"est.ce\s+qu.il\s+(?:pleut|va\s+pleuvoir)",
                    r"il\s+(?:fait|va\s+faire)\s+(?:chaud|froid|beau)",
                    r"(?:il\s+)?(?:fait\s+)?chaud\s+(?:aujourd|dehors|demain)",
                    r"(?:شنوة|كيفاش)\s+(?:الطقس|الجو|حالة)",
                    r"(?:شنوة|شو)\s+الطقس",
                    r"حالة\s+الجو",
                ],
                "blockers": [],
            },

            # ── 4. HEURE ────────────────────────────────────────────
            "get_time": {
                "strong_keywords": [
                    "quelle heure", "l'heure", "l heure",
                    "قداش الساعة", "شنوة الساعة", "الساعة كم",
                ],
                "keywords": [
                    "heure", "temps",
                    "الوقت", "قداش",
                ],
                "patterns": [
                    r"quelle\s+heure\s+(?:est.il|il\s+est)",
                    r"il\s+est\s+quelle\s+heure",
                    r"(?:dis|donne|dites)[- ]?(?:moi)?\s+l.heure",
                    r"c.est\s+(?:quoi|quelle)\s+l.heure",
                    r"قداش\s+الساعة",
                    r"(?:شنوة|كم)\s+الساعة",
                    r"الساعة\s+(?:شنو|كم|قداش)",
                    r"(?:توا|الآن)\s+(?:الساعة|الوقت)",
                ],
                # Si le texte parle de médicaments, ne pas confondre "heure" avec get_time
                "blockers": [
                    "médicament", "medicament", "comprimé", "cachet", "pilule",
                    "doliprane", "paracétamol", "amlodipine", "metformine",
                    "دواء", "دوا", "حبة",
                ],
            },

            # ── 5. AJOUTER UN MÉDICAMENT ────────────────────────────
            "add_medication": {
                "strong_keywords": [
                    "médicament", "medicament", "comprimé", "cachet", "pilule",
                    "médicaments", "pharmaceutique",
                    "doliprane", "paracétamol", "paracetamol", "aspirine",
                    "amlodipine", "metformine", "oméprazole", "amoxicilline",
                    "دواء", "دوا", "كاشي", "حبة دواء",
                ],
                "keywords": [
                    "médoc", "sirop", "traitement", "prescription",
                    "prendre mon cachet", "prendre mon comprimé",
                    "حبة",
                ],
                "patterns": [
                    r"ajouter?\s+(?:le\s+|un\s+|mon\s+)?médicament",
                    r"(?:nouveau|nouvel)\s+médicament",
                    r"prendre?\s+(?:mon|le|un|ma)\s+(?:médicament|comprimé|cachet|pilule|médoc)",
                    r"(?:je\s+)?(?:dois|faut)\s+prendre",
                    r"(?:n)?ajoute[rz]?\s+(?:le\s+|un\s+)?médicament",
                    r"(?:je\s+)?(?:dois|faut|il\s+faut)\s+prendre\s+(?:mon|le|un|ma)",
                    r"(?:عندي|لازم|خاصني)\s+(?:ن)?(?:اخذ|ناخذ|ياخذ)\s+(?:ال)?(?:دواء|دوا|حبة)",
                    r"أضف\s+(?:دواء|دوا)",
                ],
                "blockers": [],
            },

            # ── 6. LIRE LES MESSAGES ────────────────────────────────
            "read_messages": {
                "strong_keywords": [
                    "messages", "message",
                    "رسائل", "رسالة", "مسج",
                ],
                "keywords": [
                    "lire", "lis", "courrier", "notification", "nouveau", "écrit",
                    "فما", "جداد", "جديد",
                ],
                "patterns": [
                    r"li[res]\s+(?:mes|les|mon)?\s*messages?",
                    r"(?:j.ai|y.a|il\s+y\s+a)\s+(?:des|un)?\s*messages?",
                    r"(?:mes|les|nouveaux)\s+messages?",
                    r"(?:est.ce\s+que\s+)?(?:j.ai|quelqu.un)\s+(?:m.a\s+)?(?:envoyé|écrit)",
                    r"(?:quelqu.un|qui)\s+(?:m.a\s+)?(?:envoyé|écrit)",
                    r"(?:فما|عندي)\s+رسائل?\s+(?:جداد|جديدة)?",
                    r"رسائل?\s+(?:جداد|جديدة)?",
                ],
                "blockers": [],
            },

            # ── 7. ENVOYER UN MESSAGE ───────────────────────────────
            "send_message": {
                "strong_keywords": [
                    "envoyer", "envoie", "envoyer un message",
                    "ابعث", "ارسل", "نبعث", "ارسل",
                ],
                "keywords": [
                    "écrire", "écris", "envoi",
                    "بعث", "رسالة لـ",
                ],
                "patterns": [
                    r"envoyer?\s+(?:un\s+)?message\s+(?:à|a)\s+",
                    r"écrire?\s+(?:un\s+)?message\s+(?:à|a)\s+",
                    r"(?:dis|dire)\s+(?:à|a)\s+\w+\s+que",
                    r"envoie[rz]?\s+(?:un\s+message\s+)?(?:à|a)\s+\w+",
                    r"ابعث\s+(?:مسج|رسالة)\s+(?:لـ?|ل)\s*\w+",
                    r"ارسل\s+(?:رسالة|مسج)\s+(?:لـ?|ل)\s*\w+",
                ],
                "blockers": [],
            },

            # ── 8. ALARME / RÉVEIL ──────────────────────────────────
            "set_alarm": {
                "strong_keywords": [
                    "alarme", "réveil", "réveille",
                    "صحيني", "منبه", "faya9ni", "fayaqni"
                ],
                "keywords": [
                    "sonner", "sonnerie", "timer", "minuteur",
                    "ريفاي",
                ],
                "patterns": [
                    r"mettre?\s+(?:une?\s+)?(?:alarme|réveil)",
                    r"réveille[rz]?\s*(?:moi)?",
                    r"(?:une?\s+)?alarme\s+(?:à|a|pour)",
                    r"sonne[rz]?\s+(?:à|a)",
                    r"صحيني\s+(?:على|على الساعة)?",
                    r"(?:اضبط|حط)\s+(?:المنبه|منبه)",
                    r"faya9ni|fayaqni"
                ],
                "blockers": [],
            },

            # ── 9. CONSULTER L'AGENDA ───────────────────────────────
            "check_agenda": {
                "strong_keywords": [
                    "agenda", "planning", "programme",
                    "emploi du temps", "rdv",
                    "برنامج", "موعد", "برنامجي",
                ],
                "keywords": [
                    "rendez-vous", "rendez vous", "prévu", "planifié",
                    "مواعيد",
                ],
                "patterns": [
                    r"(?:mon|le|l.)?\s*agenda",
                    r"(?:qu.est.ce\s+(?:qui\s+est|que\s+j.ai))\s+(?:de\s+)?(?:prévu|planifié)",
                    r"(?:mes|les)\s+rendez.?vous",
                    r"(?:le|mon|quel\s+est\s+(?:mon|le))\s+(?:programme|planning)",
                    r"c.est\s+quoi\s+le\s+programme",
                    r"(?:نبي|نحب|بغيت)\s+(?:نشوف|اشوف)\s+(?:البرنامج|برنامجي|مواعيدي)",
                ],
                "blockers": [],
            },

            # ── 10. URGENCE ─────────────────────────────────────────
            "emergency_alert": {
                "strong_keywords": [
                    "secours", "au secours", "urgence", "urgent", "sos",
                    "samu", "ambulance", "pompiers",
                    "نجدة", "عاوني", "خطر", "نجده",
                ],
                "keywords": [
                    "aide", "aidez", "malaise", "tombé", "danger", "help",
                    "mal", "douleur",
                    "حالة طوارئ",
                ],
                "patterns": [
                    r"au\s+secours",
                    r"(?:j.ai|je\s+me\s+sens)\s+(?:mal|pas\s+bien)",
                    r"j.ai\s+besoin\s+d.aide",
                    r"appeler?\s+(?:les?\s+)?(?:urgences?|samu|ambulance|pompiers)",
                    r"(?:je\s+suis|je\s+me\s+sens)\s+(?:mal|pas\s+bien)",
                    r"(?:c.est|situation)\s+(?:une?\s+)?urgence?",
                    r"(?:je\s+suis|j.ai)\s+tomb[eé]",
                    r"عاوني.*(?:نحس|ما\s+نا)",
                    r"نجدة",
                    r"خطر",
                ],
                "blockers": [],
            },
        }

        # Médicaments connus
        self.known_meds = [
            "doliprane", "paracétamol", "paracetamol", "aspirine",
            "ibuprofène", "ibuprofen", "amlodipine", "metformine",
            "oméprazole", "amoxicilline", "losartan", "atorvastatine",
            "levothyrox", "metoprolol", "ramipril", "furosémide",
        ]

        # Contacts connus (à adapter selon la base)
        self.known_contacts = [
            "mohamed", "fatma", "amina", "ali", "samu", "ben said",
            "محمد", "فاطمة", "فاطمه",
        ]

    # ──────────────────────────────────────────────────────────────────
    #  POINT D'ENTRÉE
    # ──────────────────────────────────────────────────────────────────
    def process(self, text: str) -> Dict:
        if not text or not text.strip():
            return {"intent": "unknown", "entities": {}, "confidence": 0.0, "raw_text": ""}

        text_clean = text.strip()
        text_lower = text_clean.lower()

        # Hackathon SeniorVoice : Nettoyage des mots d'hésitation fréquents chez les seniors
        hesitations = [r"\beuh\b", r"\bben\b", r"\bbah\b", r"\bbon\b\s+", r"\balors\b\s+", r"\bmmm+\b", r"\baaa+\b", r"\bيعني\b", r"\bااا\b", r"\bامم\b"]
        for hes in hesitations:
            text_lower = re.sub(hes, " ", text_lower)
        text_lower = re.sub(r"\s+", " ", text_lower).strip()

        intent, confidence = self._detect_intent(text_lower)
        entities = self._extract_entities(text_lower, intent)

        return {
            "intent": intent,
            "entities": entities,
            "confidence": confidence,
            "raw_text": text_clean,
        }

    # ──────────────────────────────────────────────────────────────────
    #  DÉTECTION D'INTENTION
    # ──────────────────────────────────────────────────────────────────
    def _detect_intent(self, text: str) -> Tuple[str, float]:
        scores: Dict[str, float] = {}

        for intent_name, data in self.intent_patterns.items():
            score = 0.0

            # Vérifier les blockers — si un blocker est présent, score = 0 pour cet intent
            if any(b in text for b in data.get("blockers", [])):
                continue

            # Mots-clés forts (score ×2)
            for kw in data.get("strong_keywords", []):
                if kw.lower() in text:
                    score += 2.0
                    if text.startswith(kw.lower()):
                        score += 0.5

            # Mots-clés normaux
            for kw in data.get("keywords", []):
                if kw.lower() in text:
                    score += 1.0

            # Patterns regex
            for pattern in data.get("patterns", []):
                try:
                    if re.search(pattern, text, re.IGNORECASE | re.UNICODE):
                        score += 1.5
                except re.error:
                    pass

            if score > 0:
                scores[intent_name] = score

        if not scores:
            return "unknown", 0.0

        # PRIORITÉ URGENCE — si détectée avec score > 0, elle prend la main
        if "emergency_alert" in scores and scores["emergency_alert"] >= 2.0:
            conf = min(1.0, scores["emergency_alert"] / 5.0)
            return "emergency_alert", round(max(conf, 0.85), 2)

        best_intent = max(scores, key=scores.get)
        max_score = scores[best_intent]
        confidence = min(1.0, max_score / 5.0)

        return best_intent, round(confidence, 2)

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION D'ENTITÉS
    # ──────────────────────────────────────────────────────────────────
    def _extract_entities(self, text: str, intent: str) -> Dict:
        entities = {}

        time_val = self._extract_time(text)
        if time_val:
            entities["time"] = time_val

        date_val = self._extract_date(text)
        if date_val:
            entities["date"] = date_val

        if intent in ("call_contact", "send_message"):
            contact = self._extract_contact_name(text)
            if contact:
                entities["contact"] = contact

        if intent == "send_message":
            msg = self._extract_message_content(text)
            if msg:
                entities["message_content"] = msg

        if intent == "add_medication":
            med = self._extract_medication(text)
            if med:
                entities["medication"] = med

        if intent == "create_reminder":
            title = self._extract_reminder_title(text)
            if title:
                entities["reminder_title"] = title

        return entities

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION : HEURE
    # ──────────────────────────────────────────────────────────────────
    def _extract_time(self, text: str) -> Optional[str]:
        # 8h, 8h30, 8:30, 08h00
        m = re.search(r"(\d{1,2})\s*[hH:]\s*(\d{0,2})", text)
        if m:
            h, mn = int(m.group(1)), int(m.group(2) or 0)
            if 0 <= h <= 23 and 0 <= mn <= 59:
                return f"{h:02d}:{mn:02d}"

        # "8 heures 30" / "8 heures"
        m = re.search(r"(\d{1,2})\s+heure[s]?(?:\s+(?:et\s+)?(\d{1,2}))?", text)
        if m:
            h, mn = int(m.group(1)), int(m.group(2) or 0)
            if 0 <= h <= 23 and 0 <= mn <= 59:
                return f"{h:02d}:{mn:02d}"

        # Arabe : "الساعة سبعة", "الساعة 7"
        arabic_nums = {
            "واحدة": 1, "اثنتين": 2, "اثنين": 2, "ثلاثة": 3, "أربعة": 4,
            "خمسة": 5, "ستة": 6, "سبعة": 7, "ثمانية": 8, "تسعة": 9,
            "عشرة": 10, "أحد عشر": 11, "اثني عشر": 12,
        }
        m = re.search(r"الساعة\s+(\d{1,2})", text)
        if m:
            h = int(m.group(1))
            if 0 <= h <= 23:
                return f"{h:02d}:00"

        for word, val in arabic_nums.items():
            if f"الساعة {word}" in text or f"على الساعة {word}" in text:
                return f"{val:02d}:00"

        return None

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION : DATE
    # ──────────────────────────────────────────────────────────────────
    def _extract_date(self, text: str) -> Optional[str]:
        if re.search(r"aujourd.hui|اليوم|توا", text):
            return "aujourd'hui"
        if re.search(r"demain|غدوة|الغد", text):
            return "demain"
        if re.search(r"après.demain|بعد\s+غد", text):
            return "après-demain"

        days = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]
        for day in days:
            if day in text:
                return day

        if "cette semaine" in text or "هذا الأسبوع" in text:
            return "cette semaine"
        if re.search(r"ce\s+matin|الصباح", text):
            return "ce matin"
        if re.search(r"ce\s+soir|الليلة|الليلا", text):
            return "ce soir"
        if re.search(r"après.midi|العصر|العصري", text):
            return "cet après-midi"

        return None

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION : NOM DE CONTACT
    # ──────────────────────────────────────────────────────────────────
    def _extract_contact_name(self, text: str) -> Optional[str]:
        # D'abord chercher dans les contacts connus
        for c in self.known_contacts:
            if c in text.lower():
                return c.capitalize()

        stop_words = {
            "le", "la", "les", "un", "une", "des", "mon", "ma", "mes",
            "ce", "cette", "que", "qui", "pour", "dans", "te", "me",
            "je", "veux", "voudrais", "appeler", "appelle", "envoyer",
            "message", "dire", "dis", "s'il", "docteur", "dr",
            "لي", "ل", "لـ", "مع",
        }

        patterns_fr = [
            r"appelle[rz]?\s+(?:le\s+|la\s+|l.)?([A-ZÀ-Ö\w][a-zà-ö\w]+)",
            r"(?:envoie[rz]?|écrire?)\s+(?:un\s+message\s+)?(?:à|a)\s+([A-ZÀ-Ö\w][a-zà-ö\w]+)",
            r"(?:dis|dire)\s+(?:à|a)\s+([A-ZÀ-Ö\w][a-zà-ö\w]+)",
            r"contacter?\s+([A-ZÀ-Ö\w][a-zà-ö\w]+)",
            r"joindre?\s+([A-ZÀ-Ö\w][a-zà-ö\w]+)",
            r"message\s+(?:à|a)\s+([A-ZÀ-Ö\w][a-zà-ö\w]+)",
        ]
        patterns_ar = [
            r"(?:عيط|عيطلي|اتصل)\s+(?:ل|لـ|ب|بـ)?\s*(\w+)",
            r"ابعث\s+(?:مسج|رسالة)\s+(?:ل|لـ)?\s*(\w+)",
            r"ارسل\s+(?:رسالة|مسج)\s+(?:ل|لـ)?\s*(\w+)",
            r"(?:نعيط|نكلم)\s+(?:ل|لـ)?\s*(\w+)",
        ]

        for pattern in patterns_fr + patterns_ar:
            try:
                m = re.search(pattern, text, re.IGNORECASE | re.UNICODE)
                if m:
                    name = m.group(1).strip()
                    if name.lower() not in stop_words and len(name) > 1:
                        return name.capitalize()
            except re.error:
                pass

        return None

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION : CONTENU DU MESSAGE
    # ──────────────────────────────────────────────────────────────────
    def _extract_message_content(self, text: str) -> Optional[str]:
        patterns = [
            r"(?:dis|dire)\s+(?:à|a)\s+\w+\s+(?:que\s+)?(.*)",
            r"envoie[rz]?\s+(?:un\s+)?message\s+(?:à|a)\s+\w+\s*[,:]\s*(.*)",
            r"(?:le\s+message|message)\s*[,:]\s*(.*)",
            r"(?:dit|dire)\s+(?:à|a)\s+\w+\s+(.*)",
            # Arabe
            r"(?:قولو|قولها|قوله)\s+(.*)",
        ]
        for p in patterns:
            try:
                m = re.search(p, text, re.IGNORECASE | re.UNICODE)
                if m:
                    content = m.group(1).strip()
                    if content and len(content) > 1:
                        return content
            except re.error:
                pass
        return None

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION : MÉDICAMENT
    # ──────────────────────────────────────────────────────────────────
    def _extract_medication(self, text: str) -> Optional[str]:
        text_lower = text.lower()

        # Médicaments connus
        for med in self.known_meds:
            if med in text_lower:
                return med.capitalize()

        # Pattern générique : "médicament <Nom>" ou "le <Nom>"
        for p in [
            r"médicament\s+([A-ZÀ-Öa-zà-ö]\w+)",
            r"(?:le|du|un)\s+([A-Z][a-zà-ö]\w+)",  # commence par majuscule
            r"(?:comprimé|cachet|pilule)\s+(?:de\s+|d.)?([A-ZÀ-Öa-zà-ö]\w+)",
        ]:
            try:
                m = re.search(p, text, re.IGNORECASE | re.UNICODE)
                if m:
                    candidate = m.group(1).strip()
                    not_med = {"matin", "soir", "jour", "fois", "heure", "mois", "semaine",
                               "moi", "mon", "ma", "me", "le", "la", "les"}
                    if candidate.lower() not in not_med and len(candidate) > 2:
                        return candidate.capitalize()
            except re.error:
                pass

        return None

    # ──────────────────────────────────────────────────────────────────
    #  EXTRACTION : TITRE DU RAPPEL
    # ──────────────────────────────────────────────────────────────────
    def _extract_reminder_title(self, text: str) -> Optional[str]:
        patterns = [
            # "rappelle-moi de prendre mon médicament à 8h"
            r"rappelle[- ]?moi\s+(?:de\s+|d.)?(.+?)(?:\s+(?:à|a)\s+\d|$)",
            # "n'oublie pas mon rendez-vous"
            r"(?:n.)?oublie\s+pas\s+(?:de\s+|d.)?(.+?)(?:\s+(?:à|a)\s+\d|$)",
            # "rappel pour acheter du pain"
            r"rappel\s+(?:pour\s+|de\s+)?(.+?)(?:\s+(?:à|a)\s+\d|$)",
            # "créer un rappel pour X"
            r"(?:cr[ée]+r?|ajouter?)\s+(?:un\s+)?rappel\s+(?:pour\s+|de\s+)?(.+?)(?:\s+(?:à|a)\s+\d|$)",
            # Arabe : "ذكرني نشري الدوا"
            r"ذكرني\s+(.*)",
            r"فكرني\s+(.*)",
        ]

        for p in patterns:
            try:
                m = re.search(p, text, re.IGNORECASE | re.UNICODE)
                if m:
                    title = m.group(1).strip().rstrip(".,!?")
                    if title and len(title) > 2:
                        return title[:120]
            except re.error:
                pass

        # Fallback : tout ce qui suit "rappelle-moi"
        m = re.search(r"rappelle[- ]?moi\s+(.*)", text, re.IGNORECASE | re.UNICODE)
        if m:
            return m.group(1).strip()[:120]

        return None