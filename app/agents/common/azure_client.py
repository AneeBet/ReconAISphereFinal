from openai import OpenAI

from app.core.config import settings


class AzureOpenAIClient:

    _client = None

    @classmethod
    def client(cls):

        if cls._client is None:

            cls._client = OpenAI(

                base_url=settings.AZURE_OPENAI_ENDPOINT,

                api_key=settings.AZURE_OPENAI_KEY,

                timeout=60,

                max_retries=2

            )

        return cls._client

    @classmethod
    def complete(cls, prompt, temperature=0):
        """Single entry point for all agents. Deterministic, resilient."""

        response = cls.client().responses.create(

            model=settings.AZURE_OPENAI_DEPLOYMENT,

            input=prompt,

            temperature=temperature

        )

        return response.output_text