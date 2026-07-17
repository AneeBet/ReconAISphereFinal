from langfuse import get_client
from langfuse.openai import OpenAI

from app.core.config import settings


# Initialize Langfuse once
langfuse = get_client()


class AzureOpenAIClient:

    _client = None

    @classmethod
    def client(cls):

        if cls._client is None:

            cls._client = OpenAI(

                base_url=f"{settings.AZURE_OPENAI_ENDPOINT}/openai/v1",

                api_key=settings.AZURE_OPENAI_KEY,

                timeout=60,

                max_retries=2

            )

        return cls._client

    @classmethod
    def complete(
        cls,
        prompt: str,
        temperature: float = 0,
        **kwargs
    ):

        # We are intentionally ignoring metadata for now.
        # First verify that Langfuse captures traces.
        kwargs.pop("metadata", None)

        response = cls.client().responses.create(

            model=settings.AZURE_OPENAI_DEPLOYMENT,

            input=prompt

        )

        return response.output_text