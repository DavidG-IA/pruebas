from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from dotenv import load_dotenv

from services.claude_ai import ClaudeService
from services.google_tts import TTSService
from services.google_stt import STTService

load_dotenv()

app = FastAPI(title="English Learning AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

claude_service = ClaudeService(os.getenv("ANTHROPIC_API_KEY"))
tts_service = TTSService()
stt_service = STTService()


class GenerateExerciseRequest(BaseModel):
    level: str
    topic: str
    num_questions: int
    exercise_type: str


class EvaluateSpeakingRequest(BaseModel):
    audio_base64: str
    expected_text: str
    level: str


@app.get("/")
async def root():
    return {"message": "English Learning AI API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/exercises/generate")
async def generate_exercise(request: GenerateExerciseRequest):
    try:
        exercise_data = await claude_service.generate_exercise(
            level=request.level,
            topic=request.topic,
            num_questions=request.num_questions,
            exercise_type=request.exercise_type
        )

        if request.exercise_type == "listening":
            for question in exercise_data["questions"]:
                audio_url = await tts_service.generate_audio(
                    text=question["audio_text"],
                    language_code="en-US"
                )
                question["audio_url"] = audio_url

        return exercise_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/speaking/evaluate")
async def evaluate_speaking(request: EvaluateSpeakingRequest):
    try:
        transcription = await stt_service.transcribe_audio(request.audio_base64)

        evaluation = await claude_service.evaluate_speaking(
            transcription=transcription,
            expected_text=request.expected_text,
            level=request.level
        )

        return evaluation

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/tts/generate")
async def generate_audio(text: str, language: str = "en-US"):
    try:
        audio_url = await tts_service.generate_audio(text, language)
        return {"audio_url": audio_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
