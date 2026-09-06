from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.config import get_settings
from app.llm.service import LLMService


class GeminiProvider(LLMService):

    def __init__(self):
        settings = get_settings()

        self.llm = ChatGoogleGenerativeAI(
            model=settings.gemini_model,
            google_api_key=settings.gemini_api_key,
            temperature=0,
        )

    def generate(self, prompt: str) -> str:
        response = self.llm.invoke(prompt)

        return response.content