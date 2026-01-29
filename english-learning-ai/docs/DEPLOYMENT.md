# Guía de Deployment

## Google Cloud Run

### Backend

```bash
cd backend

# Build
gcloud builds submit --tag gcr.io/PROJECT_ID/english-learning-backend

# Deploy
gcloud run deploy english-learning-backend \
  --image gcr.io/PROJECT_ID/english-learning-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Frontend

```bash
cd frontend
npm run build

# Deploy a Firebase Hosting o Cloud Storage
firebase deploy --only hosting
```

## Variables de Entorno en Cloud Run

```bash
gcloud run services update english-learning-backend \
  --set-env-vars ANTHROPIC_API_KEY=your_key_here
```
