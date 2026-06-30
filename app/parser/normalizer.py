import io

import pandas as pd


CANONICAL_FIELDS = [
    "transaction_reference",
    "end_to_end_id",
    "sender_account",
    "receiver_account",
    "sender_name",
    "receiver_name",
    "amount",
    "currency",
    "payment_date",
    "settlement_date",
]

# Deterministic banking-grade alias map: source header -> canonical field.
ALIASES = {
    "txn_ref": "transaction_reference",
    "transaction_id": "transaction_reference",
    "reference": "transaction_reference",
    "uetr": "end_to_end_id",
    "e2e_id": "end_to_end_id",
    "end_to_end": "end_to_end_id",
    "debtor_account": "sender_account",
    "creditor_account": "receiver_account",
    "debtor_name": "sender_name",
    "creditor_name": "receiver_name",
    "value": "amount",
    "ccy": "currency",
    "value_date": "payment_date",
    "exec_date": "payment_date",
    "settle_date": "settlement_date",
}


class Normalizer:
    """Maps arbitrary bank/payment file headers to a canonical schema."""

    @staticmethod
    def read(contents, filename):
        ext = filename.split(".")[-1].lower()
        if ext == "csv":
            return pd.read_csv(io.BytesIO(contents))
        if ext in ("xlsx", "xls"):
            return pd.read_excel(io.BytesIO(contents))
        raise ValueError("Unsupported file format.")

    @staticmethod
    def normalize(df):
        rename = {}
        for col in df.columns:
            key = str(col).strip().lower()
            if key in ALIASES:
                rename[col] = ALIASES[key]
        df = df.rename(columns=rename)
        return df

    @staticmethod
    def rows(contents, filename):
        df = Normalizer.normalize(Normalizer.read(contents, filename))
        return df.to_dict(orient="records")