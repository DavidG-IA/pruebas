import google.generativeai as genai
import json
from typing import Dict, Any
import os


class ClaudeService:  # Mantenemos el nombre para no cambiar otros archivos
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_exercise(
        self,
        level: str,
        topic: str,
        num_questions: int,
        exercise_type: str
    ) -> Dict[str, Any]:

        prompts = {
            "listening": self._get_listening_prompt(level, topic, num_questions),
            "speaking": self._get_speaking_prompt(level, topic, num_questions),
            "reading": self._get_reading_prompt(level, topic, num_questions),
            "grammar": self._get_grammar_prompt(level, topic, num_questions)
        }

        prompt = prompts.get(exercise_type)

        response = self.model.generate_content(prompt)
        content = response.text

        # Limpia el JSON
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    def _get_listening_prompt(self, level: str, topic: str, num_questions: int) -> str:
        return f"""Genera {num_questions} preguntas de listening en inglés nivel {level} sobre el tema: {topic}.

Para cada pregunta necesito:
1. Una frase corta en inglés para el audio (máximo 2-3 oraciones, apropiadas para {level})
2. Una pregunta de comprensión en español
3. 3 opciones de respuesta en español (solo una correcta)
4. La respuesta correcta (a, b, o c)

IMPORTANTE: Responde ÚNICAMENTE en formato JSON válido:

{{
  "questions": [
    {{
      "audio_text": "texto en inglés para el audio",
      "question": "pregunta en español",
      "options": ["opción a", "opción b", "opción c"],
      "correct": "a"
    }}
  ]
}}"""

    def _get_speaking_prompt(self, level: str, topic: str, num_questions: int) -> str:
        return f"""Genera {num_questions} ejercicios de speaking en inglés nivel {level} sobre: {topic}.

Cada ejercicio debe tener:
1. Una situación o contexto en español
2. Una frase modelo en inglés que el usuario debe decir
3. Palabras clave para evaluar

Formato JSON:
{{
  "exercises": [
    {{
      "context": "contexto en español",
      "target_phrase": "frase en inglés",
      "keywords": ["palabra1", "palabra2"]
    }}
  ]
}}"""

    def _get_reading_prompt(self, level: str, topic: str, num_questions: int) -> str:
        return f"""Genera un texto en inglés nivel {level} sobre: {topic}, seguido de {num_questions} preguntas de comprensión.

Formato JSON:
{{
  "text": "texto en inglés",
  "questions": [
    {{
      "question": "pregunta en español",
      "options": ["a", "b", "c"],
      "correct": "a"
    }}
  ]
}}"""

    def _get_grammar_prompt(self, level: str, topic: str, num_questions: int) -> str:
        return f"""Genera {num_questions} ejercicios de gramática en inglés nivel {level} sobre: {topic}.

Cada ejercicio:
1. Una oración con un espacio en blanco
2. 3 opciones para completar
3. Una explicación breve

Formato JSON:
{{
  "exercises": [
    {{
      "sentence": "I ___ to school every day",
      "options": ["go", "goes", "going"],
      "correct": "a",
      "explanation": "Se usa 'go' con 'I'"
    }}
  ]
}}"""

    async def evaluate_speaking(
        self,
        transcription: str,
        expected_text: str,
        level: str
    ) -> Dict[str, Any]:

        prompt = f"""Evalúa este speaking en inglés nivel {level}:

Transcripción del usuario: "{transcription}"
Texto esperado: "{expected_text}"

Dame un análisis en JSON:
{{
  "score": 0-100,
  "pronunciation_score": 0-100,
  "fluency_score": 0-100,
  "accuracy_score": 0-100,
  "feedback": "feedback en español",
  "mistakes": ["error1", "error2"],
  "suggestions": ["sugerencia1", "sugerencia2"]
}}"""

        response = self.model.generate_content(prompt)
        content = response.text
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)
