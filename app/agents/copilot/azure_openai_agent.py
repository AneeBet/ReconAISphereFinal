from app.agents.common.azure_client import (
    AzureOpenAIClient
)

from app.core.config import settings


class AzureOpenAICopilotAgent:

    def chat(
        self,
        question,
        context
    ):

        client = AzureOpenAIClient.client()

        prompt = f"""
You are ReconAI Copilot.

Context:

{context}

Question:

{question}

Provide a concise enterprise response.
"""

        response = client.responses.create(

            model=settings.AZURE_OPENAI_DEPLOYMENT,

            input=prompt

        )

        return response.output_text
