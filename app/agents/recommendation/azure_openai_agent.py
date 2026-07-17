from datetime import datetime
from datetime import timezone

from langfuse import observe

from app.agents.common.azure_client import (
    AzureOpenAIClient,
)

from app.agents.common.json_parser import (
    JsonParser,
)


USECASE_ID = "ecb6bd82-1937-4530-a528-0476d41f5654"

AGENT_ID = 174

AGENT_NAME = "Recommendation"

ENVIRONMENT = "production"

LLM_PROVIDER = "Azure OpenAI"


def get_utc_now() -> str:

    return (
        datetime.now(timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        + "+00"
    )


class AzureOpenAIRecommendationAgent:

    @observe()
    def recommend(
        self,
        investigation_case
    ):

        prompt = f"""
You are an enterprise operations advisor.

Review the investigation case and recommend the most appropriate operational next steps.

Case:

{investigation_case}

Return ONLY valid JSON.

{{
    "recommendation": "",
    "priority": "",
    "assigned_team": "",
    "estimated_resolution": "",
    "escalation_required": false
}}
"""

        completion_start_time = get_utc_now()

        output = AzureOpenAIClient.complete(

            prompt,

            metadata={

                "agent_id": AGENT_ID,

                "agent_name": AGENT_NAME,

                "usecase_id": USECASE_ID,

                "environment": ENVIRONMENT,

                "llm_provider": LLM_PROVIDER,

                "node": "recommendation",

                "completion_start_time": completion_start_time,

            }

        )

        return JsonParser.parse(output)