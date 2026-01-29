from google.cloud import texttospeech
import base64


class TTSService:
    def __init__(self):
        self.client = texttospeech.TextToSpeechClient()

    async def generate_audio(self, text: str, language_code: str = "en-US") -> str:

        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            name=f"{language_code}-Neural2-C",
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=0.9
        )

        response = self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')

        return f"data:audio/mp3;base64,{audio_base64}"
