from app.agents.common.azure_client import (
    AzureOpenAIClient
)

from app.agents.common.json_parser import (
    JsonParser
)

from app.core.config import settings


class AzureOpenAIRecommendationAgent:

    def recommend(
        self,
        investigation_case
    ):

        prompt = f"""
You are an enterprise operations advisor.

Case:

{investigation_case}

Return ONLY JSON.

{{
    "recommendation":"",
    "priority":"",
    "assigned_team":"",
    "estimated_resolution":"",
    "escalation_required":false
}}
"""

        response = AzureOpenAIClient.complete(
            prompt
        )

        return JsonParser.parse(
            response
        )