from app.agents.matching.azure_openai_agent import (

    AzureOpenAIMatchingAgent

)


class MatchingAgentFactory:

    @staticmethod
    def create():

        return AzureOpenAIMatchingAgent()
