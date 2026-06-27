import io

import pandas as pd

from fastapi import UploadFile


class PaymentParser:

    REQUIRED_COLUMNS = [

        "transaction_reference",
        "end_to_end_id",
        "sender_account",
        "receiver_account",
        "sender_name",
        "receiver_name",
        "amount",
        "currency",
        "payment_date",
        "settlement_date"

    ]

    async def parse(
        self,
        file: UploadFile
    ):

        contents = await file.read()

        await file.seek(0)

        extension = file.filename.split(".")[-1].lower()

        if extension == "csv":

            dataframe = pd.read_csv(
                io.BytesIO(contents)
            )

        elif extension in [

            "xlsx",
            "xls"

        ]:

            dataframe = pd.read_excel(
                io.BytesIO(contents)
            )

        else:

            raise Exception(
                "Unsupported file format."
            )

        missing = [

            column

            for column in self.REQUIRED_COLUMNS

            if column not in dataframe.columns

        ]

        if missing:

            raise Exception(
                f"Missing columns: {missing}"
            )

        return dataframe
