from app.agents.exception.azure_openai_agent import (
    AzureOpenAIExceptionAgent
)


class ExceptionAnalysisAgentFactory:

    @staticmethod
    def create():

        return AzureOpenAIExceptionAgent()
