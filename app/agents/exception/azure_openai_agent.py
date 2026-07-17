import json
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

AGENT_ID = 173

AGENT_NAME = "Exception Analysis"

ENVIRONMENT = "production"

LLM_PROVIDER = "Azure OpenAI"


def get_utc_now() -> str:

    return (
        datetime.now(timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        + "+00"
    )


class AzureOpenAIExceptionAgent:

    @observe()
    def analyze(
        self,
        context: dict
    ):

        schema = {
            "summary": "",
            "root_cause": "",
            "confidence": 0,
            "business_explanation": "",
            "operational_domain": "",
            "business_impact": "",
            "evidence": [
                {
                    "field": "",
                    "payment": "",
                    "bank": "",
                    "result": ""
                }
            ],
            "recommended_actions": [
                ""
            ]
        }

        prompt = f"""
You are a Senior Cross-Border Payments Operations Analyst working for a Tier-1 Global Bank.

You are investigating a payment reconciliation exception.

Below is the complete investigation context.

<context>

{json.dumps(context, indent=2, default=str)}

</context>

Your responsibilities:

1. Explain exactly what happened.
2. Identify the most probable root cause.
3. Explain why reconciliation failed.
4. Identify the operational domain responsible.
5. Describe the customer/business impact.
6. Recommend concrete operational actions.
7. Mention any operational risks.
8. Mention any missing information if confidence is reduced.
9. Produce a confidence score between 0 and 100.

Reason using banking knowledge.

Examples:

• Amount differs
→ Amount mismatch.

• Currency differs
→ FX exception.

• Bank transaction missing
→ Missing bank confirmation or settlement issue.

• Settlement delayed
→ Settlement timing issue.

• AML failed
→ Compliance hold.

• Correspondent failed
→ Correspondent banking routing issue.

Rules:

- Base your answer ONLY on the supplied investigation context.
- Do not invent data.
- If data is missing, explicitly mention it.
- Return ONLY valid JSON.
- Keep the summary concise (3–5 sentences).
- Root cause should be a single paragraph.
- Business impact should be business-focused.
- Operational domain should be one team only.
- Confidence must be between 0 and 100.

The "evidence" array must contain one object for every important reconciliation field.

Possible fields include:

- Transaction Reference
- End-to-End ID
- Amount
- Currency
- Payment Status
- Settlement Date
- FX Rate

For every field return:

- field
- payment
- bank
- result (MATCH / MISMATCH / MISSING)

JSON Schema:

{json.dumps(schema, indent=2)}
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

                "node": "exception_analysis_1",

                "completion_start_time": completion_start_time,

            }

        )

        return JsonParser.parse(output)