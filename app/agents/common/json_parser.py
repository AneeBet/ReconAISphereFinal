import json


class JsonParser:

    @staticmethod
    def parse(
        text: str
    ):

        try:

            return json.loads(text)

        except Exception:

            return {

                "raw_response": text

            }
