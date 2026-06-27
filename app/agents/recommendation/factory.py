from app.agents.recommendation.azure_openai_agent import (
    AzureOpenAIRecommendationAgent
)


class RecommendationAgentFactory:

    @staticmethod
    def create():

        return AzureOpenAIRecommendationAgent()
