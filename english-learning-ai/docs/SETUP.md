# Guía de Instalación

## Pre-requisitos

1. Python 3.11+
2. Node.js 18+
3. Anthropic API Key
4. Google Cloud Project con TTS/STT habilitado
5. PostgreSQL (opcional para desarrollo)

## Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configura .env
cp .env.example .env
# Edita .env con tus credenciales

# Inicia el servidor
uvicorn main:app --reload
```

Backend corriendo en: http://localhost:8000

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend corriendo en: http://localhost:5173

## Google Cloud Setup

1. Crea un proyecto en Google Cloud Console
2. Habilita las APIs:
   - Cloud Text-to-Speech API
   - Cloud Speech-to-Text API
3. Crea un Service Account
4. Descarga el JSON de credenciales
5. Configura la variable de entorno:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

## Testing

Backend:

```bash
curl http://localhost:8000/health
```

Debería retornar: `{"status": "healthy"}`
