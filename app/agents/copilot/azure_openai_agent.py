import json
from datetime import datetime
from datetime import timezone

from langfuse import observe

from app.agents.common.azure_client import (
    AzureOpenAIClient
)


USECASE_ID = "ecb6bd82-1937-4530-a528-0476d41f5654"

AGENT_ID = 175

AGENT_NAME = "ReconAI Copilot"

ENVIRONMENT = "production"

LLM_PROVIDER = "Azure OpenAI"


def get_utc_now() -> str:

    return (
        datetime.now(timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        + "+00"
    )


class AzureOpenAICopilotAgent:

    @observe()
    def chat(
        self,
        question,
        context
    ):

        prompt = f"""
You are ReconSphere AI Copilot.

You are an Enterprise Operations Copilot for a cross-border payment reconciliation platform.

You are NOT a generic chatbot.

Your job is to assist Operations, Compliance, Investigations, and Reconciliation teams using ONLY the information available in the platform context.

--------------------------------------------------
PLATFORM CONTEXT
--------------------------------------------------

{json.dumps(context, indent=2, default=str)}

--------------------------------------------------
USER QUESTION
--------------------------------------------------

{question}

--------------------------------------------------
YOUR RESPONSIBILITIES
--------------------------------------------------

Answer questions about:

• Dashboard statistics
• Reconciliation runs
• Open investigation cases
• Exceptions
• Transactions
• Payment status
• Operational risks
• Business impact
• Investigation priorities
• Workload summaries

If the user asks:

"Summarize today's reconciliation"

→ summarize the latest reconciliation run.

If the user asks:

"Open exceptions"

→ summarize open exceptions.

If the user asks:

"What should Operations do today?"

→ prioritize the highest severity exceptions and open investigation cases.

If the user asks:

"Which transaction needs attention?"

→ identify transactions involved in open exceptions or investigation cases.

If the user asks something unrelated to the supplied context:

• Answer using general banking knowledge.
• Clearly mention that the requested information is not available in the current platform data.
• Never invent platform data.

--------------------------------------------------
RESPONSE STYLE
--------------------------------------------------

Always:

• Professional
• Enterprise focused
• Banking terminology
• Short paragraphs
• Bullet lists where useful

When platform data exists:

1. Start with a short summary.
2. Mention important numbers.
3. Highlight risks.
4. Recommend next operational actions.

Never fabricate transactions, cases, exceptions, or statistics.
"""

        completion_start_time = get_utc_now()

        return AzureOpenAIClient.complete(

            prompt,

            metadata={

                "agent_id": AGENT_ID,

                "agent_name": AGENT_NAME,

                "usecase_id": USECASE_ID,

                "environment": ENVIRONMENT,

                "llm_provider": LLM_PROVIDER,

                "node": "reconai_copilot",

                "completion_start_time": completion_start_time,

            }

        )