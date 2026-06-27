from app.agents.copilot.azure_openai_agent import (
    AzureOpenAICopilotAgent
)


class CopilotAgentFactory:

    @staticmethod
    def create():

        return AzureOpenAICopilotAgent()
