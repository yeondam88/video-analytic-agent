import os
import logging
from openai import AsyncOpenAI
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
            
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def create_embeddings(self, transcript: Dict[str, Any]) -> List[float]:
        """Create embeddings for the transcript text."""
        try:
            response = await self.client.embeddings.create(
                model="text-embedding-3-small",
                input=transcript['text'],
                dimensions=1536
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"OpenAI embeddings error: {str(e)}")
            raise Exception(f"Failed to create embeddings: {str(e)}")
            
    async def generate_summary(self, transcript: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the transcript."""
        try:
            prompt = f"""
            Please analyze this transcript and provide a structured summary with the following:
            1. A concise title (max 10 words)
            2. A brief summary (2-3 sentences)
            3. Key points (3-5 bullet points)
            4. Action items (if any)
            
            Transcript:
            {transcript['text']}
            
            Format the response as JSON with these keys: title, summary, key_points, action_items
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that creates concise and structured summaries of video transcripts."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI summary error: {str(e)}")
            raise Exception(f"Failed to generate summary: {str(e)}") 