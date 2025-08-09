import os
import json
from typing import Dict
from logging import getLogger
import config

logger = getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None

class GPTResumeParser:
    """GPT-powered resume parser (used if OpenAI key is provided)."""

    def __init__(self, api_key: str = None, model: str = None):
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI package is not installed. Install it with: pip install openai")
        
        self.api_key = api_key or config.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required for GPT parsing.")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = model or config.GPT_MODEL

    def parse_resume(self, text: str) -> Dict:
        """
        Sends resume text to GPT to extract structured JSON data.
        """
        try:
            prompt = f"""
You are an expert resume parser.
Extract the following fields from the resume:
- contact (name, email, phone, linkedin, github, location)
- summary
- skills (list of skills)
- experience (list of jobs with company, title, dates, description)
- education (list of degrees with degree, field, school, year, GPA if available)
- certifications
- projects (list with name, description, technologies)
- accomplishments
- languages (list with language and proficiency if mentioned)

Return ONLY a valid JSON object with these keys.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a highly accurate resume parsing assistant. Always return valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": "Output the parsed resume as a valid JSON object with the specified fields. Resume text:\n" + text
                    }
                ],
                temperature=0,
                response_format={"type": "json_object"}  # Enforce JSON mode
            )

            # Parse JSON from response.content
            raw_content = response.choices[0].message.content
            parsed_data = json.loads(raw_content)
            return parsed_data

        except Exception as e:
            logger.error(f"Error in GPT parsing: {str(e)}")
            return {"error": str(e), "raw_text": text}
