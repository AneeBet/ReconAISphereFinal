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

AGENT_ID = 172

AGENT_NAME = "Intelligent Matching"

ENVIRONMENT = "production"

LLM_PROVIDER = "Azure OpenAI"


def get_utc_now() -> str:

    return (
        datetime.now(timezone.utc)
        .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        + "+00"
    )


class AzureOpenAIMatchingAgent:

    @observe()
    def validate(

        self,

        payment,

        bank,

        score,

    ):

        prompt = f"""
You are ReconAI's Enterprise Matching Agent.

You are NOT the reconciliation engine.

The Rule Engine has already evaluated the transaction.

Only review BORDERLINE matches and determine whether the transaction should be accepted or rejected.

----------------------------------------
RULE ENGINE SCORE
----------------------------------------

{score}

----------------------------------------
PAYMENT TRANSACTION
----------------------------------------

Transaction Reference:
{payment.transaction_reference}

End To End ID:
{payment.end_to_end_id}

Amount:
{payment.amount}

Currency:
{payment.currency}

Payment Date:
{payment.payment_date}

Sender:
{payment.sender_name}

Receiver:
{payment.receiver_name}

----------------------------------------
BANK TRANSACTION
----------------------------------------

Transaction Reference:
{bank.transaction_reference if bank else "N/A"}

End To End ID:
{bank.end_to_end_id if bank else "N/A"}

Amount:
{bank.amount if bank else "N/A"}

Currency:
{bank.currency if bank else "N/A"}

Payment Date:
{bank.payment_date if bank else "N/A"}

----------------------------------------

Return ONLY valid JSON.

{{
    "decision":"MATCH or EXCEPTION",
    "confidence":95,
    "reason":"Business explanation.",
    "matched_fields":[
        "Transaction Reference",
        "Amount"
    ],
    "mismatched_fields":[
        "End To End ID"
    ],
    "risk":"LOW"
}}

Do not return markdown.
Do not explain outside JSON.
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

                "node": "intelligent_matching",

                "completion_start_time": completion_start_time,

            }

        )

        result = JsonParser.parse(output)

        return {

            "decision": result.get(
                "decision",
                "REVIEW"
            ),

            "confidence": result.get(
                "confidence",
                score
            ),

            "reason": result.get(
                "reason",
                "AI review unavailable; defaulted to rule engine score."
            ),

            "matched_fields": result.get(
                "matched_fields",
                []
            ),

            "mismatched_fields": result.get(
                "mismatched_fields",
                []
            ),

            "risk": result.get(
                "risk",
                "LOW"
            )

        }