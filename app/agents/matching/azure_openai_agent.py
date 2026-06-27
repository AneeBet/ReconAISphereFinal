from app.agents.common.azure_client import (
    AzureOpenAIClient
)

from app.agents.common.json_parser import (
    JsonParser
)

from app.core.config import (
    settings
)


class AzureOpenAIMatchingAgent:

    def validate(

        self,

        payment,

        bank,

        score

    ):

        client = AzureOpenAIClient.client()

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

        response = client.responses.create(

            model=settings.AZURE_OPENAI_DEPLOYMENT,

            input=prompt

        )

        result = JsonParser.parse(

            response.output_text

        )

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

                ""

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