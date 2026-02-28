import sys
import os

# Ensure the app module can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.nlp_processor import NLPProcessor

def test_hesitations():
    nlp = NLPProcessor()
    
    test_phrases = [
        "euh... quelle heure euh... est-il ?",
        "aman... faya9ni euh... à 8 heures.",
        "bah... euh... lis-moi le dernier message.",
        "euh... je dois prendre mon euh... doliprane à 14h.",
        "Euh... au secours... aaaaa...",
        "ben rappelle moi de manger a midi mmm"
    ]
    
    print("🚀 Test du filtre anti-bafouillage (Hackathon SeniorVoice)")
    print("-" * 50)
    
    for phrase in test_phrases:
        result = nlp.process(phrase)
        print(f"Phrase brute : {phrase}")
        print(f"Intention détectée : {result['intent']} (Confiance: {result['confidence']})")
        print(f"Entités extraites : {result['entities']}")
        print("-" * 50)

if __name__ == "__main__":
    test_hesitations()
