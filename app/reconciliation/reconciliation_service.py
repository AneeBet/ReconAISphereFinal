from app.reconciliation.matching_engine import (
    MatchingEngine
)


class EnterpriseReconciliationService:

    EXACT_MATCH_SCORE = 95

    AI_REVIEW_SCORE = 60

    def __init__(
        self
    ):

        self.engine = MatchingEngine()

    def reconcile(
        self,
        payment_transactions,
        bank_transactions
    ):

        results = []

        for payment in payment_transactions:

            best_match = None

            best_score = -1

            for bank in bank_transactions:

                score = self.engine.match(
                    payment,
                    bank
                )

                if score > best_score:

                    best_score = score

                    best_match = bank

            if best_score >= self.EXACT_MATCH_SCORE:

                status = "MATCHED"

                ai_required = False

            elif best_score >= self.AI_REVIEW_SCORE:

                status = "POTENTIAL_MATCH"

                ai_required = True

            else:

                status = "EXCEPTION"

                ai_required = False

            results.append(

                {

                    "payment": payment,

                    "bank": best_match,

                    "score": best_score,

                    "status": status,

                    "ai_required": ai_required

                }

            )

        return results