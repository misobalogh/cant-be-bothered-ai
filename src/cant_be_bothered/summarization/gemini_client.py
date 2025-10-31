import os
from datetime import datetime
from typing import Optional

from google import genai
from dotenv import load_dotenv

from cant_be_bothered.summarization.prompts import (
    MEETING_MINUTES_PROMPT,
    SIMPLE_SUMMARY_PROMPT,
    SYSTEM_PROMPT,
)

load_dotenv()


class GeminiClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key not found. Set GEMINI_API_KEY environment variable or pass it to constructor."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-2.0-flash-exp"

    def generate_meeting_minutes(
        self,
        transcript: str,
        date: Optional[str] = None,
    ) -> str:
        if date is None:
            date = datetime.now().strftime("%d. %B %Y")

        prompt = MEETING_MINUTES_PROMPT.format(
            transcript=transcript,
            date=date,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.3,
            },
        )
        return response.text

    def generate_simple_summary(self, transcript: str) -> str:
        prompt = SIMPLE_SUMMARY_PROMPT.format(transcript=transcript)

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.3,
            },
        )
        return response.text

    def generate_custom_summary(
        self,
        transcript: str,
        custom_instructions: str,
    ) -> str:
        prompt = f"{custom_instructions}\n\nPREPIS:\n{transcript}"

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config={
                "system_instruction": SYSTEM_PROMPT,
                "temperature": 0.3,
            },
        )
        return response.text

    def count_tokens(self, text: str) -> int:
        response = self.client.models.count_tokens(
            model=self.model_name,
            contents=text,
        )
        return response.total_tokens
