# Import standard library modules
import io

# Import third-party library modules
import azure.cognitiveservices.speech as speechsdk

# Import local modules
from src.components.coach_ai.settings import AZURE_SPEECH_SERVICE_KEY, AZURE_SPEECH_SERVICE_REGION


def azure_text_to_speech(text: str):
    speech_config = speechsdk.SpeechConfig(
        subscription=AZURE_SPEECH_SERVICE_KEY, region=AZURE_SPEECH_SERVICE_REGION
    )
    # Set the speech synthesis voice and style
    speech_synthesis_voice_name = "en-US-JennyNeural"
    speech_synthesis_style = "customerservice"

    # Create a synthesizer
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

    # Define the SSML to be synthesized
    ssml = f"""
    <speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis' xml:lang='en-US'>
        <voice name='{speech_synthesis_voice_name}' style='{speech_synthesis_style}'>
            {text}
        </voice>
    </speak>
    """

    # Synthesize the speech
    result = synthesizer.speak_ssml_async(ssml).get()

    # Handle the result
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return io.BytesIO(result.audio_data)
    else:
        error = (
            "Speech synthesis failed"
            if result.cancellation_details is None
            else result.cancellation_details.reason
        )
        raise Exception(error)
