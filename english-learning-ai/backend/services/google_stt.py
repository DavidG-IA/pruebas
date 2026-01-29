from google.cloud import speech
import base64


class STTService:
    def __init__(self):
        self.client = speech.SpeechClient()

    async def transcribe_audio(self, audio_base64: str) -> str:

        audio_bytes = base64.b64decode(audio_base64)

        audio = speech.RecognitionAudio(content=audio_bytes)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
            sample_rate_hertz=48000,
            language_code="en-US",
            enable_automatic_punctuation=True,
        )

        response = self.client.recognize(config=config, audio=audio)

        if response.results:
            return response.results[0].alternatives[0].transcript

        return ""
