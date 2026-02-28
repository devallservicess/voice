import os
from dotenv import load_dotenv

# ⚠️ Must be called BEFORE any app imports so that os.getenv() works everywhere
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, HTMLResponse
from contextlib import asynccontextmanager

from app.database import init_db, seed_db
from app.routers import voice


# Gestionnaire de cycle de vie
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Démarrage de SeniorVoice API...")
    init_db()
    print("✅ Base de données initialisée")
    seed_db()
    print("✅ Données d'exemple chargées")
    print("✅ Tous les services sont prêts")
    print("=" * 50)
    print("🧓 SeniorVoice est opérationnel!")
    print("🌐 Interface: http://localhost:8000")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    yield
    # Shutdown
    print("👋 Arrêt de SeniorVoice...")


# Créer l'application FastAPI
app = FastAPI(
    title="SeniorVoice API",
    description="Assistant vocal IA pour seniors tunisiens – Whisper + NLP + Actions",
    version="1.0.0",
    lifespan=lifespan
)

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure les routes API
app.include_router(voice.router)

# Chemins vers les fichiers frontend
BACKEND_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(os.path.dirname(BACKEND_DIR), "frontend")

print(f"📁 Dossier frontend: {FRONTEND_DIR}")


# ==================== Routes Frontend ====================

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Servir la page d'accueil SeniorVoice"""
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    else:
        return HTMLResponse(
            content="<html><body><h1>⚠️ Frontend non trouvé</h1></body></html>",
            status_code=404
        )

@app.get("/style.css")
async def serve_css():
    css_path = os.path.join(FRONTEND_DIR, "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="text/css",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return Response(content="/* CSS not found */", media_type="text/css", status_code=404)

@app.get("/app.js")
async def serve_js():
    js_path = os.path.join(FRONTEND_DIR, "app.js")
    if os.path.exists(js_path):
        with open(js_path, "r", encoding="utf-8") as f:
            content = f.read()
        return Response(
            content=content,
            media_type="application/javascript",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    return Response(content="// JS not found", media_type="application/javascript", status_code=404)

@app.get("/api")
async def root():
    return {
        "message": "Bienvenue sur SeniorVoice API",
        "version": "1.0.0",
        "endpoints": {
            "process_voice": "/api/process-voice",
            "contacts": "/api/contacts",
            "reminders": "/api/reminders",
            "medications": "/api/medications",
            "messages": "/api/messages",
            "agenda": "/api/agenda",
            "history": "/api/history",
            "health": "/api/health",
            "docs": "/docs"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )