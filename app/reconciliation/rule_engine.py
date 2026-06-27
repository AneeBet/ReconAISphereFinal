from decimal import Decimal


class RuleEngine:

    AMOUNT_TOLERANCE = Decimal("0.01")

    DATE_TOLERANCE_DAYS = 1

    def exact_match(
        self,
        payment,
        bank
    ):

        return (

            payment.transaction_reference ==
            bank.transaction_reference

        )

    def end_to_end_match(
        self,
        payment,
        bank
    ):

        return (

            payment.end_to_end_id ==
            bank.end_to_end_id

        )

    def amount_match(
        self,
        payment,
        bank
    ):

        difference = abs(

            Decimal(payment.amount)

            -

            Decimal(bank.amount)

        )

        return (

            difference <=
            self.AMOUNT_TOLERANCE

        )

    def currency_match(
        self,
        payment,
        bank
    ):

        return (

            payment.currency ==
            bank.currency

        )

    def date_match(
        self,
        payment,
        bank
    ):

        days = abs(

            (

                payment.payment_date

                -

                bank.payment_date

            ).days

        )

        return (

            days <=
            self.DATE_TOLERANCE_DAYS

        )
