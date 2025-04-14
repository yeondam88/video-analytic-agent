import os
import logging
from deepgram import Deepgram
from typing import Dict, Any
from src.config import settings

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self):
        """Initialize the Deepgram service.
        If no API key is available, the service will be in a disabled state.
        """
        self.api_key = settings.services.DEEPGRAM_API_KEY
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Deepgram service is disabled: DEEPGRAM_API_KEY environment variable is not set")
        else:
            self.client = Deepgram(self.api_key)
        
    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file using Deepgram."""
        if not self.enabled:
            logger.warning("Deepgram transcription skipped: Service is disabled")
            return {
                "text": "Transcription unavailable - Deepgram API key not configured",
                "words": [],
                "speakers": [],
                "confidence": 0.0
            }
            
        try:
            with open(audio_path, 'rb') as audio:
                source = {'buffer': audio, 'mimetype': 'audio/wav'}
                response = await self.client.transcription.prerecorded(
                    source,
                    {
                        'smart_format': True,
                        'model': 'nova-2',
                        'language': 'en',
                        'diarize': True,
                        'punctuate': True,
                        'utterances': True
                    }
                )
                
                return {
                    'text': response['results']['channels'][0]['alternatives'][0]['transcript'],
                    'words': response['results']['channels'][0]['alternatives'][0]['words'],
                    'speakers': response['results']['channels'][0]['alternatives'][0].get('speaker_labels', []),
                    'confidence': response['results']['channels'][0]['alternatives'][0]['confidence']
                }
                
        except Exception as e:
            logger.error(f"Deepgram transcription error: {str(e)}")
            raise Exception(f"Failed to transcribe audio: {str(e)}") 