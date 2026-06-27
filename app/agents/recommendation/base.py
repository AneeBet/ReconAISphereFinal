from abc import ABC
from abc import abstractmethod


class RecommendationAgent(ABC):

    @abstractmethod
    def recommend(
        self,
        investigation_case
    ):
        pass
