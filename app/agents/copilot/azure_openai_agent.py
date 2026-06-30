from app.agents.common.azure_client import (
    AzureOpenAIClient
)

from app.agents.common.json_parser import (
    JsonParser
)

from app.core.config import settings


class AzureOpenAIExceptionAgent:

    def analyze(
        self,
        reconciliation,
        payment_transaction,
        bank_transaction
    ):

        prompt = f"""
You are an enterprise reconciliation analyst.

Analyze the exception.

Reconciliation:
{reconciliation}

Payment:
{payment_transaction}

Bank:
{bank_transaction}

Return ONLY valid JSON.

{{
    "root_cause":"",
    "confidence":0,
    "business_explanation":"",
    "operational_domain":""
}}
"""

        response = AzureOpenAIClient.complete(
            prompt
        )

        return JsonParser.parse(
            response
        )