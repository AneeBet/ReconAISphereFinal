from app.reconciliation.rule_engine import (
    RuleEngine
)


class MatchingEngine:

    def __init__(
        self
    ):

        self.rules = RuleEngine()

    def match(
        self,
        payment,
        bank
    ):

        score = 0

        if self.rules.exact_match(
            payment,
            bank
        ):
            score += 40

        if self.rules.end_to_end_match(
            payment,
            bank
        ):
            score += 25

        if self.rules.amount_match(
            payment,
            bank
        ):
            score += 15

        if self.rules.currency_match(
            payment,
            bank
        ):
            score += 10

        if self.rules.date_match(
            payment,
            bank
        ):
            score += 10

        return score
