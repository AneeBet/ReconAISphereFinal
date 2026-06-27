from openai import OpenAI

from app.core.config import settings


class AzureOpenAIClient:

    _client = None

    @classmethod
    def client(cls):

        if cls._client is None:

            cls._client = OpenAI(

                base_url=settings.AZURE_OPENAI_ENDPOINT,

                api_key=settings.AZURE_OPENAI_KEY

            )

        return cls._client