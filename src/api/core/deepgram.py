import os
import logging
from deepgram import Deepgram
from typing import Dict, Any

logger = logging.getLogger(__name__)

class DeepgramService:
    def __init__(self):
        api_key = os.getenv("DEEPGRAM_API_KEY")
        if not api_key:
            raise ValueError("DEEPGRAM_API_KEY environment variable is required")
            
        self.client = Deepgram(api_key)
        
    async def transcribe_audio(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe audio file using Deepgram."""
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