import json
import re


class JsonParser:

    @staticmethod
    def parse(
        text: str
    ):

        if text is None:
            return {}

        cleaned = text.strip()

        # Strip ```json ... ``` or ``` ... ``` fences
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```[a-zA-Z]*", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Fallback: extract first {...} block
        match = re.search(r"\{.*\}", cleaned, re.DOTALL)

        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        return {
            "raw_response": text
        }