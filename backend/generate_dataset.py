import json
import os
import random

# Définition des 10 Intentions du Hackathon
INTENTS = [
    "create_reminder", "call_contact", "get_weather", "get_time", 
    "add_medication", "read_messages", "send_message", "set_alarm", 
    "check_agenda", "emergency_alert"
]

# Modèles avec hésitations et franglais tunisien (Darija + Français)
TEMPLATES = {
    "create_reminder": [
        "Euh... rappelle-moi de {action}... ben {time}.",
        "Ah oui... fakkarni bech {action} euh... {time}.",
        "Ntiya... euh... n'oublie pas de {action} {time}.",
        "Aman... ذكرني باش {action} euh... {time}.",
        "Euuuh rappelles-moi {action} mmmm {time}."
    ],
    "call_contact": [
        "Euh... appelle euh... {contact}.",
        "Nحب نكلم euh... {contact}... s'il te plaît.",
        "Aman... appelili {contact} euh... tawa.",
        "Euh... 3ayet l {contact}... bah... wa9teli najam.",
        "S'il te plaît... euh... contacte {contact}."
    ],
    "get_weather": [
        "Euh... quel temps euh... il fait aujourd'hui ?",
        "Chnowa el ta9s euh... lyoum ?",
        "Bah... est-ce qu'il pleut euh... tawa ?",
        "Za3ma... euh... la météo euh... demain ?",
        "Mmmm... il fait chaud... euh... dehors ?"
    ],
    "get_time": [
        "Euh... quelle heure euh... est-il ?",
        "Aman... 9adech lwa9t euh... tawa ?",
        "Euh... saa9a... euh... 9adech ?",
        "Il est quelle heure euh... s'il te plaît ?",
        "Mmmm... c'est quoi... euh... l'heure ?"
    ],
    "add_medication": [
        "Euh... je dois prendre mon euh... {medication} à {time}.",
        "Aman... n9ayed l dwe mte3i... euh... {medication} {time}.",
        "N'oublie pas euh... mon cachet de {medication}... à {time}.",
        "Euh... ajouter le médicament... euh... {medication}.",
        "Ah... la pilule de {medication}... euh... à prendre {time}."
    ],
    "read_messages": [
        "Euh... lis mes messages euh...",
        "Aman... a9rali l messages mte3i euh...",
        "Est-ce que... euh... j'ai des nouveaux messages ?",
        "Euh... choufli chkoun b3athli msg...",
        "Bah... euh... lis-moi le dernier message."
    ],
    "send_message": [
        "Euh... envoie un message euh... à {contact}.",
        "Aman... ab3ath msg l {contact} euh... tawa.",
        "Euh... dis à {contact}... euh... que je l'attends.",
        "Ah... écrire à {contact}... euh... s'il te plaît.",
        "Euh... ابعث مساج ل {contact}..."
    ],
    "set_alarm": [
        "Euh... mets une alarme euh... à {time}.",
        "Aman... faya9ni euh... {time}.",
        "Mets le réveil euh... s'il te plaît... à {time}.",
        "Euh... réveille-moi à... euh... {time}.",
        "Ah... منبه على الساعة euh... {time}."
    ],
    "check_agenda": [
        "Euh... qu'est-ce que j'ai prévu euh... aujourd'hui ?",
        "Aman... chnowa el programme euh... lyoum ?",
        "Euh... mon agenda... euh... s'il te plaît.",
        "Quels sont mes rendez-vous... euh... demain ?",
        "Euh... عندي مواعيد اليوم ?"
    ],
    "emergency_alert": [
        "Euh... au secours... ehm...",
        "Aman... 3awni... euh... je me sens pas bien.",
        "J'ai besoin d'aide... euh... urgence !",
        "Euh... appel le samu... vite...",
        "Ah... je suis tombée... euh... à l'aide..."
    ]
}

# Variables de remplissage
VARS = {
    "{action}": ["prendre mes pilules", "aller chez le médecin", "appeler mon fils", "acheter du pain", "يما"],
    "{time}": ["à 8 heures", "demain matin", "tout de suite", "el 3chiya", "à midi"],
    "{contact}": ["Mohamed", "Fatma", "mon fils", "le docteur", "ma fille"],
    "{medication}": ["Doliprane", "Paracétamol", "Aspirine", "mon sirop", "le traitement"]
}

def fill_template(template):
    result = template
    for key, values in VARS.items():
        if key in result:
            result = result.replace(key, random.choice(values))
    return result

def main():
    dataset_dir = os.path.join(os.path.dirname(__file__), "dataset")
    os.makedirs(dataset_dir, exist_ok=True)
    json_path = os.path.join(dataset_dir, "seniorvoice_dataset.json")

    print(f"🚀 Génération du dataset dans {json_path}...")

    annotations = []
    
    # Générer 50 exemples (5 par intention)
    for intent in INTENTS:
        templates = TEMPLATES.get(intent, [])
        for i in range(5):
            # Choisir un template au hasard ou tourner en boucle
            tmpl = templates[i % len(templates)]
            transcript = fill_template(tmpl)
            
            entry = {
                "id": f"senior_audio_{intent}_{i}",
                "transcription_attendue": transcript,
                "intention_cible": intent,
                "notes": "Voix chevrotante (euh), mélange de dialecte tunisien et de français."
            }
            annotations.append(entry)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(annotations, f, ensure_ascii=False, indent=4)

    print(f"✅ Génération terminée ! {len(annotations)} exemples annotés créés.")
    print("💡 Pour le hackathon, vous pouvez demander à des seniors de lire ces 50 phrases pour les enregistrer en vrai.")

if __name__ == "__main__":
    main()
