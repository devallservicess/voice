"""
Test NLP avec le dialecte tunisien (الدارجة التونسية)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from app.services.nlp_processor import NLPProcessor

nlp = NLPProcessor()

tunisian_tests = [
    # (phrase, intent attendu)
    ("نحب نعيط لمحمد", "call_contact", "Appeler Mohamed"),
    ("عيطلي لفاطمة", "call_contact", "Appeler Fatma"),
    ("شنوة الطقس اليوم", "get_weather", "Météo aujourd'hui"),
    ("قداش الساعة", "get_time", "Quelle heure"),
    ("ذكرني نشري الدوا", "create_reminder", "Rappel acheter médicament"),
    ("عاوني نحس بروحي ماني لاباس", "emergency_alert", "Urgence - pas bien"),
    ("ابعث مسج لمحمد", "send_message", "Envoyer message à Mohamed"),
    ("صحيني على الساعة سبعة", "set_alarm", "Réveil à 7h"),
    ("شنوة الساعة توا", "get_time", "Quelle heure maintenant"),
    ("نحب نشوف البرنامج متاعي", "check_agenda", "Voir mon programme"),
    ("عندي حبة دوا لازم ناخذها", "add_medication", "Prendre médicament"),
    ("نجدة نجدة", "emergency_alert", "Au secours"),
    ("فما رسائل جداد", "read_messages", "Nouveaux messages"),
    ("حالة الجو اليوم", "get_weather", "Météo du jour"),
    ("خطر عاوني", "emergency_alert", "Danger aide-moi"),
]

print("=" * 60)
print("🧪 Test NLP – Dialecte Tunisien (الدارجة التونسية)")
print("=" * 60)

passed = 0
for phrase, expected, desc in tunisian_tests:
    result = nlp.process(phrase)
    ok = result["intent"] == expected
    passed += ok
    icon = "✅" if ok else "❌"
    got = result["intent"]
    conf = result["confidence"]
    entities = result["entities"]
    ent_str = f" → {entities}" if entities else ""
    print(f"  {icon} [{desc}]")
    print(f"     \"{phrase}\"")
    if ok:
        print(f"     → {got} (conf: {conf:.2f}){ent_str}")
    else:
        print(f"     → got '{got}' expected '{expected}' (conf: {conf:.2f})")
    print()

print("=" * 60)
total = len(tunisian_tests)
print(f"📊 Résultats: {passed}/{total} ({100*passed//total}%)")
if passed == total:
    print("🎉 Tous les tests dialecte tunisien passent !")
else:
    print(f"⚠️  {total - passed} tests échoués")
print("=" * 60)
