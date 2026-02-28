import requests
import sys

def test_gemini_audio(audio_path):
    url = "http://localhost:8000/api/process-voice"
    try:
        with open(audio_path, 'rb') as f:
            # Adjust MIME type depending on file, binary is safe
            files = {'file': (audio_path, f, 'audio/wav')}
            print(f"Envoi du fichier {audio_path} à l'API...")
            response = requests.post(url, files=files)
            
            print("\n" + "="*50)
            print(f"Status Code: {response.status_code}")
            print(f"Réponse JSON: {response.json()}")
            print("="*50 + "\n")
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_audio.py <chemin_vers_audio.wav/webm>")
    else:
        test_gemini_audio(sys.argv[1])
